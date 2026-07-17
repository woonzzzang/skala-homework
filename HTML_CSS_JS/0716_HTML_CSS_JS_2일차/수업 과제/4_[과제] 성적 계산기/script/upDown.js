function UpDownGame () {
    var computerNum = Math.floor(Math.random() * 50) + 1;
    var count = 0;

    while (true) {
        var userInput = prompt ("1부터 50 사이의 숫자 중 컴퓨터가 생각한 숫자는 무엇일까요?");

        if (userInput === null) {
            alert("게임을 취소했습니다.");
            break;
        }

        if (userInput.trim() === "") {
            alert("숫자를 입력해 주세요.");
            continue;
        }

        var userNum = Number(userInput);
        count++;

        if (userNum > computerNum) {
            alert("Down!");
        } else if (userNum < computerNum) {
            alert("Up!");
        } else {
            alert("축하합니다! " + count + "번 만에 맞추셨습니다.");
            break;
        }
    }
}