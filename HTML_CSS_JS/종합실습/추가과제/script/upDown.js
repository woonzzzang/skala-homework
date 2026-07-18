var upDownDialog = document.querySelector("#updown-dialog");
var upDownForm = document.querySelector("#updown-form");
var upDownInput = document.querySelector("#updown-input");
var upDownMessage = document.querySelector("#updown-message");
var upDownCount = document.querySelector("#updown-count");
var upDownClose = document.querySelector("#updown-close");
var upDownRestart = document.querySelector("#updown-restart");

var computerNum = 0;
var count = 0;

function resetUpDownGame() {
    computerNum = Math.floor(Math.random() * 50) + 1;
    count = 0;
    upDownInput.value = "";
    upDownInput.disabled = false;
    upDownForm.querySelector("button").disabled = false;
    upDownMessage.textContent = "숫자를 입력하면 힌트가 표시됩니다.";
    upDownCount.textContent = "시도 횟수: 0회";
    upDownInput.focus();
}

function UpDownGame() {
    upDownDialog.hidden = false;
    document.body.classList.add("modal-open");
    resetUpDownGame();
}

function closeUpDownGame() {
    upDownDialog.hidden = true;
    document.body.classList.remove("modal-open");
}

upDownForm.addEventListener("submit", function (event) {
    event.preventDefault();

    var userNum = Number(upDownInput.value);

    if (!Number.isInteger(userNum) || userNum < 1 || userNum > 50) {
        upDownMessage.textContent = "1부터 50 사이의 정수를 입력해 주세요.";
        upDownInput.focus();
        return;
    }

    count++;
    upDownCount.textContent = "시도 횟수: " + count + "회";

    if (userNum > computerNum) {
        upDownMessage.textContent = "Down! 더 작은 숫자입니다.";
    } else if (userNum < computerNum) {
        upDownMessage.textContent = "Up! 더 큰 숫자입니다.";
    } else {
        upDownMessage.textContent = "축하합니다! " + count + "번 만에 맞혔습니다.";
        upDownInput.disabled = true;
        upDownForm.querySelector("button").disabled = true;
    }

    upDownInput.select();
});

upDownClose.addEventListener("click", closeUpDownGame);
upDownRestart.addEventListener("click", resetUpDownGame);

upDownDialog.addEventListener("click", function (event) {
    if (event.target === upDownDialog) {
        closeUpDownGame();
    }
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !upDownDialog.hidden) {
        closeUpDownGame();
    }
});
