from collections.abc import Generator
from dataclasses import dataclass
import os

import pytest

from framework.clients.contracts import AuthContract
from framework.clients.workboard_api import WorkBoardApi
from framework.data.factories import SyntheticUser, synthetic_user


@dataclass(frozen=True)
class ApiMember:
    user: SyntheticUser
    token: str
    user_id: int


@pytest.fixture(scope="session")
def api_client() -> Generator[WorkBoardApi, None, None]:
    with WorkBoardApi(os.environ.get("WORKBOARD_API_URL", "http://127.0.0.1:8000")) as client:
        yield client


@pytest.fixture
def api_member(api_client: WorkBoardApi) -> ApiMember:
    user = synthetic_user("api-member", phase="phase6")
    response = api_client.register(user.email, user.display_name, user.password)
    assert response.status_code == 201
    contract = AuthContract.model_validate(response.json())
    return ApiMember(user=user, token=contract.access_token, user_id=contract.user.id)


@pytest.fixture(scope="session")
def api_admin(api_client: WorkBoardApi) -> AuthContract:
    email = os.environ.get("WORKBOARD_TEST_USER_EMAIL")
    password = os.environ.get("WORKBOARD_TEST_USER_PASSWORD")
    if not email or not password:
        pytest.skip("Set synthetic administrator credentials for administrator API coverage.")
    response = api_client.login(email, password)
    assert response.status_code == 200
    contract = AuthContract.model_validate(response.json())
    assert contract.user.role == "admin"
    return contract
