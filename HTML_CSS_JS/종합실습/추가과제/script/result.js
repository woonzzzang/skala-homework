var params = new URLSearchParams(location.search);
var resultTable = document.querySelector("#resultTable");

var fields = [
    ["userName", "이름"],
    ["userId", "아이디"],
    ["userPw", "비밀번호"],
    ["userEmail", "이메일"],
    ["userTel", "전화번호"],
    ["userBirth", "생년월일"],
    ["gender", "성별"],
    ["interest", "관심 분야"],
    ["region", "지역"],
    ["intro", "자기소개"],
    ["agree", "약관 동의"]
];

function getValue(name) {
    var values = params.getAll(name);

    if (values.length === 0 || values.join("").trim() === "") {
        return "-";
    }

    return values.join(", ");
}

for (var i = 0; i < fields.length; i++) {
    var tr = document.createElement("tr");
    var th = document.createElement("th");
    var td = document.createElement("td");

    th.textContent = fields[i][1];
    td.textContent = getValue(fields[i][0]);

    tr.appendChild(th);
    tr.appendChild(td);
    resultTable.appendChild(tr);
}
