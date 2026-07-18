function Grade () {
    var subjects = ["HTML", "CSS", "JavaScript"];
    var total = 0;

    for (let value of subjects) {
        var grade = prompt(value + "점수를 입력하세요.");
        total += Number(grade)
    }

    let cnt = subjects.length
    let avg = total/cnt

    if (avg >= 60) {
        alert("====== 📊 성적 결과표 ======" + "\n" + "• 총점: " + total + "\n" + "• 평균: " + avg + "\n" + "------------------------" + "\n" + "• 결과: 🎉 합격입니다! 우수자로 선정되었습니다.")
    } else {
        alert("====== 📊 성적 결과표 ======" + "\n" + "• 총점: " + total + "\n" + "• 평균: " + avg + "\n" + "------------------------" + "\n" + "• 결과: 불합격입니다.")
    }
}