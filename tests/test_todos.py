import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app
from models import reset_todos


@pytest.fixture(autouse=True)
def clear_todos() -> None:
    reset_todos()


@pytest.fixture
def client() -> Any:
    return app.test_client()


def test_create_todo_success(client: Any) -> None:
    response = client.post(
        "/api/todos",
        json={"title": "Write tests", "done": False},
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 1,
        "title": "Write tests",
        "done": False,
    }


def test_create_todo_rejects_empty_title(client: Any) -> None:
    response = client.post("/api/todos", json={"title": "", "done": False})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_create_todo_defaults_missing_done_to_false(client: Any) -> None:
    response = client.post("/api/todos", json={"title": "No done field"})

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 1,
        "title": "No done field",
        "done": False,
    }


def test_create_todo_rejects_missing_title(client: Any) -> None:
    response = client.post("/api/todos", json={"done": False})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_create_todo_rejects_non_string_title(client: Any) -> None:
    response = client.post("/api/todos", json={"title": 123, "done": False})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_list_todos_success(client: Any) -> None:
    client.post("/api/todos", json={"title": "First", "done": False})
    client.post("/api/todos", json={"title": "Second", "done": True})

    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "title": "First", "done": False},
        {"id": 2, "title": "Second", "done": True},
    ]


def test_get_todo_success(client: Any) -> None:
    client.post("/api/todos", json={"title": "Read", "done": False})

    response = client.get("/api/todos/1")

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "title": "Read", "done": False}


def test_get_todo_not_found(client: Any) -> None:
    response = client.get("/api/todos/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found"}


def test_update_todo_success(client: Any) -> None:
    client.post("/api/todos", json={"title": "Draft", "done": False})

    response = client.put(
        "/api/todos/1",
        json={"title": "Published", "done": True},
    )

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "title": "Published", "done": True}


def test_update_todo_rejects_empty_title(client: Any) -> None:
    client.post("/api/todos", json={"title": "Draft", "done": False})

    response = client.put("/api/todos/1", json={"title": "", "done": True})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_update_todo_rejects_missing_title(client: Any) -> None:
    client.post("/api/todos", json={"title": "Draft", "done": False})

    response = client.put("/api/todos/1", json={"done": True})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_update_todo_rejects_non_string_title(client: Any) -> None:
    client.post("/api/todos", json={"title": "Draft", "done": False})

    response = client.put("/api/todos/1", json={"title": 123, "done": True})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_update_todo_not_found(client: Any) -> None:
    response = client.put(
        "/api/todos/999",
        json={"title": "Missing", "done": True},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found"}


def test_delete_todo_success(client: Any) -> None:
    client.post("/api/todos", json={"title": "Remove", "done": False})

    response = client.delete("/api/todos/1")

    assert response.status_code == 200
    assert response.get_json() == {"message": "Deleted"}
    assert client.get("/api/todos/1").status_code == 404


def test_delete_todo_not_found(client: Any) -> None:
    response = client.delete("/api/todos/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found"}
