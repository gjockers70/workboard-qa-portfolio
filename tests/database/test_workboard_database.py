from collections.abc import Mapping
from uuid import uuid4

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.backend.app.security import hash_password, verify_password
from framework.data.factories import SyntheticUser, synthetic_user


pytestmark = [pytest.mark.database, pytest.mark.integration]


def register_member(context, label: str = "member") -> tuple[SyntheticUser, str, int]:
    user = synthetic_user(label, phase="phase7")
    response = context.client.post(
        "/api/auth/register",
        json={"email": user.email, "display_name": user.display_name, "password": user.password},
    )
    assert response.status_code == 201
    body = response.json()
    return user, body["access_token"], body["user"]["id"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_task(
    context,
    token: str,
    title: str,
    description: str = "",
) -> Mapping[str, object]:
    response = context.client.post(
        "/api/tasks",
        headers=auth(token),
        json={"title": title, "description": description},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.contract
def test_schema_has_required_tables_constraints_and_indexes(database_context) -> None:
    """DB-SCHEMA-001: users/tasks expose the expected columns, uniqueness, index, and foreign key."""
    schema = inspect(database_context.engine)

    assert {"users", "tasks"}.issubset(schema.get_table_names())
    user_columns = {column["name"]: column for column in schema.get_columns("users")}
    task_columns = {column["name"]: column for column in schema.get_columns("tasks")}
    assert {"id", "email", "display_name", "password_hash", "role", "created_at"} == set(user_columns)
    assert {"id", "title", "description", "completed", "owner_id", "created_at", "updated_at"} == set(task_columns)
    assert all(not user_columns[name]["nullable"] for name in ("email", "display_name", "password_hash", "role"))
    assert all(not task_columns[name]["nullable"] for name in ("title", "description", "completed", "owner_id"))

    unique_columns = {
        tuple(constraint["column_names"])
        for constraint in schema.get_unique_constraints("users")
    }
    unique_indexes = {
        tuple(index["column_names"])
        for index in schema.get_indexes("users")
        if index.get("unique")
    }
    assert ("email",) in unique_columns | unique_indexes
    assert any(index["column_names"] == ["title"] for index in schema.get_indexes("tasks"))
    foreign_keys = schema.get_foreign_keys("tasks")
    assert any(
        key["constrained_columns"] == ["owner_id"]
        and key["referred_table"] == "users"
        and key["referred_columns"] == ["id"]
        for key in foreign_keys
    )


def test_registration_persists_normalized_user_and_salted_hash(database_context) -> None:
    """DB-USER-001: API registration inserts normalized identity data and never stores plaintext password."""
    user = synthetic_user("stored-user", phase="phase7")
    response = database_context.client.post(
        "/api/auth/register",
        json={
            "email": f"  {user.email.upper()}  ",
            "display_name": f"  {user.display_name}  ",
            "password": user.password,
        },
    )
    assert response.status_code == 201

    stored = database_context.inspector.user_by_email(user.email)
    assert stored is not None
    assert stored["email"] == user.email
    assert stored["display_name"] == user.display_name
    assert stored["role"] == "member"
    assert stored["created_at"] is not None
    assert stored["password_hash"] != user.password
    assert ":" in stored["password_hash"]
    assert verify_password(user.password, stored["password_hash"])


def test_duplicate_registration_leaves_row_count_unchanged(database_context) -> None:
    """DB-USER-002: normalized duplicate rejection creates no second row."""
    user, _, _ = register_member(database_context, "duplicate")
    before = database_context.inspector.user_count()

    duplicate = database_context.client.post(
        "/api/auth/register",
        json={"email": user.email.upper(), "display_name": "Duplicate", "password": user.password},
    )

    assert duplicate.status_code == 409
    assert database_context.inspector.user_count() == before
    assert database_context.inspector.user_count(email=user.email) == 1


def test_database_unique_constraint_rolls_back_duplicate_insert(database_context) -> None:
    """DB-USER-003: the database itself rejects an exact duplicate and remains usable after rollback."""
    email = f"phase7.direct.{uuid4().hex[:8]}@example.test"
    values = {
        "email": email,
        "display_name": "Direct Member",
        "password_hash": hash_password("Synthetic-Direct-Password!"),
        "role": "member",
    }
    insert = text(
        "INSERT INTO users (email, display_name, password_hash, role, created_at) "
        "VALUES (:email, :display_name, :password_hash, :role, CURRENT_TIMESTAMP)"
    )
    with database_context.sessions() as session:
        session.execute(insert, values)
        session.commit()
        with pytest.raises(IntegrityError):
            session.execute(insert, values)
            session.commit()
        session.rollback()

    assert database_context.inspector.user_count(email=email) == 1


@pytest.mark.parametrize("null_column", ["email", "display_name", "password_hash", "role"])
def test_required_user_columns_reject_null(database_context, null_column: str) -> None:
    """DB-USER-004: required user fields are protected by NOT NULL constraints."""
    values = {
        "email": f"phase7.null.{uuid4().hex[:8]}@example.test",
        "display_name": "Null Check",
        "password_hash": hash_password("Synthetic-Null-Password!"),
        "role": "member",
    }
    values[null_column] = None
    insert = text(
        "INSERT INTO users (email, display_name, password_hash, role, created_at) "
        "VALUES (:email, :display_name, :password_hash, :role, CURRENT_TIMESTAMP)"
    )
    with database_context.sessions() as session:
        with pytest.raises(IntegrityError):
            session.execute(insert, values)
            session.commit()
        session.rollback()

    assert database_context.inspector.user_count() == 0


def test_task_insert_defaults_transformations_and_owner(database_context) -> None:
    """DB-TASK-001: API creation inserts one owned row with trimmed values and persisted defaults."""
    _, token, user_id = register_member(database_context, "task-owner")
    before = database_context.inspector.task_count(owner_id=user_id)

    created = create_task(database_context, token, "  Stored task  ", "  Stored description  ")
    stored = database_context.inspector.task_by_id(int(created["id"]))

    assert stored is not None
    assert database_context.inspector.task_count(owner_id=user_id) == before + 1
    assert stored["title"] == "Stored task"
    assert stored["description"] == "Stored description"
    assert stored["completed"] in (False, 0)
    assert stored["owner_id"] == user_id
    assert stored["created_at"] is not None and stored["updated_at"] is not None


def test_profile_and_task_updates_match_database_state(database_context) -> None:
    """DB-TASK-002: PATCH responses and persisted profile/task values agree."""
    user, token, _ = register_member(database_context, "update-owner")
    task = create_task(database_context, token, "Before title", "Before description")
    updated_name = "Updated Database Member"
    profile_response = database_context.client.patch(
        "/api/profile",
        headers=auth(token),
        json={"display_name": updated_name},
    )
    task_response = database_context.client.patch(
        f"/api/tasks/{task['id']}",
        headers=auth(token),
        json={"title": "After title", "description": "After description", "completed": True},
    )

    assert profile_response.status_code == 200 and task_response.status_code == 200
    stored_user = database_context.inspector.user_by_email(user.email)
    stored_task = database_context.inspector.task_by_id(int(task["id"]))
    assert stored_user is not None and stored_user["display_name"] == updated_name
    assert stored_task is not None
    assert (stored_task["title"], stored_task["description"], bool(stored_task["completed"])) == (
        "After title",
        "After description",
        True,
    )
    assert task_response.json()["title"] == stored_task["title"]
    assert task_response.json()["description"] == stored_task["description"]
    assert task_response.json()["completed"] == bool(stored_task["completed"])


def test_task_delete_removes_exact_row_and_decrements_count(database_context) -> None:
    """DB-TASK-003: DELETE removes the target row and only one owned row."""
    _, token, owner_id = register_member(database_context, "delete-owner")
    retained = create_task(database_context, token, "Retained task")
    deleted = create_task(database_context, token, "Deleted task")
    before = database_context.inspector.task_count(owner_id=owner_id)

    response = database_context.client.delete(f"/api/tasks/{deleted['id']}", headers=auth(token))

    assert response.status_code == 204
    assert database_context.inspector.task_by_id(int(deleted["id"])) is None
    assert database_context.inspector.task_by_id(int(retained["id"])) is not None
    assert database_context.inspector.task_count(owner_id=owner_id) == before - 1


@pytest.mark.authorization
def test_unauthorized_update_and_delete_leave_database_unchanged(database_context) -> None:
    """DB-AUTHZ-001: rejected cross-owner mutations preserve values and row counts."""
    _, owner_token, owner_id = register_member(database_context, "owner")
    _, other_token, other_id = register_member(database_context, "other")
    task = create_task(database_context, owner_token, "Protected task", "Original value")
    task_id = int(task["id"])
    before = dict(database_context.inspector.task_by_id(task_id) or {})
    owner_count = database_context.inspector.task_count(owner_id=owner_id)
    other_count = database_context.inspector.task_count(owner_id=other_id)

    update = database_context.client.patch(
        f"/api/tasks/{task_id}",
        headers=auth(other_token),
        json={"title": "Unauthorized change", "completed": True},
    )
    delete = database_context.client.delete(f"/api/tasks/{task_id}", headers=auth(other_token))

    assert update.status_code == 404 and delete.status_code == 404
    assert dict(database_context.inspector.task_by_id(task_id) or {}) == before
    assert database_context.inspector.task_count(owner_id=owner_id) == owner_count
    assert database_context.inspector.task_count(owner_id=other_id) == other_count


def test_foreign_keys_are_enabled_and_orphan_task_is_rejected(database_context) -> None:
    """DB-INTEGRITY-001: SQLite foreign-key enforcement rejects an unknown owner."""
    assert database_context.inspector.foreign_keys_enabled()

    with database_context.sessions() as session:
        with pytest.raises(IntegrityError):
            session.execute(
                text(
                    "INSERT INTO tasks "
                    "(title, description, completed, owner_id, created_at, updated_at) "
                    "VALUES ('Orphan', '', 0, 999999, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                )
            )
            session.commit()
        session.rollback()

    assert database_context.inspector.task_count() == 0


def test_deleting_user_cascades_owned_tasks(database_context) -> None:
    """DB-INTEGRITY-002: deleting a user removes dependent tasks through ON DELETE CASCADE."""
    _, token, owner_id = register_member(database_context, "cascade-owner")
    first = create_task(database_context, token, "Cascade one")
    second = create_task(database_context, token, "Cascade two")
    assert database_context.inspector.task_count(owner_id=owner_id) == 2

    with database_context.sessions() as session:
        session.execute(text("DELETE FROM users WHERE id = :owner_id"), {"owner_id": owner_id})
        session.commit()

    assert database_context.inspector.user_count() == 0
    assert database_context.inspector.task_count(owner_id=owner_id) == 0
    assert database_context.inspector.task_by_id(int(first["id"])) is None
    assert database_context.inspector.task_by_id(int(second["id"])) is None


def test_api_search_filter_ids_match_sql_result_ids(database_context) -> None:
    """DB-INTEGRATION-001: API combined-filter results match an independent SQL query."""
    _, token, owner_id = register_member(database_context, "filter-owner")
    search_token = uuid4().hex[:8]
    active = create_task(database_context, token, f"Active {search_token}", "shared term")
    completed = create_task(database_context, token, f"Completed {search_token}", "shared term")
    create_task(database_context, token, "Different task", "not included")
    response = database_context.client.patch(
        f"/api/tasks/{completed['id']}",
        headers=auth(token),
        json={"completed": True},
    )
    assert response.status_code == 200

    api_response = database_context.client.get(
        "/api/tasks",
        headers=auth(token),
        params={"search": search_token.upper(), "state": "active"},
    )
    api_ids = [int(task["id"]) for task in api_response.json()]
    sql_ids = database_context.inspector.task_ids_for_search_and_state(
        owner_id,
        search_token,
        completed=False,
    )

    assert api_response.status_code == 200
    assert api_ids == sql_ids == [int(active["id"])]


def test_owner_row_counts_and_ids_remain_isolated(database_context) -> None:
    """DB-INTEGRATION-002: owner-specific SQL counts and identifiers do not overlap."""
    _, first_token, first_id = register_member(database_context, "first-owner")
    _, second_token, second_id = register_member(database_context, "second-owner")
    first_tasks = [
        create_task(database_context, first_token, "First one"),
        create_task(database_context, first_token, "First two"),
    ]
    second_task = create_task(database_context, second_token, "Second one")

    first_ids = database_context.inspector.task_ids_for_owner(first_id)
    second_ids = database_context.inspector.task_ids_for_owner(second_id)
    assert first_ids == sorted(int(task["id"]) for task in first_tasks)
    assert second_ids == [int(second_task["id"])]
    assert database_context.inspector.task_count(owner_id=first_id) == 2
    assert database_context.inspector.task_count(owner_id=second_id) == 1
    assert set(first_ids).isdisjoint(second_ids)
