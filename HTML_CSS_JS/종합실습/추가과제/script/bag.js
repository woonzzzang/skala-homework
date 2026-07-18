function showMyBag() {
    var myBag = [
        { name: "여권", emoji: "✈️", count: 1},
        { name: "스마트폰", emoji: "📱", count: 2},
        { name: "지갑", emoji: "💳", count: 1}
    ];

    var massage = "🎒 [내 가방 속 물품 목록]\n\n";

    for (var i = 0; i < myBag.length; i++) {
        massage += "- " + myBag[i].name + " " + myBag[i].emoji + " : " + myBag[i].count + "개\n";
    } 

    massage += "------------------\n";
    massage += "총 물품 종류: " + myBag.length + "가지";

    alert(massage);
}