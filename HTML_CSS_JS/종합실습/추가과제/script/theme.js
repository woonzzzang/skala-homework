var themeButton = document.querySelector(".theme-button");
var savedTheme = localStorage.getItem("archive-theme");

function updateThemeButton() {
    if (document.body.classList.contains("dark")) {
        themeButton.textContent = "☀️ 라이트모드";
    } else {
        themeButton.textContent = "🌙 다크모드";
    }
}

if (themeButton) {
    if (savedTheme === "dark") {
        document.body.classList.add("dark");
    }

    updateThemeButton();

    themeButton.addEventListener("click", function () {
        document.body.classList.toggle("dark");

        if (document.body.classList.contains("dark")) {
            localStorage.setItem("archive-theme", "dark");
        } else {
            localStorage.setItem("archive-theme", "light");
        }

        updateThemeButton();
    });
}
