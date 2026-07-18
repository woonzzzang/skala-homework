var cities = {
    paris: {
        name: "프랑스 파리 FR",
        latitude: 48.85,
        longitude: 2.35
    },
    tokyo: {
        name: "일본 도쿄 JP",
        latitude: 35.68,
        longitude: 139.69
    },
    seoul: {
        name: "대한민국 서울 KR",
        latitude: 37.57,
        longitude: 126.98
    }
};

var citySelect = document.querySelector("#city-select");
var weatherBox = document.querySelector("#weather-box");

//사용자가 도시 변경 할 때 마다 실행

citySelect.addEventListener("change", function () {
    var selectedCity = citySelect.value;

    if (selectedCity === "") {
        weatherBox.innerHTML = "도시를 선택해주시면 정보가 표시됩니다.";
        return;
    }

    var city = cities[selectedCity];

    weatherBox.innerHTML = 
        "<h4>📍 " + city.name + " 정보</h4>" +
        "<p>위도(Latitude): " + city.latitude + "</p>" +
        "<p>경도(Longitude): " + city.longitude + "</p>";

});
