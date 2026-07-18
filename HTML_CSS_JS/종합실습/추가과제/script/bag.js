var myBag = [
    {
        name: "여권",
        emoji: "✈️",
        count: 1,
        category: "Travel",
        description: "여행이나 신분 확인이 필요한 상황을 대비해 챙기는 중요한 물건입니다."
    },
    {
        name: "스마트폰",
        emoji: "📱",
        count: 1,
        category: "Device",
        description: "연락, 사진, 길 찾기, 일정 확인까지 가장 자주 꺼내 쓰는 필수품입니다."
    },
    {
        name: "지갑",
        emoji: "💳",
        count: 1,
        category: "Money",
        description: "카드와 현금을 챙겨두는 물건으로, 외출할 때 가장 먼저 확인합니다."
    },
    {
        name: "노트북",
        emoji: "💻",
        count: 1,
        category: "Study",
        description: "수업 자료를 확인하고 과제를 진행할 때 사용하는 작업 도구입니다."
    },
    {
        name: "충전기",
        emoji: "🔌",
        count: 2,
        category: "Power",
        description: "스마트폰과 노트북 배터리가 부족할 때를 대비해 꼭 챙겨두는 물건입니다."
    },
    {
        name: "텀블러",
        emoji: "☕️",
        count: 1,
        category: "Life",
        description: "수업 중에도 물이나 커피를 마실 수 있도록 가방에 넣어두는 물건입니다."
    }
];

function createBagCard(item) {
    var card = document.createElement("article");
    var image = document.createElement("div");
    var info = document.createElement("div");
    var category = document.createElement("p");
    var name = document.createElement("h3");
    var description = document.createElement("p");
    var cardBottom = document.createElement("div");
    var count = document.createElement("strong");

    card.className = "product-card";
    image.className = "product-image";
    image.textContent = item.emoji;

    info.className = "product-info";
    category.className = "category";
    category.textContent = item.category;
    name.textContent = item.name;
    description.textContent = item.description;

    cardBottom.className = "card-bottom";
    count.textContent = item.count + "개";

    cardBottom.appendChild(count);
    info.appendChild(category);
    info.appendChild(name);
    info.appendChild(description);
    info.appendChild(cardBottom);
    card.appendChild(image);
    card.appendChild(info);

    return card;
}

function showMyBag() {
    var bagList = document.querySelector("#bag-list");
    var bagCount = document.querySelector("#bag-count");

    bagList.innerHTML = "";

    for (var i = 0; i < myBag.length; i++) {
        bagList.appendChild(createBagCard(myBag[i]));
    }

    bagCount.textContent = "총 " + myBag.length + "가지 물품";
}

showMyBag();
