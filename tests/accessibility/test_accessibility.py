import json
from urllib.request import Request, urlopen
from uuid import uuid4

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from framework.accessibility.axe import format_violations, run_axe, violation_ids
from framework.config.settings import Settings
from framework.data.factories import SyntheticUser, synthetic_user
from framework.pages.login_page import LoginPage
from framework.pages.workspace_page import WorkspacePage


pytestmark = [pytest.mark.accessibility, pytest.mark.ui, pytest.mark.regression]
API_URL = "http://127.0.0.1:8000"


def register_user(user: SyntheticUser) -> dict[str, object]:
    request = Request(
        f"{API_URL}/api/auth/register",
        data=json.dumps(
            {"email": user.email, "display_name": user.display_name, "password": user.password}
        ).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        assert response.status == 201
        return json.loads(response.read())


def open_workspace(
    driver: WebDriver,
    settings: Settings,
    *,
    seeded: bool = False,
) -> WorkspacePage:
    user = synthetic_user()
    auth = register_user(user)
    target = settings.base_url + ("/?accessibility-defects=true" if seeded else "")
    driver.get(target)
    driver.execute_script(
        "localStorage.setItem('workboard-session', arguments[0])",
        json.dumps({"token": auth["access_token"], "user": auth["user"]}),
    )
    driver.refresh()
    return WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()


def assert_no_axe_violations(driver: WebDriver) -> dict[str, object]:
    results = run_axe(driver)
    assert results["violations"] == [], format_violations(results)
    return results


def test_signed_out_and_registration_views_have_no_axe_violations(
    driver: WebDriver,
    settings: Settings,
) -> None:
    login = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).load()
    assert_no_axe_violations(driver)
    login.switch_to_registration()
    assert_no_axe_violations(driver)


def test_member_workspace_states_have_no_axe_violations(
    driver: WebDriver,
    settings: Settings,
) -> None:
    workspace = open_workspace(driver, settings)
    assert_no_axe_violations(driver)
    workspace.create_task(f"Accessibility {uuid4().hex[:8]}", "Axe-expanded application state")
    assert_no_axe_violations(driver)


def test_seeded_baseline_is_detected_by_axe(driver: WebDriver, settings: Settings) -> None:
    workspace = open_workspace(driver, settings, seeded=True)
    workspace.create_task(f"Seeded finding {uuid4().hex[:8]}", "Controlled defect evidence")
    found = violation_ids(run_axe(driver))
    assert {"button-name", "color-contrast"}.issubset(found)


def test_corrected_controls_have_accessible_names_and_heading_order(
    driver: WebDriver,
    settings: Settings,
) -> None:
    workspace = open_workspace(driver, settings)
    title = f"Named control {uuid4().hex[:8]}"
    workspace.create_task(title, "Semantic structure")
    names = driver.execute_script(
        """
        return [...document.querySelectorAll('input, textarea, select, button')].map(element => ({
          testid: element.dataset.testid || '',
          name: element.getAttribute('aria-label')
            || element.closest('label')?.firstChild?.textContent?.trim()
            || element.textContent.trim()
        }));
        """
    )
    assert all(control["name"] for control in names)
    headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
    levels = [int(heading.tag_name[1]) for heading in headings]
    assert levels[0] == 1
    assert all(current - previous <= 1 for previous, current in zip(levels, levels[1:]))
    assert workspace.task_card(title).find_element(By.CSS_SELECTOR, "h2").text == title


def test_seeded_semantic_defects_remain_reproducible(driver: WebDriver, settings: Settings) -> None:
    workspace = open_workspace(driver, settings, seeded=True)
    title = f"Seeded semantics {uuid4().hex[:8]}"
    workspace.create_task(title, "Controlled semantic defect")
    card = workspace.task_card(title)
    assert card.find_element(By.CSS_SELECTOR, '[data-testid="task-delete"]').accessible_name == ""
    assert card.find_element(By.CSS_SELECTOR, "h3").text == title
    search = workspace.visible(workspace.TASK_SEARCH)
    assert driver.execute_script("return arguments[0].labels.length", search) == 0


def test_keyboard_focus_is_visible_and_not_obscured(driver: WebDriver, settings: Settings) -> None:
    workspace = open_workspace(driver, settings)
    target = workspace.visible(workspace.TASK_TITLE)
    target.click()
    target.send_keys(Keys.TAB)
    focused = driver.switch_to.active_element
    styles = driver.execute_script(
        """
        const s = getComputedStyle(arguments[0]);
        const r = arguments[0].getBoundingClientRect();
        return {outlineStyle: s.outlineStyle, outlineWidth: s.outlineWidth,
          boxShadow: s.boxShadow, top: r.top, bottom: r.bottom,
          viewportHeight: window.innerHeight};
        """,
        focused,
    )
    assert focused.get_attribute("data-testid") == "task-description"
    assert styles["outlineStyle"] != "none"
    assert styles["outlineWidth"] == "3px"
    assert styles["boxShadow"] != "none"
    assert styles["top"] >= 0 and styles["bottom"] <= styles["viewportHeight"]


def test_seeded_focus_defect_is_detectable(driver: WebDriver, settings: Settings) -> None:
    workspace = open_workspace(driver, settings, seeded=True)
    target = workspace.visible(workspace.TASK_TITLE)
    target.click()
    target.send_keys(Keys.TAB)
    focused = driver.switch_to.active_element
    styles = driver.execute_script(
        "const s=getComputedStyle(arguments[0]);return [s.outlineStyle,s.boxShadow]",
        focused,
    )
    assert styles == ["none", "none"]


def test_success_and_error_updates_use_live_region_roles(
    driver: WebDriver,
    settings: Settings,
) -> None:
    workspace = open_workspace(driver, settings)
    feedback = driver.find_element(*workspace.FEEDBACK)
    assert feedback.get_attribute("role") == "status"
    assert feedback.get_attribute("aria-atomic") == "true"
    assert feedback.text == ""
    workspace.create_task(f"Announcement {uuid4().hex[:8]}", "Live-region evidence")
    assert workspace.visible(workspace.FEEDBACK).get_attribute("role") == "status"
    workspace.fill(workspace.TASK_TITLE, " ")
    driver.execute_script("arguments[0].removeAttribute('required')", workspace.visible(workspace.TASK_TITLE))
    workspace.click(workspace.CREATE_TASK)
    workspace.wait_for_feedback("Check the submitted values")
    assert workspace.visible(workspace.FEEDBACK).get_attribute("role") == "alert"


def test_delete_confirmation_is_descriptive_and_restores_focus(
    driver: WebDriver,
    settings: Settings,
) -> None:
    workspace = open_workspace(driver, settings)
    title = f"Dialog review {uuid4().hex[:8]}"
    workspace.create_task(title, "Native confirmation semantics")
    delete = workspace.task_card(title).find_element(By.CSS_SELECTOR, '[data-testid="task-delete"]')
    delete.click()
    dialog = driver.switch_to.alert
    assert dialog.text == f'Delete "{title}"?'
    dialog.dismiss()
    assert workspace.has_task(title)
    assert driver.switch_to.active_element.get_attribute("data-testid") == "task-delete"


def test_workspace_reflows_without_horizontal_scrolling(
    driver: WebDriver,
    settings: Settings,
) -> None:
    driver.set_window_size(320, 900)
    workspace = open_workspace(driver, settings)
    assert driver.execute_script(
        "return document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )
    for locator in (
        workspace.TASK_TITLE,
        workspace.TASK_DESCRIPTION,
        workspace.CREATE_TASK,
        workspace.PROFILE_NAME,
        workspace.TASK_SEARCH,
        workspace.TASK_FILTER,
        workspace.SIGN_OUT,
    ):
        element = workspace.visible(locator)
        viewport_width = driver.execute_script("return document.documentElement.clientWidth")
        assert element.rect["x"] >= 0
        assert element.rect["x"] + element.rect["width"] <= viewport_width + 1
