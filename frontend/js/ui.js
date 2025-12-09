// UI rendering for CRUD operations

// Room Functions
function renderRoomItem(r) {
  const tr = document.createElement("tr");
  
  // ID column
  const tdId = document.createElement("td");
  tdId.textContent = r.id;
  tr.appendChild(tdId);
  
  // Room number column
  const tdNumber = document.createElement("td");
  tdNumber.textContent = r.number;
  tr.appendChild(tdNumber);
  
  // Type column
  const tdType = document.createElement("td");
  tdType.textContent = r.room_type?.name || "N/A";
  tr.appendChild(tdType);
  
  // Price column
  const tdPrice = document.createElement("td");
  tdPrice.textContent = `$${r.price_per_night}`;
  tr.appendChild(tdPrice);
  
  // Size column
  const tdSize = document.createElement("td");
  tdSize.textContent = r.square_meters || "N/A";
  tr.appendChild(tdSize);
  
  // Max Occupancy column
  const tdOccupancy = document.createElement("td");
  tdOccupancy.textContent = r.room_type?.max_occupancy || "N/A";
  tr.appendChild(tdOccupancy);
  
  // Floor column
  const tdFloor = document.createElement("td");
  tdFloor.textContent = r.floor;
  tr.appendChild(tdFloor);
  
  // Status column
  const tdStatus = document.createElement("td");
  const statusBadge = document.createElement("span");
  statusBadge.className = "badge badge-success";
  statusBadge.textContent = "Available";
  tdStatus.appendChild(statusBadge);
  tr.appendChild(tdStatus);
  
  // Actions column
  const tdActions = document.createElement("td");
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
  tdActions.appendChild(btnDelete);
  tr.appendChild(tdActions);

  return tr;
}

async function listRooms() {
  showMessage("rooms-message", "");
  try {
    const rooms = await listRoomsAPI();
    const tbody = document.getElementById("room-list");
    tbody.innerHTML = "";
    if (rooms && rooms.length > 0) {
      rooms.forEach(r => tbody.appendChild(renderRoomItem(r)));
    } else {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: #7f8c8d;">No rooms yet</td></tr>';
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
  const tr = document.createElement("tr");
  
  // ID column
  const tdId = document.createElement("td");
  tdId.textContent = g.id;
  tr.appendChild(tdId);
  
  // Name column
  const tdName = document.createElement("td");
  tdName.textContent = `${g.name} ${g.surname}`;
  tr.appendChild(tdName);
  
  // Email column
  const tdEmail = document.createElement("td");
  tdEmail.textContent = g.email || "N/A";
  tr.appendChild(tdEmail);
  
  // Phone column
  const tdPhone = document.createElement("td");
  tdPhone.textContent = g.phone || "N/A";
  tr.appendChild(tdPhone);
  
  // Registered column
  const tdRegistered = document.createElement("td");
  tdRegistered.textContent = g.created_at ? new Date(g.created_at).toLocaleDateString() : "N/A";
  tr.appendChild(tdRegistered);
  
  // Vip Tier column
  const tdVip = document.createElement("td");
  tdVip.textContent = g.vip_tier || "0";
  tr.appendChild(tdVip);
  
  // Actions column
  const tdActions = document.createElement("td");
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
  tdActions.appendChild(btnDelete);
  tr.appendChild(tdActions);

  return tr;
}

async function listGuests() {
  showMessage("guests-message", "");
  try {
    const guests = await listGuestsAPI();
    const tbody = document.getElementById("guest-list");
    tbody.innerHTML = "";
    if (guests && guests.length > 0) {
      guests.forEach(g => tbody.appendChild(renderGuestItem(g)));
    } else {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #7f8c8d;">No guests yet</td></tr>';
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
  const tr = document.createElement("tr");
  
  // ID column
  const tdId = document.createElement("td");
  tdId.textContent = b.id;
  tr.appendChild(tdId);
  
  // Guest column
  const tdGuest = document.createElement("td");
  tdGuest.textContent = b.guest ? `${b.guest.name} ${b.guest.surname}` : `Guest #${b.guest_id}`;
  tr.appendChild(tdGuest);
  
  // Room column
  const tdRoom = document.createElement("td");
  tdRoom.textContent = b.room_id;
  tr.appendChild(tdRoom);
  
  // Check-in column
  const tdCheckIn = document.createElement("td");
  tdCheckIn.textContent = b.check_in;
  tr.appendChild(tdCheckIn);
  
  // Check-out column
  const tdCheckOut = document.createElement("td");
  tdCheckOut.textContent = b.check_out;
  tr.appendChild(tdCheckOut);
  
  // Nights column
  const tdNights = document.createElement("td");
  tdNights.textContent = b.number_of_nights;
  tr.appendChild(tdNights);
  
  // Total Price column
  const tdPrice = document.createElement("td");
  tdPrice.textContent = b.total_price ? `$${b.total_price}` : "N/A";
  tr.appendChild(tdPrice);
  
  // Status column
  const tdStatus = document.createElement("td");
  const statusBadge = document.createElement("span");
  const status = b.status || "confirmed";
  statusBadge.className = `badge badge-${status === "confirmed" ? "success" : status === "checked_in" ? "info" : "warning"}`;
  statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
  tdStatus.appendChild(statusBadge);
  tr.appendChild(tdStatus);
  
  // Actions column
  const tdActions = document.createElement("td");
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
  tdActions.appendChild(btnDelete);
  tr.appendChild(tdActions);

  return tr;
}

async function listBookings() {
  showMessage("bookings-message", "");
  try {
    const bookings = await listBookingsAPI();
    const tbody = document.getElementById("booking-list");
    tbody.innerHTML = "";
    if (bookings && bookings.length > 0) {
      bookings.forEach(b => {
        if (b.status !== "cancelled") {
          tbody.appendChild(renderBookingItem(b));
        }
      });
      if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: #7f8c8d;">No active bookings</td></tr>';
      }
    } else {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: #7f8c8d;">No bookings yet</td></tr>';
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
    const tbody = document.getElementById('payment-list');
    tbody.innerHTML = '';
    if (payments && payments.length > 0) {
      payments.forEach(p => {
        const tr = document.createElement('tr');
        
        // ID column
        const tdId = document.createElement('td');
        tdId.textContent = p.id;
        tr.appendChild(tdId);
        
        // Booking ID column
        const tdBooking = document.createElement('td');
        tdBooking.textContent = p.booking_id;
        tr.appendChild(tdBooking);
        
        // Amount column
        const tdAmount = document.createElement('td');
        tdAmount.textContent = p.amount;
        tr.appendChild(tdAmount);
        
        // Currency column
        const tdCurrency = document.createElement('td');
        tdCurrency.textContent = p.currency;
        tr.appendChild(tdCurrency);
        
        // Method column
        const tdMethod = document.createElement('td');
        tdMethod.textContent = p.method || 'N/A';
        tr.appendChild(tdMethod);
        
        // Reference column
        const tdTransaction = document.createElement('td');
        tdTransaction.textContent = p.reference || 'N/A';
        tr.appendChild(tdTransaction);
        
        // Date column
        const tdDate = document.createElement('td');
        tdDate.textContent = p.created_at ? new Date(p.created_at).toLocaleDateString() : 'N/A';
        tr.appendChild(tdDate);
        
        // Status column
        const tdStatus = document.createElement('td');
        const statusBadge = document.createElement('span');
        const status = (p.status || '').toLowerCase();
        const statusClass = (() => {
          if (['completed', 'paid', 'succeeded'].includes(status)) return 'badge badge-success';
          if (['pending', 'processing', 'in_progress'].includes(status)) return 'badge badge-warning';
          if (['refunded'].includes(status)) return 'badge badge-info';
          if (['failed', 'declined', 'canceled', 'cancelled', 'voided'].includes(status)) return 'badge badge-danger';
          return 'badge badge-info';
        })();
        statusBadge.className = statusClass;
        const label = status ? status.replace(/_/g, ' ') : 'Unknown';
        statusBadge.textContent = label.charAt(0).toUpperCase() + label.slice(1);
        tdStatus.appendChild(statusBadge);
        tr.appendChild(tdStatus);
        
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #7f8c8d;">No payments yet</td></tr>';
    }
  } catch (e) {
    showMessage('payments-message', `Failed to load payments: ${e.message}`, true);
  }
}
