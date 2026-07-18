var gradeDialog = document.querySelector("#grade-dialog");
var gradeForm = document.querySelector("#grade-form");
var gradeClose = document.querySelector("#grade-close");
var gradeResult = document.querySelector("#grade-result");
var htmlGrade = document.querySelector("#html-grade");
var cssGrade = document.querySelector("#css-grade");
var javascriptGrade = document.querySelector("#javascript-grade");

function Grade() {
    gradeDialog.hidden = false;
    gradeResult.hidden = true;
    gradeResult.innerHTML = "";
    gradeForm.reset();
    document.body.classList.add("modal-open");
    htmlGrade.focus();
}

function closeGrade() {
    gradeDialog.hidden = true;
    document.body.classList.remove("modal-open");
}

gradeForm.addEventListener("submit", function (event) {
    event.preventDefault();

    var scores = [
        Number(htmlGrade.value),
        Number(cssGrade.value),
        Number(javascriptGrade.value)
    ];
    var total = 0;

    for (var i = 0; i < scores.length; i++) {
        total += scores[i];
    }

    var average = total / scores.length;
    var resultMessage = average >= 60 ? "합격입니다!" : "불합격입니다.";

    gradeResult.innerHTML =
        "<strong>성적 결과</strong>" +
        "<p>총점: " + total + "점</p>" +
        "<p>평균: " + average.toFixed(1) + "점</p>" +
        "<p>결과: " + resultMessage + "</p>";
    gradeResult.hidden = false;
});

gradeClose.addEventListener("click", closeGrade);

gradeDialog.addEventListener("click", function (event) {
    if (event.target === gradeDialog) {
        closeGrade();
    }
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !gradeDialog.hidden) {
        closeGrade();
    }
});
