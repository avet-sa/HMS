// UI rendering for CRUD operations

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
        await deleteRoomAPI(r.id);
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
    const rooms = await listRoomsAPI();
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

async function listRoomTypes() {
  try {
    const types = await listRoomTypesAPI();
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
    await createRoomAPI(number, room_type_id, price, square_meters, floor);
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
        await deleteGuestAPI(g.id);
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
    const guests = await listGuestsAPI();
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
    await createGuestAPI(name, surname, email);
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
        await cancelBookingAPI(b.id);
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
    const bookings = await listBookingsAPI();
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
    await createBookingAPI(guest_id, room_id, check_in, check_out);
    document.getElementById("booking-form").reset();
    await listBookings();
    showMessage("bookings-message", "Reservation created successfully");
  } catch (e) {
    showMessage("bookings-message", `Failed to create reservation: ${e.message}`, true);
  }
}

// Payment Functions
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
    const p = await createPaymentAPI(booking_id, amount, currency, method);
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

async function listPayments() {
  showMessage('payments-message', '');
  try {
    const payments = await listPaymentsAPI();
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
