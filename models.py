# models.py
from typing import Any

# 실습에서는 간단히 메모리 딕셔너리를 DB 대신 사용합니다
todos_db: dict[int, dict[str, Any]] = {}
next_id: int = 1


def get_all_todos() -> list[dict[str, Any]]:
    return list(todos_db.values())


def get_todo(todo_id: int) -> dict[str, Any] | None:
    return todos_db.get(todo_id)


def create_todo(title: str, done: bool = False) -> dict[str, Any]:
    global next_id

    todo = {
        "id": next_id,
        "title": title,
        "done": done,
    }
    todos_db[next_id] = todo
    next_id += 1
    return todo


def update_todo(todo_id: int, title: str, done: bool) -> dict[str, Any] | None:
    todo = get_todo(todo_id)
    if todo is None:
        return None

    todo["title"] = title
    todo["done"] = done
    return todo


def delete_todo(todo_id: int) -> bool:
    if todo_id not in todos_db:
        return False

    del todos_db[todo_id]
    return True


def reset_todos() -> None:
    global next_id

    todos_db.clear()
    next_id = 1
