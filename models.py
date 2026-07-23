# models.py
from datetime import datetime
from typing import Optional

# 실습에서는 간단히 메모리 딕셔너리를 DB 대신 사용합니다
todos_db: dict = {}
next_id: int = 1

def get_all_todos() -> list:
    return list(todos_db.values())

def get_todo(todo_id: int) -> Optional[dict]:
    return todos_db.get(todo_id)