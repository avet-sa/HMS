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
  try { localStorage.setItem("theme", isDarkTheme ? "dark" : "light"); } catch (e) {}
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
    const data = await apiFetch(`/auth/login`, {
      method: "POST",
      body: JSON.stringify({ username, password })
    });
    authToken = data.token || authToken;
    currentUser = username;
    updateUserDisplay(username);
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    hideAuthModal();
    showMessage("auth-message", "");
    // Load data
    setTimeout(() => { listRooms(); listGuests(); listBookings(); }, 200);
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
  document.getElementById("user-display").textContent = "Guest";
  document.getElementById("btn-logout").style.display = "none";
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
  text.innerHTML = `<span class="item-id">#${b.id}</span>Guest ${b.guest_id} → Room ${b.room_id} (${b.check_in})`;
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
      bookings.forEach(b => ul.appendChild(renderBookingItem(b)));
    } else {
      ul.innerHTML = '<li style="text-align: center; color: #7f8c8d;">No bookings yet</li>';
    }
  } catch (e) {
    showMessage("bookings-message", `Failed to load bookings: ${e.message}`, true);
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

  // Show auth modal on start
  showAuthModal();
});