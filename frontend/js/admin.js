const API_URL = "http://127.0.0.1:8000";
let authToken = localStorage.getItem("authToken");
let currentUser = null;
let isDarkTheme = true;

// Theme Management
function toggleTheme() {
    isDarkTheme = !isDarkTheme;
    document.body.classList.toggle("dark-theme", isDarkTheme);
    const btn = document.getElementById("btn-toggle-theme");
    if (btn) btn.textContent = isDarkTheme ? "☀️" : "🌙";
    try { localStorage.setItem("theme", isDarkTheme ? "dark" : "light"); } catch (e) { }
}

function initTheme() {
    try {
        const theme = localStorage.getItem("theme");
        if (theme === "light") {
            isDarkTheme = false;
            document.body.classList.remove("dark-theme");
        } else {
            isDarkTheme = true;
            document.body.classList.add("dark-theme");
        }
    } catch (e) {
        document.body.classList.add("dark-theme");
        isDarkTheme = true;
    }
    const btn = document.getElementById("btn-toggle-theme");
    if (btn) btn.textContent = isDarkTheme ? "☀️" : "🌙";
}

// API Helper
async function apiFetch(path, opts = {}) {
    const headers = opts.headers || {};
    if (!headers["Content-Type"]) headers["Content-Type"] = "application/json";
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

    try {
        const res = await fetch(`${API_URL}${path}`, { ...opts, headers });
        const text = await res.text();
        const data = text ? JSON.parse(text) : null;
        if (!res.ok) {
            const err = data && data.detail ? data.detail : data || res.statusText;
            throw new Error(typeof err === "string" ? err : JSON.stringify(err));
        }
        return data;
    } catch (e) {
        throw e;
    }
}

function showMessage(id, message, isError = false) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = message;
    el.classList.toggle("error", !!isError);
    if (message) {
        setTimeout(() => {
            el.textContent = "";
        }, 5000);
    }
}

// Auth Check
async function checkAuth() {
    if (!authToken) {
        showAuthRequired();
        return false;
    }

    try {
        const user = await apiFetch("/users/me");
        currentUser = user;

        if (user.permission_level !== "ADMIN") {
            showAuthRequired();
            return false;
        }

        document.getElementById("user-display").textContent = user.username;
        document.getElementById("btn-logout").style.display = "inline-block";
        document.getElementById("auth-required").style.display = "none";
        document.getElementById("admin-panel").style.display = "flex";

        return true;
    } catch (e) {
        showAuthRequired();
        return false;
    }
}

function showAuthRequired() {
    document.getElementById("auth-required").style.display = "flex";
    document.getElementById("admin-panel").style.display = "none";
}

function logout() {
    authToken = null;
    localStorage.removeItem("authToken");
    window.location.href = "index.html";
}

// User Management
async function loadUsers() {
    showMessage("users-message", "");
    try {
        const users = await apiFetch("/users/");
        renderUsersTable(users);
        updateStats(users);
    } catch (e) {
        showMessage("users-message", `Failed to load users: ${e.message}`, true);
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById("users-table-body");
    tbody.innerHTML = "";

    if (!users || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-secondary);">No users found</td></tr>';
        return;
    }

    users.forEach(user => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
      <td class="user-id">#${user.id}</td>
      <td><strong>${user.username}</strong></td>
      <td id="perm-${user.id}"><span class="permission-badge ${user.permission_level.toLowerCase()}">${user.permission_level}</span></td>
      <td><span class="status-badge ${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
      <td>${new Date(user.created_at).toLocaleDateString()}</td>
      <td class="action-buttons"></td>
    `;

        const actionsCell = tr.querySelector(".action-buttons");

        // Permission Cycle Button (if not current user)
        if (user.id !== currentUser.id) {
            const btnTogglePerm = document.createElement("button");
            btnTogglePerm.className = "btn btn-secondary btn-icon";
            
            // Cycle through: REGULAR -> MANAGER -> ADMIN -> REGULAR
            let nextPerm = "MANAGER";
            let arrow = "↑ Manager";
            if (user.permission_level === "REGULAR") {
                nextPerm = "MANAGER";
                arrow = "↑ Manager";
            } else if (user.permission_level === "MANAGER") {
                nextPerm = "ADMIN";
                arrow = "↑ Admin";
            } else if (user.permission_level === "ADMIN") {
                nextPerm = "REGULAR";
                arrow = "↓ Regular";
            }
            
            btnTogglePerm.textContent = arrow;
            btnTogglePerm.addEventListener("click", () => changePermission(user.id, user.permission_level));
            actionsCell.appendChild(btnTogglePerm);
        }

        // Deactivate or Activate Button
        if (user.id !== currentUser.id) {
            if (user.is_active) {
                const btnDeactivate = document.createElement("button");
                btnDeactivate.className = "btn btn-secondary btn-icon";
                btnDeactivate.textContent = "Deactivate";
                btnDeactivate.style.color = "var(--danger)";
                btnDeactivate.addEventListener("click", () => deactivateUser(user.id));
                actionsCell.appendChild(btnDeactivate);
            } else {
                const btnActivate = document.createElement("button");
                btnActivate.className = "btn btn-secondary btn-icon";
                btnActivate.textContent = "Activate";
                btnActivate.style.color = "var(--success)";
                btnActivate.addEventListener("click", () => activateUser(user.id));
                actionsCell.appendChild(btnActivate);
            }
        }

        tbody.appendChild(tr);
    });
}

function updateStats(users) {
    const totalUsers = users.length;
    const adminUsers = users.filter(u => u.permission_level === "ADMIN").length;
    const managerUsers = users.filter(u => u.permission_level === "MANAGER").length;
    const activeUsers = users.filter(u => u.is_active).length;

    document.getElementById("total-users").textContent = totalUsers;
    document.getElementById("admin-users").textContent = adminUsers;
    document.getElementById("manager-users").textContent = managerUsers;
    document.getElementById("active-users").textContent = activeUsers;
}

async function createUser() {
    const username = document.getElementById("new-username").value.trim();
    const password = document.getElementById("new-password").value;
    const permission_level = document.getElementById("new-permission").value;

    if (!username || !password) {
        showMessage("users-message", "Please fill all fields", true);
        return;
    }

    if (password.length < 6) {
        showMessage("users-message", "Password must be at least 6 characters", true);
        return;
    }

    showMessage("users-message", "Creating user...");
    try {
        await apiFetch("/users/", {
            method: "POST",
            body: JSON.stringify({ username, password, permission_level })
        });

        document.getElementById("create-user-form").reset();
        await loadUsers();
        showMessage("users-message", "User created successfully");
    } catch (e) {
        showMessage("users-message", `Failed to create user: ${e.message}`, true);
    }
}

async function changePermission(userId, currentPermission) {
    // Cycle through: REGULAR -> MANAGER -> ADMIN -> REGULAR
    let newPermission = "MANAGER";
    if (currentPermission === "REGULAR") newPermission = "MANAGER";
    else if (currentPermission === "MANAGER") newPermission = "ADMIN";
    else if (currentPermission === "ADMIN") newPermission = "REGULAR";


    showMessage("users-message", "Updating permission...");
    try {
        await apiFetch(`/users/${userId}`, {
            method: "PATCH",
            body: JSON.stringify({ permission_level: newPermission })
        });

        await loadUsers();
        showMessage("users-message", "Permission updated successfully");
    } catch (e) {
        showMessage("users-message", `Failed to update permission: ${e.message}`, true);
    }
}

async function deactivateUser(userId) {
    if (!confirm("Deactivate this user?")) return;

    showMessage("users-message", "Deactivating user...");
    try {
        await apiFetch(`/users/${userId}`, { method: "DELETE" });
        await loadUsers();
        showMessage("users-message", "User deactivated successfully");
    } catch (e) {
        showMessage("users-message", `Failed to deactivate user: ${e.message}`, true);
    }
}

async function activateUser(userId) {
    if (!confirm("Activate this user?")) return;

    showMessage("users-message", "Activating user...");
    try {
        await apiFetch(`/users/${userId}`, {
            method: "PATCH",
            body: JSON.stringify({ is_active: true })
        });
        await loadUsers();
        showMessage("users-message", "User activated successfully");
    } catch (e) {
        showMessage("users-message", `Failed to activate user: ${e.message}`, true);
    }
}

// Event Listeners
document.addEventListener("DOMContentLoaded", async () => {
    initTheme();
    const themeBtn = document.getElementById("btn-toggle-theme");
    if (themeBtn) themeBtn.addEventListener("click", toggleTheme);

    document.getElementById("btn-logout")?.addEventListener("click", logout);
    document.getElementById("btn-refresh-users")?.addEventListener("click", loadUsers);
    document.getElementById("btn-create-user")?.addEventListener("click", createUser);
    document.getElementById("create-user-form")?.addEventListener("submit", (e) => e.preventDefault());

    const isAuthorized = await checkAuth();
    if (isAuthorized) {
        await loadUsers();
    }
});

// ==========================================
// AUDIT LOGS
// ==========================================

let currentLogsPage = 1;
let logsFilters = {
    action: '',
    entity_type: '',
    date_from: '',
    date_to: ''
};

async function loadAuditLogs(page = 1) {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
        let url = `${API_BASE_URL}/audit-logs/?page=${page}&page_size=50`;
        
        // Apply filters
        if (logsFilters.action) url += `&action=${logsFilters.action}`;
        if (logsFilters.entity_type) url += `&entity_type=${logsFilters.entity_type}`;
        if (logsFilters.date_from) url += `&date_from=${logsFilters.date_from}T00:00:00`;
        if (logsFilters.date_to) url += `&date_to=${logsFilters.date_to}T23:59:59`;

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load audit logs');
        }

        const data = await response.json();
        displayAuditLogs(data.items || []);
        updateLogsPagination(data.page || 1, data.total_pages || 1);
        currentLogsPage = page;

        showMessage('logs-message', 'Audit logs loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading audit logs:', error);
        showMessage('logs-message', 'Failed to load audit logs', 'error');
    }
}

function displayAuditLogs(logs) {
    const tbody = document.getElementById('audit-logs-table-body');
    if (!tbody) return;

    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No audit logs found</td></tr>';
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const timestamp = new Date(log.created_at).toLocaleString();
        return `
            <tr>
                <td>${timestamp}</td>
                <td>${log.username || 'SYSTEM'}</td>
                <td><span class="badge badge-${getActionBadgeClass(log.action)}">${log.action}</span></td>
                <td>${log.entity_type}</td>
                <td>${log.entity_id || '-'}</td>
                <td>${log.description || '-'}</td>
                <td>${log.ip_address || '-'}</td>
            </tr>
        `;
    }).join('');
}

function getActionBadgeClass(action) {
    const actionClasses = {
        'CREATE': 'success',
        'UPDATE': 'info',
        'DELETE': 'danger',
        'LOGIN_SUCCESS': 'success',
        'LOGIN_FAILED': 'danger',
        'LOGOUT': 'secondary',
        'CHECK_IN': 'info',
        'CHECK_OUT': 'info',
        'CANCEL': 'warning',
        'PROCESS': 'success',
        'REFUND': 'warning'
    };
    return actionClasses[action] || 'secondary';
}

function updateLogsPagination(currentPage, totalPages) {
    const paginationDiv = document.getElementById('logs-pagination');
    if (!paginationDiv) return;

    let html = '';
    
    // Previous button
    html += `<button onclick="loadAuditLogs(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>&laquo; Previous</button>`;
    
    // Page info
    html += `<span class="page-info">Page ${currentPage} of ${totalPages}</span>`;
    
    // Next button
    html += `<button onclick="loadAuditLogs(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next &raquo;</button>`;
    
    paginationDiv.innerHTML = html;
}

function applyLogFilters() {
    logsFilters.action = document.getElementById('log-action-filter')?.value || '';
    logsFilters.entity_type = document.getElementById('log-entity-filter')?.value || '';
    logsFilters.date_from = document.getElementById('log-date-from')?.value || '';
    logsFilters.date_to = document.getElementById('log-date-to')?.value || '';
    
    loadAuditLogs(1);
}

// Event listeners for audit logs
document.addEventListener('DOMContentLoaded', function() {
    const btnRefreshLogs = document.getElementById('btn-refresh-logs');
    const btnApplyFilters = document.getElementById('btn-apply-log-filters');
    
    if (btnRefreshLogs) {
        btnRefreshLogs.addEventListener('click', () => loadAuditLogs(currentLogsPage));
    }
    
    if (btnApplyFilters) {
        btnApplyFilters.addEventListener('click', applyLogFilters);
    }
    
    // Load audit logs if admin panel is visible
    if (document.getElementById('admin-panel').style.display !== 'none') {
        loadAuditLogs();
    }
});
