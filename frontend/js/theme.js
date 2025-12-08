// Theme management

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
