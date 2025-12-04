const API_URL = "http://127.0.0.1:8000"; // FastAPI backend URL
let authToken = null;

// ----------- AUTH -----------
async function register() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  document.getElementById("auth-message").innerText = JSON.stringify(data);
}

async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  document.getElementById("auth-message").innerText = JSON.stringify(data);
  if (res.ok) authToken = data.token || "dummy"; // placeholder for JWT
}

// ----------- ROOMS -----------
async function listRooms() {
  const res = await fetch(`${API_URL}/rooms/`);
  const rooms = await res.json();
  const ul = document.getElementById("room-list");
  ul.innerHTML = "";

  rooms.forEach(r => {
    const li = document.createElement("li");
    li.innerHTML = `#${r.id} - ${r.number} | $${r.price_per_night} 
      <button onclick="deleteRoom(${r.id})">Delete</button>
      <button onclick="updateRoomPrompt(${r.id}, ${r.price_per_night})">Update</button>`;
    ul.appendChild(li);
  });
}

async function createRoom() {
  const number = document.getElementById("room-number").value;
  const price = parseFloat(document.getElementById("room-price").value);

  await fetch(`${API_URL}/rooms/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ number, price_per_night: price })
  });

  listRooms();
}

async function deleteRoom(id) {
  await fetch(`${API_URL}/rooms/${id}`, { method: "DELETE" });
  listRooms();
}

async function updateRoomPrompt(id, currentPrice) {
  const newPrice = prompt("Enter new price:", currentPrice);
  if (newPrice) {
    await fetch(`${API_URL}/rooms/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ price_per_night: parseFloat(newPrice) })
    });
    listRooms();
  }
}

// ----------- GUESTS -----------
async function listGuests() {
  const res = await fetch(`${API_URL}/guests/`);
  const guests = await res.json();
  const ul = document.getElementById("guest-list");
  ul.innerHTML = "";

  guests.forEach(g => {
    const li = document.createElement("li");
    li.innerHTML = `#${g.id} - ${g.name} ${g.surname} | ${g.email}
      <button onclick="deleteGuest(${g.id})">Delete</button>
      <button onclick="updateGuestPrompt(${g.id}, '${g.name}', '${g.surname}', '${g.email}')">Update</button>`;
    ul.appendChild(li);
  });
}

async function createGuest() {
  const name = document.getElementById("guest-name").value;
  const surname = document.getElementById("guest-surname").value;
  const email = document.getElementById("guest-email").value;

  await fetch(`${API_URL}/guests/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, surname, email })
  });

  listGuests();
}

async function deleteGuest(id) {
  await fetch(`${API_URL}/guests/${id}`, { method: "DELETE" });
  listGuests();
}

async function updateGuestPrompt(id, name, surname, email) {
  const newName = prompt("Name:", name);
  const newSurname = prompt("Surname:", surname);
  const newEmail = prompt("Email:", email);

  await fetch(`${API_URL}/guests/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: newName, surname: newSurname, email: newEmail })
  });

  listGuests();
}

// ----------- BOOKINGS -----------
async function listBookings() {
  const res = await fetch(`${API_URL}/bookings/`);
  const bookings = await res.json();
  const ul = document.getElementById("booking-list");
  ul.innerHTML = "";

  bookings.forEach(b => {
    const li = document.createElement("li");
    li.innerHTML = `#${b.id} - Guest:${b.guest_id} Room:${b.room_id} | ${b.check_in} → ${b.check_out} | ${b.status}
      <button onclick="checkIn(${b.id})">Check-in</button>
      <button onclick="checkOut(${b.id})">Check-out</button>
      <button onclick="cancelBooking(${b.id})">Cancel</button>`;
    ul.appendChild(li);
  });
}

async function createBooking() {
  const guest_id = parseInt(document.getElementById("booking-guest-id").value);
  const room_id = parseInt(document.getElementById("booking-room-id").value);
  const check_in = document.getElementById("booking-checkin").value;
  const check_out = document.getElementById("booking-checkout").value;

  await fetch(`${API_URL}/bookings/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ guest_id, room_id, check_in, check_out })
  });

  listBookings();
}

async function checkIn(id) {
  await fetch(`${API_URL}/bookings/${id}/checkin`, { method: "POST" });
  listBookings();
}

async function checkOut(id) {
  await fetch(`${API_URL}/bookings/${id}/checkout`, { method: "POST" });
  listBookings();
}

async function cancelBooking(id) {
  await fetch(`${API_URL}/bookings/${id}/cancel`, { method: "POST" });
  listBookings();
}