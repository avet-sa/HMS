// HMS Dashboard - Main Application Entry Point
// This file initializes the application and sets up all event listeners

document.addEventListener("DOMContentLoaded", () => {
  // Initialize theme and attach toggle
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

  // Invoices
  document.getElementById("btn-refresh-invoices").addEventListener("click", listInvoices);
  document.getElementById("btn-generate-invoice").addEventListener("click", generateInvoice);

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

      // Auto-load data when switching to certain tabs
      if (tabName === "invoices") {
        listInvoices();
      } else if (tabName === "rooms") {
        listRooms();
      } else if (tabName === "guests") {
        listGuests();
      } else if (tabName === "bookings") {
        listBookings();
      } else if (tabName === "payments") {
        listPayments();
      }
    });
  });

  // Form submission handling
  document.getElementById("auth-form")?.addEventListener("submit", (e) => e.preventDefault());
  document.getElementById("room-form")?.addEventListener("submit", (e) => e.preventDefault());
  document.getElementById("guest-form")?.addEventListener("submit", (e) => e.preventDefault());
  document.getElementById("booking-form")?.addEventListener("submit", (e) => e.preventDefault());

  // Check for stored token and auto-login
  restoreAuthFromStorage().catch(() => {
    showAuthModal();
  });
});