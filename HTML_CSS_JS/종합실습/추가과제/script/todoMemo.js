import { loadTodos, saveTodos } from "./todoStorage.js";

var memoList = document.querySelector("#todo-memo-list");
var addButton = document.querySelector("#todo-memo-add");
var memoForm = document.querySelector("#todo-memo-form");
var memoInput = document.querySelector("#todo-memo-input");
var todos = loadTodos();

function getActiveTodos() {
    return todos.filter(function (todo) {
        return todo.done === false;
    });
}

function renderMemo() {
    var activeTodos = getActiveTodos();
    memoList.innerHTML = "";

    if (activeTodos.length === 0) {
        var emptyMessage = document.createElement("li");
        emptyMessage.className = "todo-memo-empty";
        emptyMessage.textContent = "진행 중인 할 일이 없습니다.";
        memoList.appendChild(emptyMessage);
        return;
    }

    for (var i = 0; i < activeTodos.length; i++) {
        var todo = activeTodos[i];
        var item = document.createElement("li");
        var checkbox = document.createElement("input");
        var text = document.createElement("span");

        item.className = "todo-memo-item";
        item.dataset.id = todo.id;

        checkbox.type = "checkbox";
        checkbox.className = "todo-memo-check";
        checkbox.setAttribute("aria-label", todo.text + " 완료 처리");

        text.className = "todo-memo-text";
        text.textContent = todo.text;

        item.appendChild(checkbox);
        item.appendChild(text);
        memoList.appendChild(item);
    }
}

function addTodo(text) {
    todos.push({
        id: Date.now(),
        text: text,
        done: false
    });

    saveTodos(todos);
    renderMemo();
}

function completeTodo(id) {
    for (var i = 0; i < todos.length; i++) {
        if (todos[i].id === id) {
            todos[i].done = true;
        }
    }

    saveTodos(todos);
    renderMemo();
}

addButton.addEventListener("click", function () {
    var willOpen = memoForm.hidden;

    memoForm.hidden = !willOpen;
    addButton.setAttribute("aria-expanded", String(willOpen));
    addButton.textContent = willOpen ? "−" : "+";

    if (willOpen) {
        memoInput.focus();
    }
});

memoForm.addEventListener("submit", function (event) {
    event.preventDefault();

    var todoText = memoInput.value.trim();

    if (todoText === "") {
        memoInput.focus();
        return;
    }

    addTodo(todoText);
    memoInput.value = "";
    memoInput.focus();
});

memoList.addEventListener("change", function (event) {
    if (!event.target.classList.contains("todo-memo-check")) {
        return;
    }

    var item = event.target.closest(".todo-memo-item");
    completeTodo(Number(item.dataset.id));
});

window.addEventListener("storage", function (event) {
    if (event.key === "day2-todo-list") {
        todos = loadTodos();
        renderMemo();
    }
});

window.addEventListener("pageshow", function () {
    todos = loadTodos();
    renderMemo();
});

renderMemo();
