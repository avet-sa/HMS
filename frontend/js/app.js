const API_URL = "http://127.0.0.1:8000";
let authToken = null;
let currentUser = null;
// Theme: default to dark
let isDarkTheme = true;

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
    // ignore localStorage errors
    document.body.classList.add("dark-theme");
    isDarkTheme = true;
  }
  const btn = document.getElementById("btn-toggle-theme");
  if (btn) btn.textContent = isDarkTheme ? "☀️" : "🌙";
}

// Centralized API fetch helper
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
}

function showAuthModal() {
  document.getElementById("auth-modal").classList.add("modal-active");
  document.getElementById("dashboard").style.display = "none";
}

function hideAuthModal() {
  document.getElementById("auth-modal").classList.remove("modal-active");
  document.getElementById("dashboard").style.display = "flex";
}

function updateUserDisplay(username) {
  document.getElementById("user-display").textContent = username;
  document.getElementById("btn-logout").style.display = "inline-block";
}

// Auth Functions
async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  if (!username || !password) {
    showMessage("auth-message", "Please enter username and password", true);
    return;
  }

  showMessage("auth-message", "Signing in...");
  try {
    // OAuth2 token endpoint expects form-encoded body
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    params.append('grant_type', 'password');

    const res = await fetch(`${API_URL}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params.toString()
    });
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(txt || res.statusText);
    }
    const data = await res.json();
    authToken = data.access_token;

    // Store token in localStorage
    try { localStorage.setItem("authToken", authToken); } catch (e) { }

    // Fetch user info to check permission level
    const userInfo = await apiFetch("/users/me");
    currentUser = userInfo;

    updateUserDisplay(username);

    // Show admin link if user is admin
    if (userInfo.permission_level === "ADMIN") {
      document.getElementById("admin-link").style.display = "inline-flex";
    }

    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    hideAuthModal();
    showMessage("auth-message", "");
    // Load data
    setTimeout(() => { listRooms(); listGuests(); listBookings(); listRoomTypes(); listPayments(); }, 200);
  } catch (e) {
    showMessage("auth-message", `Sign in failed: ${e.message}`, true);
  }
}

async function register() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  if (!username || !password) {
    showMessage("auth-message", "Please enter username and password", true);
    return;
  }

  if (password.length < 6) {
    showMessage("auth-message", "Password must be at least 6 characters", true);
    return;
  }

  showMessage("auth-message", "Creating account...");
  try {
    await apiFetch(`/auth/register`, {
      method: "POST",
      body: JSON.stringify({ username, password })
    });
    showMessage("auth-message", "Account created! Now sign in.");
    document.getElementById("username").value = username;
    document.getElementById("password").value = "";
  } catch (e) {
    showMessage("auth-message", `Registration failed: ${e.message}`, true);
  }
}

function logout() {
  authToken = null;
  currentUser = null;
  try { localStorage.removeItem("authToken"); } catch (e) { }
  document.getElementById("user-display").textContent = "Guest";
  document.getElementById("btn-logout").style.display = "none";
  document.getElementById("admin-link").style.display = "none";
  showAuthModal();
}

// Room Functions
function renderRoomItem(r) {
  const li = document.createElement("li");
  const text = document.createElement("span");
  text.innerHTML = `<span class="item-id">#${r.id}</span>${r.number} — $${r.price_per_night}/night`;
  li.appendChild(text);

  const btnDelete = document.createElement("button");
  btnDelete.className = "btn btn-secondary btn-sm";
  btnDelete.textContent = "Delete";
  btnDelete.addEventListener("click", async () => {
    if (confirm("Delete this room?")) {
      try {
        await apiFetch(`/rooms/${r.id}`, { method: "DELETE" });
        listRooms();
      } catch (e) {
        showMessage("rooms-message", `Delete failed: ${e.message}`, true);
      }
    }
  });

  li.appendChild(btnDelete);
  return li;
}

async function listRooms() {
  showMessage("rooms-message", "");
  try {
    const rooms = await apiFetch(`/rooms/`);
    const ul = document.getElementById("room-list");
    ul.innerHTML = "";
    if (rooms && rooms.length > 0) {
      rooms.forEach(r => ul.appendChild(renderRoomItem(r)));
    } else {
      ul.innerHTML = '<li style="text-align: center; color: #7f8c8d;">No rooms yet</li>';
    }
  } catch (e) {
    showMessage("rooms-message", `Failed to load rooms: ${e.message}`, true);
  }
}

// Room Types
async function listRoomTypes() {
  try {
    const types = await apiFetch('/room-types/');
    const sel = document.getElementById('room-type');
    if (!sel) return;
    sel.innerHTML = '<option value="">Select Type</option>';
    types.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = `${t.name} — $${t.base_price}`;
      sel.appendChild(opt);
    });
  } catch (e) {
    showMessage('rooms-message', `Failed to load room types: ${e.message}`, true);
  }
}

async function createRoom() {
  const number = document.getElementById("room-number").value.trim();
  const room_type_id = parseInt(document.getElementById("room-type").value);
  const price = parseFloat(document.getElementById("room-price").value);
  const square_meters = parseInt(document.getElementById("room-sqm").value);
  const floor = parseInt(document.getElementById("room-floor").value);

  if (!number || !room_type_id || Number.isNaN(price) || Number.isNaN(square_meters) || Number.isNaN(floor)) {
    showMessage("rooms-message", "Please fill all room fields with valid values", true);
    return;
  }

  showMessage("rooms-message", "Adding room...");
  try {
    await apiFetch(`/rooms/`, {
      method: "POST",
      body: JSON.stringify({ number, room_type_id, price_per_night: price, square_meters, floor })
    });
    document.getElementById("room-form").reset();
    await listRooms();
    showMessage("rooms-message", "Room added successfully");
  } catch (e) {
    showMessage("rooms-message", `Failed to add room: ${e.message}`, true);
  }
}

// Payments
async function createPayment() {
  const booking_id = parseInt(document.getElementById('payment-booking-id').value);
  const amount = parseFloat(document.getElementById('payment-amount').value);
  const currency = document.getElementById('payment-currency').value || 'USD';
  const method = document.getElementById('payment-method').value || 'card';

  if (!booking_id || Number.isNaN(amount)) {
    showMessage('payments-message', 'Please provide booking id and amount', true);
    return;
  }

  showMessage('payments-message', 'Creating payment...');
  try {
    const p = await apiFetch('/payments/create', {
      method: 'POST',
      body: JSON.stringify({ booking_id, amount, currency, method }),
    });
    showMessage('payments-message', 'Payment created');
    // Append created payment to list if possible
    try {
      const ul = document.getElementById('payment-list');
      if (ul) {
        const li = document.createElement('li');
        li.textContent = `#${p.id} Booking:${p.booking_id} ${p.amount} ${p.currency} — ${p.status}`;
        // If the placeholder message exists, clear it
        if (ul.children.length === 1 && ul.children[0].textContent.includes('not available')) ul.innerHTML = '';
        ul.prepend(li);
      }
    } catch (err) {
      // ignore UI append errors
    }
  } catch (e) {
    showMessage('payments-message', `Failed to create payment: ${e.message}`, true);
  }
}

// Reports
async function fetchOccupancyReport() {
  const start = document.getElementById('report-start').value;
  const end = document.getElementById('report-end').value;
  if (!start || !end) { showMessage('reports-message', 'Select start and end dates', true); return; }
  
  const out = document.getElementById('report-output');
  out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">Loading occupancy report...</div>';
  showMessage('reports-message', 'Fetching occupancy...');
  
  try {
    const data = await apiFetch(`/occupancy?start_date=${start}&end_date=${end}`);
    if (!data.daily || data.daily.length === 0) {
      out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">No occupancy data available for selected date range.</div>';
      showMessage('reports-message', 'No data found', true);
      return;
    }
    renderOccupancyReport(data);
    showMessage('reports-message', '');
  } catch (e) {
    out.innerHTML = '';
    showMessage('reports-message', `Failed: ${e.message}`, true);
  }
}

async function fetchRevenueReport() {
  const start = document.getElementById('report-start').value;
  const end = document.getElementById('report-end').value;
  if (!start || !end) { showMessage('reports-message', 'Select start and end dates', true); return; }
  
  const out = document.getElementById('report-output');
  out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">Loading revenue report...</div>';
  showMessage('reports-message', 'Fetching revenue...');
  
  try {
    const data = await apiFetch(`/revenue?start_date=${start}&end_date=${end}`);
    if (!data.daily || data.daily.length === 0) {
      out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">No revenue data available for selected date range.</div>';
      showMessage('reports-message', 'No data found', true);
      return;
    }
    renderRevenueReport(data);
    showMessage('reports-message', '');
  } catch (e) {
    out.innerHTML = '';
    showMessage('reports-message', `Failed: ${e.message}`, true);
  }
}

async function fetchTrendsReport() {
  const start = document.getElementById('report-start').value;
  const end = document.getElementById('report-end').value;
  if (!start || !end) { showMessage('reports-message', 'Select start and end dates', true); return; }
  
  const out = document.getElementById('report-output');
  out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">Loading trends report...</div>';
  showMessage('reports-message', 'Fetching trends...');
  
  try {
    const data = await apiFetch(`/trends?start_date=${start}&end_date=${end}`);
    if (data.total_bookings === 0) {
      out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">No booking data available for selected date range.</div>';
      showMessage('reports-message', 'No data found', true);
      return;
    }
    renderTrendsReport(data);
    showMessage('reports-message', '');
  } catch (e) {
    out.innerHTML = '';
    showMessage('reports-message', `Failed: ${e.message}`, true);
  }
}

// Report rendering helpers
function safeText(s) {
  return String(s == null ? "" : s);
}

function fmtDate(d) {
  // Expect ISO date string (YYYY-MM-DD) or Date object
  if (typeof d === 'string') {
    // If already ISO format, return as-is
    if (/^\d{4}-\d{2}-\d{2}$/.test(d)) return d;
  }
  try {
    const dt = typeof d === 'string' ? new Date(d + 'T00:00:00Z') : d;
    if (isNaN(dt)) return safeText(d);
    return dt.toISOString().slice(0, 10);
  } catch (e) {
    return safeText(d);
  }
}

function fmtCurrency(n, cur = 'USD') {
  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: cur }).format(Number(n));
  } catch (e) {
    return `${n} ${cur}`;
  }
}

function fmtPercent(n) {
  try {
    return `${Number(n).toFixed(2)}%`;
  } catch (e) {
    return safeText(n);
  }
}

// Reusable function to create stat cards
function createStatCard(label, value) {
  const card = document.createElement('div');
  card.style.cssText = 'display: flex; flex-direction: column; gap: 0.5rem;';
  const lbl = document.createElement('div');
  lbl.style.cssText = 'font-weight: 600; color: var(--text-secondary); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;';
  lbl.textContent = label;
  const val = document.createElement('div');
  val.style.cssText = 'font-size: 1.75rem; font-weight: 700; color: var(--accent);';
  val.textContent = value;
  card.appendChild(lbl);
  card.appendChild(val);
  return card;
}

function renderOccupancyReport(data) {
  clearReportExports();
  const out = document.getElementById('report-output');
  out.innerHTML = '';
  const header = document.createElement('div');
  header.className = 'report-header';
  header.innerHTML = `<strong>Occupancy</strong> — ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}`;
  out.appendChild(header);

  // Chart section
  const chartSection = document.createElement('div');
  chartSection.id = 'report-chart-container';
  const canvas = document.createElement('canvas');
  canvas.id = 'report-chart';
  chartSection.appendChild(canvas);
  out.appendChild(chartSection);

  // Summary section
  const summary = document.createElement('div');
  summary.className = 'report-summary';
  summary.appendChild(createStatCard('Average Occupancy', fmtPercent(data.average_occupancy)));
  summary.appendChild(createStatCard('Peak Occupancy', fmtPercent(data.max_occupancy)));
  summary.appendChild(createStatCard('Min Occupancy', fmtPercent(data.min_occupancy)));
  summary.appendChild(createStatCard('Total Room-Nights', safeText(data.total_room_nights)));
  out.appendChild(summary);
  
  // Render the actual chart
  setTimeout(() => renderOccupancyChart(data), 0);

  // Export buttons
  showExportButtons('occupancy', data);
}

function renderRevenueReport(data) {
  clearReportExports();
  const out = document.getElementById('report-output');
  out.innerHTML = '';
  const header = document.createElement('div');
  header.className = 'report-header';
  header.innerHTML = `<strong>Revenue</strong> — ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}`;
  out.appendChild(header);

  // Chart section
  const chartSection = document.createElement('div');
  chartSection.id = 'report-chart-container';
  const canvas = document.createElement('canvas');
  canvas.id = 'report-chart';
  chartSection.appendChild(canvas);
  out.appendChild(chartSection);

  // Summary section
  const summary = document.createElement('div');
  summary.className = 'report-summary';
  summary.appendChild(createStatCard('Total Revenue', fmtCurrency(data.total_revenue)));
  summary.appendChild(createStatCard('Avg Daily Revenue', fmtCurrency(data.average_daily_revenue)));
  summary.appendChild(createStatCard('Max Daily Revenue', fmtCurrency(data.max_daily_revenue)));
  summary.appendChild(createStatCard('Min Daily Revenue', fmtCurrency(data.min_daily_revenue)));
  summary.appendChild(createStatCard('Paid Bookings', safeText(data.total_paid_bookings)));
  
  // Add room type breakdown
  if (data.room_type_breakdown && data.room_type_breakdown.length > 0) {
    const topRoomType = data.room_type_breakdown.reduce((max, rt) => 
      Number(rt.revenue) > Number(max.revenue) ? rt : max, data.room_type_breakdown[0]);
    summary.appendChild(createStatCard('Top Room Type', `${topRoomType.room_type} (${fmtCurrency(topRoomType.revenue)})`));
  }
  
  out.appendChild(summary);
  
  // Render the actual chart
  setTimeout(() => renderRevenueChart(data), 0);

  // Export buttons
  showExportButtons('revenue', data);
}

function renderTrendsReport(data) {
  clearReportExports();
  const out = document.getElementById('report-output');
  out.innerHTML = '';
  const header = document.createElement('div');
  header.className = 'report-header';
  header.innerHTML = `<strong>Booking Trends</strong> — ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}`;
  out.appendChild(header);

  // Chart section
  const chartSection = document.createElement('div');
  chartSection.id = 'report-chart-container';
  const canvas = document.createElement('canvas');
  canvas.id = 'report-chart';
  chartSection.appendChild(canvas);
  out.appendChild(chartSection);

  const grid = document.createElement('div');
  grid.className = 'report-summary';
  grid.appendChild(createStatCard('Total Bookings', data.total_bookings));
  grid.appendChild(createStatCard('Confirmed', data.confirmed_bookings));
  grid.appendChild(createStatCard('Cancellations', data.cancellations));
  grid.appendChild(createStatCard('No-shows', data.no_shows));
  grid.appendChild(createStatCard('Cancel Rate', fmtPercent(data.cancellation_rate)));
  grid.appendChild(createStatCard('No-show Rate', fmtPercent(data.no_show_rate)));
  grid.appendChild(createStatCard('Avg Lead Time', `${Math.round(data.avg_lead_time_days) || 0} days`));
  grid.appendChild(createStatCard('Avg Stay', `${Math.round(data.avg_length_of_stay_nights) || 0} nights`));
  out.appendChild(grid);

  // Chart - render after DOM is ready
  setTimeout(() => renderTrendsChart(data), 0);

  // Export buttons
  showExportButtons('trends', data);
}

// Chart.js rendering
let currentReportChart = null;

function renderOccupancyChart(data) {
  const container = document.getElementById('report-chart-container');
  const canvas = document.getElementById('report-chart');
  if (!container || !canvas) return;
  
  let labels = (data.daily || []).map(d => fmtDate(d.date));
  let rates = (data.daily || []).map(d => Number(d.occupancy_rate) || 0);
  
  container.style.display = 'block';
  
  if (currentReportChart) currentReportChart.destroy();
  
  // Aggregate data for large date ranges
  const dayCount = labels.length;
  if (dayCount > 90) {
    const aggregateSize = dayCount > 180 ? 30 : 7; // Monthly for 180+ days, weekly for 90+ days
    const newLabels = [];
    const newRates = [];
    const monthFormatter = new Intl.DateTimeFormat('en', { month: 'short', year: '2-digit' });
    
    for (let i = 0; i < labels.length; i += aggregateSize) {
      const chunk = rates.slice(i, i + aggregateSize);
      const avgRate = chunk.length > 0 ? chunk.reduce((a,b) => a+b, 0) / chunk.length : 0;
      
      let label;
      if (dayCount > 180) {
        // Monthly: use month name
        const date = new Date(labels[i]);
        label = monthFormatter.format(date);
      } else {
        // Weekly: use date range
        label = labels[i] + ' to ' + labels[Math.min(i + aggregateSize - 1, labels.length - 1)];
      }
      
      newLabels.push(label);
      newRates.push(Number(avgRate.toFixed(2)));
    }
    labels = newLabels;
    rates = newRates;
  }
  
  currentReportChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Occupancy Rate (%)',
        data: rates,
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        tension: 0.4,
        fill: true,
        borderWidth: 2,
        pointRadius: dayCount > 90 ? 5 : 3
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true, position: 'top' } },
      scales: {
        y: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%' } },
        x: { ticks: { maxRotation: 45, minRotation: 0 } }
      }
    }
  });
}

function renderRevenueChart(data) {
  const container = document.getElementById('report-chart-container');
  const canvas = document.getElementById('report-chart');
  if (!container || !canvas) return;
  
  let labels = (data.daily || []).map(d => fmtDate(d.date));
  let revenues = (data.daily || []).map(d => Number(d.revenue) || 0);
  
  container.style.display = 'block';
  
  if (currentReportChart) currentReportChart.destroy();
  
  // Aggregate data for large date ranges
  const dayCount = labels.length;
  if (dayCount > 90) {
    const aggregateSize = dayCount > 180 ? 30 : 7; // Monthly for 180+ days, weekly for 90+ days
    const newLabels = [];
    const newRevenues = [];
    const monthFormatter = new Intl.DateTimeFormat('en', { month: 'short', year: '2-digit' });
    
    for (let i = 0; i < labels.length; i += aggregateSize) {
      const chunk = revenues.slice(i, i + aggregateSize);
      const sumRevenue = chunk.reduce((a,b) => a+b, 0);
      
      let label;
      if (dayCount > 180) {
        // Monthly: use month name
        const date = new Date(labels[i]);
        label = monthFormatter.format(date);
      } else {
        // Weekly: use date range
        label = labels[i] + ' to ' + labels[Math.min(i + aggregateSize - 1, labels.length - 1)];
      }
      
      newLabels.push(label);
      newRevenues.push(Number(sumRevenue.toFixed(2)));
    }
    labels = newLabels;
    revenues = newRevenues;
  }
  
  currentReportChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: dayCount > 90 ? 'Period Revenue' : 'Daily Revenue',
        data: revenues,
        backgroundColor: '#27ae60',
        borderColor: '#229954',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true, position: 'top' } },
      scales: {
        y: { beginAtZero: true },
        x: { ticks: { maxRotation: 45, minRotation: 0 } }
      }
    }
  });
}

function renderTrendsChart(data) {
  const container = document.getElementById('report-chart-container');
  const canvas = document.getElementById('report-chart');
  if (!container || !canvas) return;
  
  container.style.display = 'block';
  
  if (currentReportChart) currentReportChart.destroy();
  
  currentReportChart = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: ['Confirmed', 'Cancelled', 'No-shows'],
      datasets: [{
        data: [
          data.confirmed_bookings || 0,
          data.cancellations || 0,
          data.no_shows || 0
        ],
        backgroundColor: ['#27ae60', '#e74c3c', '#f39c12'],
        borderWidth: 2,
        borderColor: '#ecf0f1'
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true, position: 'right' } }
    }
  });
}

// Export functions
function clearReportExports() {
  const container = document.getElementById('report-export-buttons');
  if (container) container.innerHTML = '';
  const chartContainer = document.getElementById('report-chart-container');
  if (chartContainer) chartContainer.style.display = 'none';
}

function showExportButtons(reportType, data) {
  const container = document.getElementById('report-export-buttons');
  if (!container) return;
  
  container.innerHTML = '';
  
  const csvBtn = document.createElement('button');
  csvBtn.className = 'btn btn-secondary btn-sm';
  csvBtn.textContent = '📥 CSV';
  csvBtn.addEventListener('click', () => exportCSV(reportType, data));
  container.appendChild(csvBtn);
  
  const pdfBtn = document.createElement('button');
  pdfBtn.className = 'btn btn-secondary btn-sm';
  pdfBtn.textContent = '📄 PDF';
  pdfBtn.addEventListener('click', () => exportPDF(reportType, data));
  container.appendChild(pdfBtn);
}

function exportCSV(reportType, data) {
  let csv = '';
  const timestamp = new Date().toISOString().slice(0, 10);
  
  if (reportType === 'occupancy') {
    csv = 'Occupancy Report\n';
    csv += `Period: ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}\n`;
    csv += `Average Occupancy: ${fmtPercent(data.average_occupancy)}\n\n`;
    csv += 'Date,Occupied,Total Rooms,Occupancy Rate\n';
    (data.daily || []).forEach(d => {
      csv += `${fmtDate(d.date)},${d.occupied},${d.total_rooms},${d.occupancy_rate}%\n`;
    });
  } else if (reportType === 'revenue') {
    csv = 'Revenue Report\n';
    csv += `Period: ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}\n`;
    csv += `Total Revenue: ${fmtCurrency(data.total_revenue)}\n\n`;
    csv += 'Date,Revenue\n';
    (data.daily || []).forEach(d => {
      csv += `${fmtDate(d.date)},${d.revenue}\n`;
    });
  } else if (reportType === 'trends') {
    csv = 'Booking Trends Report\n';
    csv += `Period: ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}\n\n`;
    csv += 'Metric,Value\n';
    csv += `Total Bookings,${data.total_bookings}\n`;
    csv += `Cancellations,${data.cancellations}\n`;
    csv += `No-shows,${data.no_shows}\n`;
    csv += `Cancellation Rate,${data.cancellation_rate}%\n`;
    csv += `No-show Rate,${data.no_show_rate}%\n`;
  }
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${reportType}-report-${timestamp}.csv`;
  link.click();
}

function exportPDF(reportType, data) {
  // Simple PDF export by printing to PDF
  const element = document.getElementById('report-output');
  if (!element) return;
  
  // Create a new window for printing
  const printWindow = window.open('', '', 'width=900,height=600');
  printWindow.document.write('<html><head><title>');
  printWindow.document.write(reportType + ' Report - ' + new Date().toISOString().slice(0, 10));
  printWindow.document.write('</title><style>');
  printWindow.document.write(`
    body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { background: #3498db; color: white; padding: 10px; text-align: left; }
    td { padding: 8px; border-bottom: 1px solid #ddd; }
    tr:nth-child(even) { background: #f9f9f9; }
    .report-header { font-size: 20px; font-weight: bold; margin: 20px 0 10px 0; border-bottom: 2px solid #3498db; }
    .report-summary { margin: 20px 0; }
    dt { font-weight: bold; margin-top: 10px; }
    dd { margin-left: 20px; font-size: 16px; }
  `);
  printWindow.document.write('</style></head><body>');
  printWindow.document.write(element.innerHTML);
  printWindow.document.write('</body></html>');
  printWindow.document.close();
  
  // Trigger print dialog
  setTimeout(() => {
    printWindow.print();
  }, 250);
}

// Date range helpers
function getToday() {
  return new Date().toISOString().slice(0, 10);
}

function addDays(date, n) {
  const d = new Date(date);
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

function setDateRange(days) {
  const today = getToday();
  const start = addDays(today, -days);
  document.getElementById('report-start').value = start;
  document.getElementById('report-end').value = today;
}

// Guest Functions
function renderGuestItem(g) {
  const li = document.createElement("li");
  const text = document.createElement("span");
  text.innerHTML = `<span class="item-id">#${g.id}</span>${g.name} ${g.surname}`;
  li.appendChild(text);

  const btnDelete = document.createElement("button");
  btnDelete.className = "btn btn-secondary btn-sm";
  btnDelete.textContent = "Delete";
  btnDelete.addEventListener("click", async () => {
    if (confirm("Delete this guest?")) {
      try {
        await apiFetch(`/guests/${g.id}`, { method: "DELETE" });
        listGuests();
      } catch (e) {
        showMessage("guests-message", `Delete failed: ${e.message}`, true);
      }
    }
  });

  li.appendChild(btnDelete);
  return li;
}

async function listGuests() {
  showMessage("guests-message", "");
  try {
    const guests = await apiFetch(`/guests/`);
    const ul = document.getElementById("guest-list");
    ul.innerHTML = "";
    if (guests && guests.length > 0) {
      guests.forEach(g => ul.appendChild(renderGuestItem(g)));
    } else {
      ul.innerHTML = '<li style="text-align: center; color: #7f8c8d;">No guests yet</li>';
    }
  } catch (e) {
    showMessage("guests-message", `Failed to load guests: ${e.message}`, true);
  }
}

async function createGuest() {
  const name = document.getElementById("guest-name").value.trim();
  const surname = document.getElementById("guest-surname").value.trim();
  const email = document.getElementById("guest-email").value.trim();

  if (!name || !surname || !email) {
    showMessage("guests-message", "Please fill all guest fields", true);
    return;
  }

  showMessage("guests-message", "Registering guest...");
  try {
    await apiFetch(`/guests/`, {
      method: "POST",
      body: JSON.stringify({ name, surname, email })
    });
    document.getElementById("guest-form").reset();
    await listGuests();
    showMessage("guests-message", "Guest registered successfully");
  } catch (e) {
    showMessage("guests-message", `Failed to register guest: ${e.message}`, true);
  }
}

// Booking Functions
function renderBookingItem(b) {
  const li = document.createElement("li");
  const text = document.createElement("span");
  text.innerHTML = `<span class="item-id">#${b.id}</span>Guest #${b.guest.id} ${b.guest.name} ${b.guest.surname} → Room ${b.room_id} | ${b.check_in} - ${b.check_out} | ${b.number_of_nights} Nights`;
  li.appendChild(text);

  const btnDelete = document.createElement("button");
  btnDelete.className = "btn btn-secondary btn-sm";
  btnDelete.textContent = "Cancel";
  btnDelete.addEventListener("click", async () => {
    if (confirm("Cancel this booking?")) {
      try {
        await apiFetch(`/bookings/${b.id}/cancel`, { method: "POST" });
        listBookings();
      } catch (e) {
        showMessage("bookings-message", `Failed to cancel: ${e.message}`, true);
      }
    }
  });

  li.appendChild(btnDelete);
  return li;
}

async function listBookings() {
  showMessage("bookings-message", "");
  try {
    const bookings = await apiFetch(`/bookings/`);
    const ul = document.getElementById("booking-list");
    ul.innerHTML = "";
    if (bookings && bookings.length > 0) {
      bookings.forEach(b => {
          if (b.status !== "cancelled") {
              ul.appendChild(renderBookingItem(b));
          }
      });
    } else {
      ul.innerHTML = '<li style="text-align: center; color: #7f8c8d;">No bookings yet</li>';
    }
  } catch (e) {
    showMessage("bookings-message", `Failed to load bookings: ${e.message}`, true);
  }
}

// Payments list
async function listPayments() {
  showMessage('payments-message', '');
  try {
    const payments = await apiFetch('/payments/');
    const ul = document.getElementById('payment-list');
    ul.innerHTML = '';
    if (payments && payments.length > 0) {
      payments.forEach(p => {
        const li = document.createElement('li');
        li.textContent = `#${p.id} Booking:${p.booking_id} ${p.amount} ${p.currency} — ${p.status}`;
        ul.appendChild(li);
      });
    } else {
      ul.innerHTML = '<li style="text-align: center; color: #7f8c8d;">No payments yet</li>';
    }
  } catch (e) {
    showMessage('payments-message', `Failed to load payments: ${e.message}`, true);
  }
}

async function createBooking() {
  const guest_id = parseInt(document.getElementById("booking-guest-id").value);
  const room_id = parseInt(document.getElementById("booking-room-id").value);
  const check_in = document.getElementById("booking-checkin").value;
  const check_out = document.getElementById("booking-checkout").value;

  if (!guest_id || !room_id || !check_in || !check_out) {
    showMessage("bookings-message", "Please fill all booking fields", true);
    return;
  }

  if (new Date(check_in) >= new Date(check_out)) {
    showMessage("bookings-message", "Check-out must be after check-in", true);
    return;
  }

  showMessage("bookings-message", "Creating reservation...");
  try {
    await apiFetch(`/bookings/`, {
      method: "POST",
      body: JSON.stringify({ guest_id, room_id, check_in, check_out })
    });
    document.getElementById("booking-form").reset();
    await listBookings();
    showMessage("bookings-message", "Reservation created successfully");
  } catch (e) {
    showMessage("bookings-message", `Failed to create reservation: ${e.message}`, true);
  }
}

// Event Listeners - Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  // Initialize theme and attach toggle safely
  initTheme();
  const themeBtn = document.getElementById("btn-toggle-theme");
  if (themeBtn) themeBtn.addEventListener("click", toggleTheme);

  // Auth buttons
  document.getElementById("btn-login").addEventListener("click", login);
  document.getElementById("btn-register").addEventListener("click", register);
  document.getElementById("btn-logout").addEventListener("click", logout);

  // Rooms
  document.getElementById("btn-refresh-rooms").addEventListener("click", listRooms);
  document.getElementById("btn-add-room").addEventListener("click", createRoom);

  // Guests
  document.getElementById("btn-refresh-guests").addEventListener("click", listGuests);
  document.getElementById("btn-add-guest").addEventListener("click", createGuest);

  // Bookings
  document.getElementById("btn-refresh-bookings").addEventListener("click", listBookings);
  document.getElementById("btn-add-booking").addEventListener("click", createBooking);

  // Payments
  document.getElementById("btn-refresh-payments").addEventListener("click", listPayments);
  document.getElementById("btn-add-payment").addEventListener("click", createPayment);

  // Reports buttons
  document.getElementById('btn-occupancy-report').addEventListener('click', fetchOccupancyReport);
  document.getElementById('btn-revenue-report').addEventListener('click', fetchRevenueReport);
  document.getElementById('btn-trends-report').addEventListener('click', fetchTrendsReport);

  // Set default date range (last 30 days)
  setDateRange(30);

  // Tab navigation
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", (e) => {
      const tabName = e.target.dataset.tab;

      // Update active tab button
      document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
      e.target.classList.add("active");

      // Update active tab content
      document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
      document.getElementById(tabName).classList.add("active");
    });
  });

  // Form submission handling
  document.getElementById("auth-form")?.addEventListener("submit", (e) => e.preventDefault());
  document.getElementById("room-form")?.addEventListener("submit", (e) => e.preventDefault());
  document.getElementById("guest-form")?.addEventListener("submit", (e) => e.preventDefault());
  document.getElementById("booking-form")?.addEventListener("submit", (e) => e.preventDefault());

  // Check for stored token and auto-login
  try {
    const storedToken = localStorage.getItem("authToken");
    if (storedToken) {
      authToken = storedToken;
      apiFetch("/users/me").then(userInfo => {
        currentUser = userInfo;
        updateUserDisplay(userInfo.username);
        if (userInfo.permission_level === "ADMIN") {
          document.getElementById("admin-link").style.display = "inline-flex";
        }
        hideAuthModal();
        listRooms();
        listGuests();
        listBookings();
        listRoomTypes();
        listPayments();
      }).catch(() => {
        // Token invalid, show auth
        showAuthModal();
      });
    } else {
      showAuthModal();
    }
  } catch (e) {
    showAuthModal();
  }
});