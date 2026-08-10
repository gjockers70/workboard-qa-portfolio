from uuid import uuid4

import httpx
from pydantic import TypeAdapter
import pytest

from framework.clients.contracts import (
    AdminTaskContract,
    AuthContract,
    HealthContract,
    TaskContract,
    UserContract,
)
from framework.clients.workboard_api import ApiResponseError, WorkBoardApi
from framework.data.factories import synthetic_task_title, synthetic_user


pytestmark = [pytest.mark.api, pytest.mark.functional]
task_list_contract = TypeAdapter(list[TaskContract])
admin_task_list_contract = TypeAdapter(list[AdminTaskContract])


@pytest.mark.smoke
@pytest.mark.contract
def test_health_contract_and_single_request_timing(api_client: WorkBoardApi) -> None:
    """API-HEALTH-001: service health uses the expected contract and responds promptly locally."""
    response = api_client.health()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert HealthContract.model_validate(response.json()).status == "ok"
    assert response.elapsed.total_seconds() < 1.0


@pytest.mark.smoke
@pytest.mark.contract
def test_registration_normalizes_email_and_returns_auth_contract(api_client: WorkBoardApi) -> None:
    """API-AUTH-001: POST registration returns 201, a bearer token, and normalized user data."""
    user = synthetic_user("registration", phase="phase6")
    response = api_client.register(f"  {user.email.upper()}  ", user.display_name, user.password)

    assert response.status_code == 201
    contract = AuthContract.model_validate(response.json())
    assert contract.token_type == "bearer"
    assert contract.access_token
    assert contract.user.email == user.email
    assert contract.user.display_name == user.display_name
    assert contract.user.role == "member"


@pytest.mark.negative
def test_duplicate_registration_returns_conflict(api_client: WorkBoardApi) -> None:
    """API-AUTH-002: duplicate normalized email returns 409."""
    user = synthetic_user("duplicate", phase="phase6")
    assert api_client.register(user.email, user.display_name, user.password).status_code == 201

    duplicate = api_client.register(user.email.upper(), "Duplicate Name", user.password)

    assert duplicate.status_code == 409
    assert duplicate.json() == {"detail": "Email is already registered"}


@pytest.mark.contract
def test_login_returns_auth_contract(api_client: WorkBoardApi) -> None:
    """API-AUTH-003: valid POST login returns the authenticated member contract."""
    user = synthetic_user("login", phase="phase6")
    api_client.register(user.email, user.display_name, user.password)

    response = api_client.login(user.email.upper(), user.password)

    assert response.status_code == 200
    contract = AuthContract.model_validate(response.json())
    assert contract.user.email == user.email
    assert contract.access_token


@pytest.mark.negative
@pytest.mark.parametrize("identity", ["incorrect-password", "unknown-email"])
def test_invalid_credentials_share_neutral_error(api_client: WorkBoardApi, identity: str) -> None:
    """API-AUTH-004/005: incorrect and unknown credentials both return the same 401 response."""
    user = synthetic_user(identity, phase="phase6")
    password = user.password
    if identity == "incorrect-password":
        api_client.register(user.email, user.display_name, password)
        password = "Incorrect-Synthetic-Password!"

    response = api_client.login(user.email, password)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


@pytest.mark.negative
@pytest.mark.parametrize("token", [None, "invalid-token"])
def test_protected_endpoint_rejects_missing_or_invalid_token(api_client: WorkBoardApi, token: str | None) -> None:
    """API-AUTHZ-001: protected GET requests return 401 without task content."""
    response = api_client.tasks(token)

    assert response.status_code == 401
    assert "detail" in response.json()
    assert "title" not in response.text


@pytest.mark.contract
def test_profile_get_patch_and_validation(api_client: WorkBoardApi, api_member) -> None:
    """API-PROFILE-001/002: GET/PATCH persist valid data and reject invalid payloads."""
    profile = api_client.profile(api_member.token)
    assert profile.status_code == 200
    assert UserContract.model_validate(profile.json()).id == api_member.user_id

    updated_name = f"Updated API Member {uuid4().hex[:6]}"
    updated = api_client.update_profile(api_member.token, updated_name)
    assert updated.status_code == 200
    assert UserContract.model_validate(updated.json()).display_name == updated_name
    assert UserContract.model_validate(api_client.profile(api_member.token).json()).display_name == updated_name

    for invalid_name in (" ", ["incorrect", "type"]):
        rejected = api_client.update_profile(api_member.token, invalid_name)
        assert rejected.status_code == 422


@pytest.mark.smoke
@pytest.mark.contract
def test_task_crud_contract(api_client: WorkBoardApi, api_member) -> None:
    """API-TASK-001: POST, GET, PATCH, and DELETE complete the owned-task lifecycle."""
    title = synthetic_task_title("API lifecycle", phase="phase6")
    created = api_client.create_task(api_member.token, title, "Created through the service")
    assert created.status_code == 201
    task = TaskContract.model_validate(created.json())
    assert task.title == title and task.owner_id == api_member.user_id and task.completed is False

    listed = task_list_contract.validate_python(api_client.tasks(api_member.token).json())
    assert any(item.id == task.id for item in listed)

    updated_title = synthetic_task_title("API updated", phase="phase6")
    updated = api_client.update_task(
        api_member.token,
        task.id,
        title=updated_title,
        description="Updated through PATCH",
        completed=True,
    )
    updated_task = TaskContract.model_validate(updated.json())
    assert updated.status_code == 200
    assert (updated_task.title, updated_task.description, updated_task.completed) == (
        updated_title,
        "Updated through PATCH",
        True,
    )

    deleted = api_client.delete_task(api_member.token, task.id)
    assert deleted.status_code == 204 and deleted.content == b""
    assert all(item.id != task.id for item in task_list_contract.validate_python(api_client.tasks(api_member.token).json()))


@pytest.mark.negative
@pytest.mark.parametrize(
    ("title", "description"),
    [
        (None, "missing title"),
        (" ", "blank title"),
        ("T" * 121, "overlong title"),
        ("Valid title", "D" * 1001),
        (["incorrect", "type"], "invalid title type"),
        ("Valid title", ["incorrect", "type"]),
    ],
)
def test_create_task_rejects_invalid_payloads(
    api_client: WorkBoardApi,
    api_member,
    title: object,
    description: object,
) -> None:
    """API-TASK-002: missing, boundary, and incorrect-type payloads return 422."""
    response = api_client.create_task(api_member.token, title, description)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


@pytest.mark.negative
@pytest.mark.parametrize(
    ("search", "state"),
    [("S" * 121, "all"), ("", "archived")],
)
def test_task_query_rejects_invalid_parameters(
    api_client: WorkBoardApi,
    api_member,
    search: str,
    state: str,
) -> None:
    """API-TASK-003: invalid query values return 422 instead of broad results."""
    response = api_client.tasks(api_member.token, search=search, state=state)

    assert response.status_code == 422


@pytest.mark.contract
def test_search_and_state_filters_apply_together(api_client: WorkBoardApi, api_member) -> None:
    """API-TASK-004: GET search and state filters constrain the same result set."""
    token = uuid4().hex[:8]
    active_title = f"Active match {token}"
    completed_title = f"Completed match {token}"
    other_title = f"Other task {uuid4().hex[:8]}"
    active = TaskContract.model_validate(api_client.create_task(api_member.token, active_title, "shared").json())
    completed = TaskContract.model_validate(api_client.create_task(api_member.token, completed_title, "shared").json())
    api_client.create_task(api_member.token, other_title, "different")
    api_client.update_task(api_member.token, completed.id, completed=True)

    active_results = task_list_contract.validate_python(
        api_client.tasks(api_member.token, search=token.lower(), state="active").json()
    )
    completed_results = task_list_contract.validate_python(
        api_client.tasks(api_member.token, search=token.upper(), state="completed").json()
    )

    assert [item.id for item in active_results] == [active.id]
    assert [item.id for item in completed_results] == [completed.id]


@pytest.mark.authorization
def test_member_cannot_mutate_another_members_task(api_client: WorkBoardApi) -> None:
    """API-AUTHZ-002: another member's task is absent and update/delete return 404."""
    owner_user = synthetic_user("owner", phase="phase6")
    other_user = synthetic_user("other", phase="phase6")
    owner = AuthContract.model_validate(
        api_client.register(owner_user.email, owner_user.display_name, owner_user.password).json()
    )
    other = AuthContract.model_validate(
        api_client.register(other_user.email, other_user.display_name, other_user.password).json()
    )
    task = TaskContract.model_validate(api_client.create_task(owner.access_token, "Owner task", "private").json())

    assert task_list_contract.validate_python(api_client.tasks(other.access_token).json()) == []
    assert api_client.update_task(other.access_token, task.id, title="Unauthorized").status_code == 404
    assert api_client.delete_task(other.access_token, task.id).status_code == 404
    assert any(item.id == task.id for item in task_list_contract.validate_python(api_client.tasks(owner.access_token).json()))


@pytest.mark.authorization
def test_member_cannot_access_administrator_endpoint(api_client: WorkBoardApi, api_member) -> None:
    """API-ADMIN-001: a member receives 403 from team oversight."""
    response = api_client.all_tasks(api_member.token)

    assert response.status_code == 403
    assert response.json() == {"detail": "Administrator access required"}


@pytest.mark.authorization
@pytest.mark.contract
def test_administrator_team_contract_includes_owner_identity(
    api_client: WorkBoardApi,
    api_member,
    api_admin: AuthContract,
) -> None:
    """API-ADMIN-002: administrator GET includes owner fields for a member task."""
    title = synthetic_task_title("admin visibility", phase="phase6")
    created = TaskContract.model_validate(api_client.create_task(api_member.token, title, "team visibility").json())

    response = api_client.all_tasks(api_admin.access_token)

    assert response.status_code == 200
    tasks = admin_task_list_contract.validate_python(response.json())
    visible = next(item for item in tasks if item.id == created.id)
    assert visible.owner_id == api_member.user_id
    assert visible.owner_email == api_member.user.email
    assert visible.owner_name == api_member.user.display_name


def test_authenticated_read_single_request_timing(api_client: WorkBoardApi, api_member) -> None:
    """API-PERF-OBS-001: one local authenticated read is observed without claiming load capacity."""
    response = api_client.tasks(api_member.token)

    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 1.0


@pytest.mark.negative
def test_client_exposes_controlled_server_error() -> None:
    """API-ERROR-001: a simulated 5xx response becomes a typed client error."""
    def unavailable(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"detail": "Service temporarily unavailable"}, request=request)

    with WorkBoardApi("http://workboard.test", transport=httpx.MockTransport(unavailable)) as client:
        response = client.health()
        with pytest.raises(ApiResponseError) as captured:
            client.require_success(response)

    assert captured.value.status_code == 503
    assert captured.value.detail == "Service temporarily unavailable"
