var scheduleWeek = document.querySelector("#schedule-week");
var scheduleList = document.querySelector("#schedule-list");
var schedulePrev = document.querySelector("#schedule-prev");
var scheduleNext = document.querySelector("#schedule-next");
var lunchToggle = document.querySelector("#lunch-toggle");
var lunchDialog = document.querySelector("#lunch-dialog");
var lunchClose = document.querySelector("#lunch-close");
var lunchPanel = document.querySelector("#lunch-panel");
var scheduleData = {};
var weeklyMeals = {};
var availableWeeks = [];
var activeWeekIndex = 0;
var selectedWeekDates = [];

function parseCsv(text) {
    var rows = [];
    var row = [];
    var field = "";
    var inQuotes = false;

    for (var i = 0; i < text.length; i++) {
        var character = text[i];
        var nextCharacter = text[i + 1];

        if (character === '"' && inQuotes && nextCharacter === '"') {
            field += '"';
            i++;
        } else if (character === '"') {
            inQuotes = !inQuotes;
        } else if (character === "," && !inQuotes) {
            row.push(field);
            field = "";
        } else if (character === "\n" && !inQuotes) {
            row.push(field);
            rows.push(row);
            row = [];
            field = "";
        } else if (character !== "\r") {
            field += character;
        }
    }

    row.push(field);
    rows.push(row);
    return rows;
}

function cleanText(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
}

function formatDate(date) {
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, "0");
    var day = String(date.getDate()).padStart(2, "0");
    return year + "-" + month + "-" + day;
}

function getMonday(dateText) {
    var date = new Date(dateText + "T00:00:00");
    var day = date.getDay();
    var move = day === 0 ? -6 : 1 - day;

    date.setDate(date.getDate() + move);
    return formatDate(date);
}

function getWeekDates(mondayText) {
    var monday = new Date(mondayText + "T00:00:00");
    var dates = [];

    for (var i = 0; i < 5; i++) {
        var date = new Date(monday);
        date.setDate(monday.getDate() + i);
        dates.push(formatDate(date));
    }

    return dates;
}

function parseSchedule(rows) {
    var schedule = {};

    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var date = cleanText(row[0]);

        if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
            continue;
        }

        schedule[date] = {
            course: cleanText(row[3]),
            instructor: cleanText(row[7])
        };
    }

    return schedule;
}

function parseLunchMenus(rows) {
    var meals = {};
    var dateColumns = [];
    var isLunch = false;

    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var foundDates = [];

        for (var j = 0; j < row.length; j++) {
            var match = cleanText(row[j]).match(/(\d+)월\s*(\d+)일/);

            if (match) {
                foundDates.push({
                    column: j,
                    date: "2026-" + String(match[1]).padStart(2, "0") + "-" + String(match[2]).padStart(2, "0")
                });
            }
        }

        if (foundDates.length > 0) {
            dateColumns = foundDates;
            isLunch = false;
            continue;
        }

        var mealType = cleanText(row[0]).replace(/\s/g, "");

        if (mealType === "중식") {
            isLunch = true;
            continue;
        }

        if (mealType === "조식" || mealType === "석식") {
            isLunch = false;
            continue;
        }

        if (!isLunch) {
            continue;
        }

        for (var k = 0; k < dateColumns.length; k++) {
            var dateInfo = dateColumns[k];
            var menu = cleanText(row[dateInfo.column]);

            if (menu) {
                if (!meals[dateInfo.date]) {
                    meals[dateInfo.date] = [];
                }

                meals[dateInfo.date].push(menu);
            }
        }
    }

    return meals;
}

function createElement(tagName, className, text) {
    var element = document.createElement(tagName);

    if (className) {
        element.className = className;
    }

    if (text) {
        element.textContent = text;
    }

    return element;
}

function getAvailableWeeks(schedule) {
    var weekMap = {};
    var scheduleDates = Object.keys(schedule);

    for (var i = 0; i < scheduleDates.length; i++) {
        var date = scheduleDates[i];

        if (schedule[date].course) {
            weekMap[getMonday(date)] = true;
        }
    }

    return Object.keys(weekMap).sort();
}

function getLatestMealWeek(meals) {
    var weekMap = {};
    var mealDates = Object.keys(meals);

    for (var i = 0; i < mealDates.length; i++) {
        weekMap[getMonday(mealDates[i])] = true;
    }

    var mealWeeks = Object.keys(weekMap).sort();
    return mealWeeks[mealWeeks.length - 1];
}

function getDateLabel(dateText) {
    var date = new Date(dateText + "T00:00:00");
    var dayNames = ["일", "월", "화", "수", "목", "금", "토"];
    return dayNames[date.getDay()] + "요일 " + (date.getMonth() + 1) + "/" + date.getDate();
}

function renderSchedule() {
    scheduleList.innerHTML = "";
    var block = createElement("div", "schedule-week-block");

    for (var i = 0; i < selectedWeekDates.length; i++) {
        var date = selectedWeekDates[i];
        var daySchedule = scheduleData[date] || {};
        var row = createElement("div", "schedule-row");

        row.append(createElement("span", "schedule-row-date", getDateLabel(date)));
        row.append(createElement("strong", "schedule-row-course", daySchedule.course || "수업 정보 없음"));
        row.append(createElement("span", "schedule-row-instructor", daySchedule.instructor || ""));
        block.append(row);
    }

    scheduleList.append(block);
}

function renderLunchMenu() {
    lunchPanel.innerHTML = "";

    for (var i = 0; i < selectedWeekDates.length; i++) {
        var date = selectedWeekDates[i];
        var mealDay = createElement("article", "meal-day");
        var menuList = weeklyMeals[date] || ["등록된 중식 메뉴가 없습니다."];
        var list = document.createElement("ul");

        mealDay.append(createElement("h4", "", getDateLabel(date)));

        for (var j = 0; j < menuList.length; j++) {
            list.append(createElement("li", "", menuList[j]));
        }

        mealDay.append(list);
        lunchPanel.append(mealDay);
    }
}

function updateWeek() {
    selectedWeekDates = getWeekDates(availableWeeks[activeWeekIndex]);

    var start = new Date(selectedWeekDates[0] + "T00:00:00");
    var end = new Date(selectedWeekDates[4] + "T00:00:00");

    scheduleWeek.textContent = (start.getMonth() + 1) + "/" + start.getDate() + "~" + (end.getMonth() + 1) + "/" + end.getDate() + " · 204호 3반";
    schedulePrev.disabled = activeWeekIndex === 0;
    scheduleNext.disabled = activeWeekIndex === availableWeeks.length - 1;
    renderSchedule();
    renderLunchMenu();
}

function showScheduleError() {
    scheduleWeek.textContent = "시간표를 불러오지 못했습니다.";
    scheduleList.textContent = "로컬 서버에서 다시 열어 주세요.";
}

Promise.all([
    fetch("data/schedule.csv").then(function (response) { return response.text(); }),
    fetch("data/lunch-menu.csv").then(function (response) { return response.text(); })
]).then(function (data) {
    scheduleData = parseSchedule(parseCsv(data[0]));
    weeklyMeals = parseLunchMenus(parseCsv(data[1]));
    availableWeeks = getAvailableWeeks(scheduleData);

    if (availableWeeks.length === 0) {
        throw new Error("표시할 주차가 없습니다.");
    }

    var latestMealWeek = getLatestMealWeek(weeklyMeals);
    var latestMealIndex = availableWeeks.indexOf(latestMealWeek);

    activeWeekIndex = latestMealIndex >= 0 ? latestMealIndex : availableWeeks.length - 1;
    updateWeek();
    lunchToggle.disabled = false;
    lunchToggle.textContent = "🍚 12:00~13:00 점심시간 · 중식 보기";
}).catch(showScheduleError);

schedulePrev.addEventListener("click", function () {
    if (activeWeekIndex > 0) {
        activeWeekIndex--;
        updateWeek();
    }
});

scheduleNext.addEventListener("click", function () {
    if (activeWeekIndex < availableWeeks.length - 1) {
        activeWeekIndex++;
        updateWeek();
    }
});

lunchToggle.addEventListener("click", function () {
    lunchDialog.hidden = false;
    document.body.classList.add("modal-open");
    lunchClose.focus();
});

lunchClose.addEventListener("click", function () {
    lunchDialog.hidden = true;
    document.body.classList.remove("modal-open");
    lunchToggle.focus();
});

lunchDialog.addEventListener("click", function (event) {
    if (event.target === lunchDialog) {
        lunchDialog.hidden = true;
        document.body.classList.remove("modal-open");
        lunchToggle.focus();
    }
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !lunchDialog.hidden) {
        lunchDialog.hidden = true;
        document.body.classList.remove("modal-open");
        lunchToggle.focus();
    }
});
