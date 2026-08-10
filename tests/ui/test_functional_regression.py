import pytest

from framework.config.settings import Settings
from framework.data.factories import SyntheticUser, synthetic_task_title
from framework.pages.login_page import LoginPage
from framework.pages.workspace_page import WorkspacePage


pytestmark = [pytest.mark.ui, pytest.mark.functional]


@pytest.mark.smoke
def test_member_can_register_and_sign_out(
    driver,
    settings: Settings,
    registered_workspace: tuple[SyntheticUser, WorkspacePage],
) -> None:
    """TC-AUTH-001, TC-AUTH-006: registration creates a session and sign-out ends it."""
    member, workspace = registered_workspace
    assert member.display_name in workspace.profile_summary
    assert "member" in workspace.profile_summary.lower()

    workspace.sign_out()
    login_page = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    assert login_page.heading == "Welcome back"

    driver.refresh()
    assert login_page.wait_until_loaded().heading == "Welcome back"


@pytest.mark.negative
@pytest.mark.regression
def test_incorrect_password_does_not_create_session(
    driver,
    settings: Settings,
    registered_workspace: tuple[SyntheticUser, WorkspacePage],
) -> None:
    """TC-AUTH-004: incorrect credentials show a neutral error and retain signed-out state."""
    member, workspace = registered_workspace
    workspace.sign_out()
    login_page = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()

    login_page.sign_in(member.email, "Incorrect-Synthetic-Password!")

    login_page.wait_for_feedback("Invalid email or password")
    assert login_page.heading == "Welcome back"
    assert driver.execute_script("return localStorage.getItem('workboard-session')") is None


@pytest.mark.smoke
@pytest.mark.regression
def test_member_task_lifecycle(
    registered_workspace: tuple[SyntheticUser, WorkspacePage],
) -> None:
    """TC-TASK-001, 005–009: create, edit, toggle, cancel deletion, and delete."""
    _, workspace = registered_workspace
    original_title = synthetic_task_title("lifecycle")
    edited_title = synthetic_task_title("edited")

    workspace.create_task(original_title, "Initial synthetic description")
    assert workspace.task_description(original_title) == "Initial synthetic description"

    workspace.edit_task(original_title, edited_title, "Updated synthetic description")
    assert workspace.task_description(edited_title) == "Updated synthetic description"

    workspace.toggle_task(edited_title, "Task completed")
    assert "Reopen" in workspace.task_action_labels(edited_title)
    workspace.toggle_task(edited_title, "Task reopened")
    assert "Complete" in workspace.task_action_labels(edited_title)

    workspace.cancel_task_deletion(edited_title)
    assert workspace.has_task(edited_title)
    workspace.delete_task(edited_title)
    assert not workspace.has_task(edited_title)


@pytest.mark.negative
@pytest.mark.regression
def test_blank_task_title_is_rejected(
    registered_workspace: tuple[SyntheticUser, WorkspacePage],
) -> None:
    """TC-TASK-002: whitespace-only titles do not create task records."""
    _, workspace = registered_workspace

    workspace.fill(workspace.TASK_TITLE, "   ")
    workspace.fill(workspace.TASK_DESCRIPTION, "Should not be created")
    workspace.click(workspace.CREATE_TASK)

    workspace.wait_for_feedback("Check the submitted values")
    workspace.wait_for_titles(set())


@pytest.mark.regression
def test_search_and_status_filter_apply_together(
    registered_workspace: tuple[SyntheticUser, WorkspacePage],
) -> None:
    """TC-SEARCH-006: combined search and status criteria both constrain results."""
    _, workspace = registered_workspace
    search_token = synthetic_task_title("filter").split()[-1]
    completed_match = f"Completed match {search_token}"
    active_match = f"Active match {search_token}"
    active_other = synthetic_task_title("other")
    created_titles = {completed_match, active_match, active_other}

    try:
        for title in created_titles:
            workspace.create_task(title, f"Description for {title}")
        workspace.toggle_task(completed_match, "Task completed")

        workspace.set_search(search_token.lower())
        workspace.wait_for_titles({completed_match, active_match})
        workspace.set_filter("completed")
        workspace.wait_for_titles({completed_match})
    finally:
        workspace.set_filter("all")
        workspace.wait_for_titles({completed_match, active_match})
        workspace.set_search("")
        workspace.wait_for_titles(created_titles)
        for title in created_titles:
            if workspace.has_task(title):
                workspace.delete_task(title)


@pytest.mark.regression
def test_profile_name_persists_across_sessions(
    driver,
    settings: Settings,
    registered_workspace: tuple[SyntheticUser, WorkspacePage],
) -> None:
    """TC-PROFILE-001: a saved display name remains after sign-out and sign-in."""
    member, workspace = registered_workspace
    updated_name = f"Updated {member.display_name}"

    workspace.update_profile(updated_name)
    workspace.sign_out()
    login_page = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    login_page.sign_in(member.email, member.password)

    reloaded_workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    assert updated_name in reloaded_workspace.profile_summary


@pytest.mark.regression
def test_administrator_team_view_is_read_only_for_member_task(
    driver,
    settings: Settings,
    registered_workspace: tuple[SyntheticUser, WorkspacePage],
    test_credentials: tuple[str, str],
) -> None:
    """TC-ADMIN-001, 002: team view identifies owners and hides mutation controls."""
    member, member_workspace = registered_workspace
    task_title = synthetic_task_title("team-view")
    member_workspace.create_task(task_title, "Visible to administrator oversight")
    member_workspace.sign_out()

    admin_email, admin_password = test_credentials
    login_page = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    login_page.sign_in(admin_email, admin_password)
    admin_workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()

    try:
        admin_workspace.open_team_tasks()
        card = admin_workspace.task_card(task_title)
        assert member.email in card.text
        assert admin_workspace.task_action_labels(task_title) == set()
    finally:
        admin_workspace.sign_out()
        login_page.wait_until_loaded().sign_in(member.email, member.password)
        cleanup_workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
        if cleanup_workspace.has_task(task_title):
            cleanup_workspace.delete_task(task_title)
