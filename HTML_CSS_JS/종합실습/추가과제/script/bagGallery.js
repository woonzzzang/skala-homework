var themeButton = document.querySelector("#themeButton");

themeButton.addEventListener("click", function () {
    document.body.classList.toggle("dark");

    if (document.body.classList.contains("dark")) {
        themeButton.textContent = "☀️ 라이트모드";
    } else {
        themeButton.textContent = "🌙 다크모드";
    }
});
