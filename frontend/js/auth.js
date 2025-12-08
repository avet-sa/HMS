// Authentication management

let authToken = null;
let currentUser = null;

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

async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  if (!username || !password) {
    showMessage("auth-message", "Please enter username and password", true);
    return;
  }

  showMessage("auth-message", "Signing in...");
  try {
    const data = await loginAPI(username, password);
    authToken = data.access_token;

    // Store token in localStorage
    try { localStorage.setItem("authToken", authToken); } catch (e) { }

    // Fetch user info to check permission level
    const userInfo = await fetchUserInfoAPI();
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
    setTimeout(() => {
      listRooms();
      listGuests();
      listBookings();
      listRoomTypes();
      listPayments();
    }, 200);
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
    await registerAPI(username, password);
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

async function restoreAuthFromStorage() {
  try {
    const storedToken = localStorage.getItem("authToken");
    if (storedToken) {
      authToken = storedToken;
      const userInfo = await fetchUserInfoAPI();
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
      return true;
    }
  } catch (e) {
    // Token invalid
    authToken = null;
  }
  return false;
}
