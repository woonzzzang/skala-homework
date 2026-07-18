var STORAGE_KEY = "day2-todo-list";

export function loadTodos() {
    var savedTodos = localStorage.getItem(STORAGE_KEY);

    if (savedTodos === null) {
        return [];
    }

    return JSON.parse(savedTodos);
}

export function saveTodos(todos) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
}
