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

        // Permission Dropdown (if not current user)
        if (user.id !== currentUser.id) {
            const permDropdown = document.createElement("select");
            permDropdown.className = "permission-select";
            permDropdown.innerHTML = `
                <option value="REGULAR" ${user.permission_level === "REGULAR" ? "selected" : ""}>Regular</option>
                <option value="MANAGER" ${user.permission_level === "MANAGER" ? "selected" : ""}>Manager</option>
                <option value="ADMIN" ${user.permission_level === "ADMIN" ? "selected" : ""}>Admin</option>
            `;
            permDropdown.addEventListener("change", (e) => {
                if (e.target.value !== user.permission_level) {
                    changePermissionDirect(user.id, user.permission_level, e.target.value);
                }
            });
            const permCell = tr.querySelector(`#perm-${user.id}`);
            permCell.innerHTML = "";
            permCell.appendChild(permDropdown);
        }

        // Deactivate Button
        if (user.is_active && user.id !== currentUser.id) {
            const btnDeactivate = document.createElement("button");
            btnDeactivate.className = "btn btn-secondary btn-icon";
            btnDeactivate.textContent = "Deactivate";
            btnDeactivate.style.color = "var(--danger)";
            btnDeactivate.addEventListener("click", () => deactivateUser(user.id));
            actionsCell.appendChild(btnDeactivate);
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
    document.getElementById("admin-users").textContent = `${adminUsers} + ${managerUsers} managers`;
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

async function changePermissionDirect(userId, currentPermission, newPermission) {
    if (!confirm(`Change permission to ${newPermission}?`)) return;

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

async function changePermission(userId, currentPermission) {
    // Cycle through: REGULAR -> MANAGER -> ADMIN -> REGULAR
    let newPermission = "MANAGER";
    if (currentPermission === "REGULAR") newPermission = "MANAGER";
    else if (currentPermission === "MANAGER") newPermission = "ADMIN";
    else if (currentPermission === "ADMIN") newPermission = "REGULAR";

    if (!confirm(`Change permission to ${newPermission}?`)) return;

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
