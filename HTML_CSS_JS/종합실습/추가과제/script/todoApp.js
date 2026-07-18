import { loadTodos, saveTodos } from "./todoStorage.js";

var todoForm = document.querySelector("#todoForm");
var todoInput = document.querySelector("#todoInput");
var todoList = document.querySelector("#todoList");
var summary = document.querySelector("#summary");
var filterButtons = document.querySelectorAll(".filter-button");
var quoteText = document.querySelector("#quoteText");
var quoteAuthor = document.querySelector("#quoteAuthor");

var todos = loadTodos();
var currentFilter = "all";

async function loadQuote() {
    try {
        var response = await fetch("https://dummyjson.com/quotes/random");

        if (!response.ok) {
            throw new Error("오늘의 한마디를 불러오지 못했습니다.");
        }

        var data = await response.json();
        quoteText.textContent = '"' + data.quote + '"';
        quoteAuthor.textContent = "- " + data.author;
    } catch (error) {
        quoteText.textContent = "하루하루는 성실하게, 인생 전체는 되는 대로";
        quoteAuthor.textContent = "- 이동진";
    }
}

function addTodo(text) {
    var todo = {
        id: Date.now(),
        text: text,
        done: false
    };

    todos.push(todo);
    saveTodos(todos);
    renderTodos();
}

function toggleTodo(id) {
    for (var i = 0; i < todos.length; i++) {
        if (todos[i].id === id) {
            todos[i].done = !todos[i].done;
        }
    }

    saveTodos(todos);
    renderTodos();
}

function deleteTodo(id) {
    todos = todos.filter(function (todo) {
        return todo.id !== id;
    });

    saveTodos(todos);
    renderTodos();
}

function getFilteredTodos() {
    if (currentFilter === "active") {
        return todos.filter(function (todo) {
            return todo.done === false;
        });
    }

    if (currentFilter === "done") {
        return todos.filter(function (todo) {
            return todo.done === true;
        });
    }

    return todos;
}

function updateSummary() {
    var doneCount = todos.filter(function (todo) {
        return todo.done === true;
    }).length;

    summary.textContent = "전체 " + todos.length + "개 · 완료 " + doneCount + "개";
}

function renderTodos() {
    var filteredTodos = getFilteredTodos();
    todoList.innerHTML = "";

    updateSummary();

    if (filteredTodos.length === 0) {
        var emptyMessage = document.createElement("li");
        emptyMessage.className = "empty-message";
        emptyMessage.textContent = "표시할 할 일이 없습니다.";
        todoList.appendChild(emptyMessage);
        return;
    }

    for (var i = 0; i < filteredTodos.length; i++) {
        var todo = filteredTodos[i];
        var item = document.createElement("li");
        var checkbox = document.createElement("input");
        var text = document.createElement("span");
        var deleteButton = document.createElement("button");

        item.className = "todo-item";
        item.dataset.id = todo.id;

        if (todo.done === true) {
            item.classList.add("done");
        }

        checkbox.type = "checkbox";
        checkbox.className = "todo-check";
        checkbox.checked = todo.done;

        text.className = "todo-text";
        text.textContent = todo.text;

        deleteButton.type = "button";
        deleteButton.className = "delete-button";
        deleteButton.textContent = "×";

        item.appendChild(checkbox);
        item.appendChild(text);
        item.appendChild(deleteButton);
        todoList.appendChild(item);
    }
}

todoForm.addEventListener("submit", function (event) {
    event.preventDefault();

    var todoText = todoInput.value.trim();

    if (todoText === "") {
        alert("할 일을 입력해주세요.");
        todoInput.focus();
        return;
    }

    addTodo(todoText);
    todoInput.value = "";
    todoInput.focus();
});

todoList.addEventListener("click", function (event) {
    var item = event.target.closest(".todo-item");

    if (item === null) {
        return;
    }

    var id = Number(item.dataset.id);

    if (event.target.classList.contains("todo-check")) {
        toggleTodo(id);
    }

    if (event.target.classList.contains("delete-button")) {
        deleteTodo(id);
    }
});

for (var i = 0; i < filterButtons.length; i++) {
    filterButtons[i].addEventListener("click", function (event) {
        currentFilter = event.target.dataset.filter;

        for (var j = 0; j < filterButtons.length; j++) {
            filterButtons[j].classList.remove("active");
        }

        event.target.classList.add("active");
        renderTodos();
    });
}

loadQuote();
renderTodos();
