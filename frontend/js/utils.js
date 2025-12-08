// Utility functions for formatting and DOM manipulation

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

function showMessage(id, message, isError = false) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = message;
  el.classList.toggle("error", !!isError);
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
