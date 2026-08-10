import pytest

from framework.config.settings import Settings
from framework.data.factories import SyntheticUser, synthetic_task_title
from framework.pages.login_page import LoginPage
from framework.pages.workspace_page import WorkspacePage


pytestmark = [pytest.mark.ui, pytest.mark.functional, pytest.mark.uat]


def test_member_business_workflow_replay(
    driver,
    settings: Settings,
    registered_workspace: tuple[SyntheticUser, WorkspacePage],
) -> None:
    """Corroborate UAT-001 through UAT-004 and UAT-006 in Brave."""
    member, workspace = registered_workspace
    updated_name = f"Phase 11 {member.display_name}"
    lifecycle_title = synthetic_task_title("daily", phase="phase11")
    edited_title = synthetic_task_title("revised", phase="phase11")
    search_token = synthetic_task_title("find", phase="phase11").split()[-1]
    active_match = f"Active {search_token}"
    completed_match = f"Completed {search_token}"
    unrelated = synthetic_task_title("unrelated", phase="phase11")
    refresh_title = synthetic_task_title("refresh", phase="phase11")
    cleanup_titles = {edited_title, active_match, completed_match, unrelated, refresh_title}

    workspace.update_profile(updated_name)
    workspace.create_task(lifecycle_title, "Daily business work")
    workspace.edit_task(lifecycle_title, edited_title, "Revised business work")
    workspace.toggle_task(edited_title, "Task completed")
    workspace.toggle_task(edited_title, "Task reopened")
    workspace.cancel_task_deletion(edited_title)
    assert workspace.has_task(edited_title)

    for title in (active_match, completed_match, unrelated, refresh_title):
        workspace.create_task(title, f"Details for {title}")
    workspace.toggle_task(completed_match, "Task completed")

    workspace.set_search(search_token.lower())
    workspace.wait_for_titles({active_match, completed_match})
    workspace.set_filter("completed")
    workspace.wait_for_titles({completed_match})
    workspace.set_filter("all")
    workspace.set_search("")
    workspace.wait_for_titles(cleanup_titles)

    driver.refresh()
    workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    workspace.wait_for_titles(cleanup_titles)
    assert workspace.task_titles() == cleanup_titles
    assert len(workspace.task_cards()) == len(cleanup_titles)

    for title in cleanup_titles:
        if workspace.has_task(title):
            workspace.delete_task(title)

    workspace.sign_out()
    login_page = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    assert login_page.heading == "Welcome back"
    driver.refresh()
    assert login_page.wait_until_loaded().heading == "Welcome back"


def test_administrator_business_workflow_replay(
    driver,
    settings: Settings,
    registered_workspace: tuple[SyntheticUser, WorkspacePage],
    test_credentials: tuple[str, str],
) -> None:
    """Corroborate UAT-005 owner visibility and read-only team oversight."""
    member, member_workspace = registered_workspace
    team_title = synthetic_task_title("team", phase="phase11")
    member_workspace.create_task(team_title, "Member-owned team work")
    member_workspace.sign_out()

    admin_email, admin_password = test_credentials
    login_page = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    login_page.sign_in(admin_email, admin_password)
    admin_workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()

    try:
        admin_workspace.open_team_tasks()
        assert member.email in admin_workspace.task_card(team_title).text
        assert admin_workspace.task_action_labels(team_title) == set()
    finally:
        admin_workspace.sign_out()
        login_page.wait_until_loaded().sign_in(member.email, member.password)
        cleanup = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
        if cleanup.has_task(team_title):
            cleanup.delete_task(team_title)
