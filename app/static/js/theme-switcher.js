// Theme switcher
let storedTheme = localStorage.getItem("theme") || "light";
document.documentElement.setAttribute("data-theme", storedTheme);
localStorage.setItem("theme", storedTheme);
const themeIcon = document.getElementById("theme-icon");
if (storedTheme === "dark") {
  themeIcon.setAttribute("class", "bi bi-sun");
} else {
  themeIcon.setAttribute("class", "bi bi-moon");
}

let themeSwitcher = document.getElementById("theme-switcher");
themeSwitcher.addEventListener("click", () => {
  let theme = document.documentElement.getAttribute("data-theme");
  let newTheme = theme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  let themeIcon = document.getElementById("theme-icon");
  if (newTheme === "dark") {
    themeIcon.setAttribute("class", "bi bi-sun");
  } else {
    themeIcon.setAttribute("class", "bi bi-moon");
  }
  themeSwitcher.blur();
});
