from collections.abc import Mapping
from typing import Any

from sqlalchemy import Engine, text


class DatabaseInspector:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def foreign_keys_enabled(self) -> bool:
        with self.engine.connect() as connection:
            return connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1

    def user_count(self, *, email: str | None = None) -> int:
        statement = "SELECT COUNT(*) FROM users"
        parameters: dict[str, Any] = {}
        if email is not None:
            statement += " WHERE email = :email"
            parameters["email"] = email
        with self.engine.connect() as connection:
            return int(connection.execute(text(statement), parameters).scalar_one())

    def task_count(self, *, owner_id: int | None = None) -> int:
        statement = "SELECT COUNT(*) FROM tasks"
        parameters: dict[str, Any] = {}
        if owner_id is not None:
            statement += " WHERE owner_id = :owner_id"
            parameters["owner_id"] = owner_id
        with self.engine.connect() as connection:
            return int(connection.execute(text(statement), parameters).scalar_one())

    def user_by_email(self, email: str) -> Mapping[str, Any] | None:
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    "SELECT id, email, display_name, password_hash, role, created_at "
                    "FROM users WHERE email = :email"
                ),
                {"email": email},
            ).mappings().one_or_none()
        return row

    def task_by_id(self, task_id: int) -> Mapping[str, Any] | None:
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    "SELECT id, title, description, completed, owner_id, created_at, updated_at "
                    "FROM tasks WHERE id = :task_id"
                ),
                {"task_id": task_id},
            ).mappings().one_or_none()
        return row

    def task_ids_for_owner(self, owner_id: int) -> list[int]:
        with self.engine.connect() as connection:
            rows = connection.execute(
                text("SELECT id FROM tasks WHERE owner_id = :owner_id ORDER BY id"),
                {"owner_id": owner_id},
            ).scalars().all()
        return [int(task_id) for task_id in rows]

    def task_ids_for_search_and_state(self, owner_id: int, term: str, completed: bool) -> list[int]:
        with self.engine.connect() as connection:
            rows = connection.execute(
                text(
                    "SELECT id FROM tasks "
                    "WHERE owner_id = :owner_id "
                    "AND (LOWER(title) LIKE :term OR LOWER(description) LIKE :term) "
                    "AND completed = :completed ORDER BY created_at DESC"
                ),
                {
                    "owner_id": owner_id,
                    "term": f"%{term.lower()}%",
                    "completed": completed,
                },
            ).scalars().all()
        return [int(task_id) for task_id in rows]
