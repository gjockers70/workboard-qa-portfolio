import pytest

from framework.config.settings import Settings
from framework.pages.login_page import LoginPage
from framework.pages.workspace_page import WorkspacePage


@pytest.mark.ui
@pytest.mark.smoke
def test_registered_user_can_sign_in(
    driver,
    settings: Settings,
    test_credentials: tuple[str, str],
) -> None:
    email, password = test_credentials
    login_page = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).load()

    assert login_page.heading == "Welcome back"
    login_page.sign_in(email, password)

    workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    assert workspace.heading in {"Your tasks", "Team tasks"}
    assert "·" in workspace.profile_summary
    assert "member" in workspace.profile_summary.lower() or "admin" in workspace.profile_summary.lower()
