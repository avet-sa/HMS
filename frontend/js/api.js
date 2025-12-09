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

// Room API calls
async function listRoomsAPI(page = 1, page_size = 50, search = '') {
  let url = `/rooms/?page=${page}&page_size=${page_size}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  return await apiFetch(url);
}

async function createRoomAPI(number, room_type_id, price_per_night, square_meters, floor) {
  return await apiFetch('/rooms/', {
    method: "POST",
    body: JSON.stringify({ number, room_type_id, price_per_night, square_meters, floor })
  });
}

async function deleteRoomAPI(id) {
  return await apiFetch(`/rooms/${id}`, { method: "DELETE" });
}

// Room Types API calls
async function listRoomTypesAPI() {
  return await apiFetch('/room-types/');
}

// Guest API calls
async function listGuestsAPI(page = 1, page_size = 50, search = '') {
  let url = `/guests/?page=${page}&page_size=${page_size}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  return await apiFetch(url);
}

async function createGuestAPI(name, surname, email) {
  return await apiFetch('/guests/', {
    method: "POST",
    body: JSON.stringify({ name, surname, email })
  });
}

async function deleteGuestAPI(id) {
  return await apiFetch(`/guests/${id}`, { method: "DELETE" });
}

// Booking API calls
async function listBookingsAPI(page = 1, page_size = 50, search = '') {
  let url = `/bookings/?page=${page}&page_size=${page_size}&sort_order=desc`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  return await apiFetch(url);
}

async function createBookingAPI(guest_id, room_id, check_in, check_out) {
  return await apiFetch('/bookings/', {
    method: "POST",
    body: JSON.stringify({ guest_id, room_id, check_in, check_out })
  });
}

async function cancelBookingAPI(id) {
  return await apiFetch(`/bookings/${id}/cancel`, { method: "POST" });
}

// Payment API calls
async function listPaymentsAPI(page = 1, page_size = 50, status = '') {
  let url = `/payments/?page=${page}&page_size=${page_size}&sort_order=desc`;
  if (status) url += `&status=${encodeURIComponent(status)}`;
  return await apiFetch(url);
}

async function createPaymentAPI(booking_id, amount, currency = 'USD', method = 'card') {
  return await apiFetch('/payments/create', {
    method: 'POST',
    body: JSON.stringify({ booking_id, amount, currency, method })
  });
}

// Report API calls
async function fetchOccupancyReportAPI(start_date, end_date) {
  return await apiFetch(`/occupancy?start_date=${start_date}&end_date=${end_date}`);
}

async function fetchRevenueReportAPI(start_date, end_date) {
  return await apiFetch(`/revenue?start_date=${start_date}&end_date=${end_date}`);
}

async function fetchTrendsReportAPI(start_date, end_date) {
  return await apiFetch(`/trends?start_date=${start_date}&end_date=${end_date}`);
}

// Invoice API calls
async function listInvoicesAPI(page = 1, page_size = 50, search = '') {
  let url = `/invoices/?page=${page}&page_size=${page_size}&sort_order=desc`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  return await apiFetch(url);
}

async function generateInvoiceAPI(booking_id) {
  return await apiFetch(`/invoices/${booking_id}`, {
    method: 'POST'
  });
}

async function downloadInvoicePDFAPI(invoice_id) {
  const headers = {};
  if (authToken) headers["Authorization"] = `Bearer ${authToken}`;
  
  const res = await fetch(`${API_URL}/invoices/${invoice_id}/pdf`, { headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to download PDF');
  }
  return await res.blob();
}

// Auth API calls
async function registerAPI(username, password) {
  return await apiFetch('/auth/register', {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
}

async function loginAPI(username, password) {
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

  return await res.json();
}

async function fetchUserInfoAPI() {
  return await apiFetch("/users/me");
}
