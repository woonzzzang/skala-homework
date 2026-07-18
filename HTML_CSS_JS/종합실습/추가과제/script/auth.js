var guestMenu = document.querySelector("#guest-menu");
var userMenu = document.querySelector("#user-menu");
var logoutButton = document.querySelector("#logout-button");
var loginForm = document.querySelector("#login-form");

function updateAuthMenu() {
    var isLoggedIn = localStorage.getItem("archiveLoggedIn") === "true";

    if (guestMenu !== null) {
        guestMenu.hidden = isLoggedIn;
    }

    if (userMenu !== null) {
        userMenu.hidden = !isLoggedIn;
    }
}

if (loginForm !== null) {
    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();

        var loginId = document.querySelector("#loginId").value;
        var loginPw = document.querySelector("#loginPw").value;

        if (loginId.trim() === "" || loginPw.trim() === "") {
            alert("아이디와 비밀번호를 모두 입력해 주세요.");
            return;
        }

        localStorage.setItem("archiveLoggedIn", "true");
        localStorage.setItem("archiveUserName", loginId.trim());
        alert(loginId.trim() + "님, 로그인되었습니다.");
        location.href = "index.html";
    });
}

if (logoutButton !== null) {
    logoutButton.addEventListener("click", function () {
        localStorage.removeItem("archiveLoggedIn");
        localStorage.removeItem("archiveUserName");
        alert("로그아웃되었습니다.");
        updateAuthMenu();
    });
}

updateAuthMenu();
