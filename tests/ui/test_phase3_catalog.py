import json
from time import monotonic
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

import pytest
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from framework.config.settings import Settings
from framework.data.factories import SyntheticUser, synthetic_user
from framework.pages.login_page import LoginPage
from framework.pages.workspace_page import WorkspacePage


pytestmark = [pytest.mark.ui, pytest.mark.functional, pytest.mark.regression]
API_URL = "http://127.0.0.1:8000"


def api_request(
    method: str,
    path: str,
    payload: dict[str, object] | None = None,
    token: str | None = None,
) -> tuple[int, object | None]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(
        f"{API_URL}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=10) as response:
            body = response.read()
            return response.status, json.loads(body) if body else None
    except HTTPError as error:
        body = error.read()
        return error.code, json.loads(body) if body else None


def register_api(user: SyntheticUser) -> dict[str, object]:
    status, body = api_request(
        "POST",
        "/api/auth/register",
        {"email": user.email, "display_name": user.display_name, "password": user.password},
    )
    assert status == 201
    assert isinstance(body, dict)
    return body


def authenticated_workspace(
    driver: WebDriver,
    settings: Settings,
    user: SyntheticUser,
) -> WorkspacePage:
    auth = register_api(user)
    driver.get(settings.base_url)
    driver.execute_script(
        "localStorage.setItem('workboard-session', arguments[0])",
        json.dumps({"token": auth["access_token"], "user": auth["user"]}),
    )
    driver.refresh()
    return WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()


def wait_for_title_count(workspace: WorkspacePage, expected: int) -> None:
    workspace.wait.until(lambda _: len(workspace.task_titles()) == expected)


def tab_to_testid(driver: WebDriver, testid: str, limit: int = 30):
    for _ in range(limit):
        active = driver.switch_to.active_element
        if active.get_attribute("data-testid") == testid:
            return active
        active.send_keys(Keys.TAB)
    raise AssertionError(f"Keyboard focus did not reach {testid}")


def test_authentication_positive_and_negative_paths(driver: WebDriver, settings: Settings) -> None:
    """TC-AUTH-002, TC-AUTH-003, TC-AUTH-005."""
    user = synthetic_user()
    register_api(user)
    login = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).load()

    login.sign_in("unknown." + user.email, user.password)
    login.wait_for_feedback("Invalid email or password")
    assert login.heading == "Welcome back"

    login.sign_in(user.email, user.password)
    workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    assert user.display_name in workspace.profile_summary
    workspace.sign_out()

    login.wait_until_loaded().switch_to_registration()
    login.fill(login.DISPLAY_NAME, "Duplicate Member")
    login.fill(login.EMAIL, user.email.upper())
    login.fill(login.PASSWORD, user.password)
    login.click(login.SUBMIT)
    login.wait_for_feedback("Email is already registered")
    assert login.heading == "Create your account"


def test_invalid_session_recovers_to_sign_in(driver: WebDriver, settings: Settings) -> None:
    """TC-AUTH-007."""
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    workspace.driver.execute_script(
        "const s=JSON.parse(localStorage.getItem('workboard-session'));"
        "s.token='invalidated-session-token';"
        "localStorage.setItem('workboard-session', JSON.stringify(s));"
    )
    driver.refresh()
    login = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    login.wait_for_feedback("Your session expired. Please sign in again.")
    assert driver.execute_script("return localStorage.getItem('workboard-session')") is None


def test_blank_profile_name_is_rejected(driver: WebDriver, settings: Settings) -> None:
    """TC-PROFILE-002."""
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    original = workspace.profile_summary
    profile = workspace.visible(workspace.PROFILE_NAME)
    profile.clear()
    profile.send_keys(" ")
    workspace.click(workspace.SAVE_PROFILE)
    assert driver.execute_script("return arguments[0].matches(':invalid')", profile)
    driver.refresh()
    assert workspace.wait_until_loaded().profile_summary == original


def test_task_boundaries(driver: WebDriver, settings: Settings) -> None:
    """TC-TASK-003, TC-TASK-004."""
    user = synthetic_user()
    auth = register_api(user)
    token = str(auth["access_token"])
    valid_title = "T" * 120
    valid_description = "D" * 1000

    status, created = api_request(
        "POST", "/api/tasks", {"title": valid_title, "description": valid_description}, token
    )
    assert status == 201
    assert isinstance(created, dict)
    assert len(str(created["title"])) == 120
    assert len(str(created["description"])) == 1000

    for payload in (
        {"title": "T" * 121, "description": "valid"},
        {"title": "valid", "description": "D" * 1001},
    ):
        rejected_status, _ = api_request("POST", "/api/tasks", payload, token)
        assert rejected_status == 422

    status, tasks = api_request("GET", "/api/tasks?search=&state=all", token=token)
    assert status == 200
    assert isinstance(tasks, list) and len(tasks) == 1


def test_search_and_filter_catalog(driver: WebDriver, settings: Settings) -> None:
    """TC-SEARCH-001 through TC-SEARCH-005 and TC-SEARCH-007."""
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    token = uuid4().hex[:8]
    alpha = f"Alpha {token}"
    beta = f"Beta {token}"
    gamma = f"Gamma {token}"
    workspace.create_task(alpha, "first description")
    workspace.create_task(beta, f"Contains Needle-{token}")
    workspace.create_task(gamma, "third description")
    workspace.toggle_task(beta, "Task completed")

    workspace.set_search(alpha.upper())
    workspace.wait_for_titles({alpha})
    workspace.set_search(f"needle-{token}".lower())
    workspace.wait_for_titles({beta})
    workspace.set_search("no-match-value")
    workspace.wait_for_titles(set())

    workspace.set_search("")
    workspace.wait_for_titles({alpha, beta, gamma})
    workspace.set_filter("active")
    workspace.wait_for_titles({alpha, gamma})
    workspace.set_filter("completed")
    workspace.wait_for_titles({beta})
    workspace.set_filter("all")
    workspace.wait_for_titles({alpha, beta, gamma})


def test_member_authorization_and_data_isolation(driver: WebDriver, settings: Settings) -> None:
    """TC-ADMIN-003 and TC-AUTHZ-001."""
    first = synthetic_user()
    second = synthetic_user()
    first_auth = register_api(first)
    second_auth = register_api(second)
    first_token = str(first_auth["access_token"])
    second_token = str(second_auth["access_token"])

    _, first_task = api_request(
        "POST", "/api/tasks", {"title": "First member task", "description": "private"}, first_token
    )
    _, second_task = api_request(
        "POST", "/api/tasks", {"title": "Second member task", "description": "private"}, second_token
    )
    assert isinstance(first_task, dict) and isinstance(second_task, dict)

    status, first_tasks = api_request("GET", "/api/tasks?search=&state=all", token=first_token)
    assert status == 200
    assert [task["title"] for task in first_tasks] == ["First member task"]
    status, second_tasks = api_request("GET", "/api/tasks?search=&state=all", token=second_token)
    assert status == 200
    assert [task["title"] for task in second_tasks] == ["Second member task"]

    forbidden_status, _ = api_request("GET", "/api/admin/tasks", token=first_token)
    assert forbidden_status == 403
    hidden_update_status, _ = api_request(
        "PATCH", f"/api/tasks/{second_task['id']}", {"title": "Unauthorized change"}, first_token
    )
    assert hidden_update_status == 404

    workspace = authenticated_workspace(driver, settings, synthetic_user())
    assert not driver.find_elements(*workspace.TEAM_TASKS)


def test_administrator_personal_view_remains_owned_only(
    driver: WebDriver,
    settings: Settings,
    test_credentials: tuple[str, str],
) -> None:
    """TC-ADMIN-004."""
    member = synthetic_user()
    member_auth = register_api(member)
    api_request(
        "POST",
        "/api/tasks",
        {"title": "Member-only task", "description": "not an administrator task"},
        str(member_auth["access_token"]),
    )

    admin_email, admin_password = test_credentials
    login = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).load()
    login.sign_in(admin_email, admin_password)
    workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    own_title = f"Administrator task {uuid4().hex[:8]}"
    workspace.create_task(own_title, "owned by administrator")
    workspace.open_team_tasks()
    workspace.task_card("Member-only task")
    workspace.click(workspace.MY_TASKS)
    workspace.wait.until(lambda _: workspace.heading == "Your tasks")
    assert workspace.has_task(own_title)
    assert not workspace.has_task("Member-only task")
    assert workspace.task_action_labels(own_title) == {"Complete", "Edit", "Delete"}


def test_keyboard_navigation_and_visible_focus(driver: WebDriver, settings: Settings) -> None:
    """TC-ACCESS-001."""
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    title = tab_to_testid(driver, "task-title")
    title.send_keys("Keyboard workflow task")
    title.send_keys(Keys.TAB)
    description = driver.switch_to.active_element
    assert description.get_attribute("data-testid") == "task-description"
    description.send_keys("Created without pointer activation")
    description.send_keys(Keys.TAB)
    create = driver.switch_to.active_element
    assert create.get_attribute("data-testid") == "create-task"
    focus_style = driver.execute_script(
        "const s=getComputedStyle(arguments[0]); return [s.outlineStyle,s.outlineWidth,s.boxShadow]", create
    )
    assert focus_style[0] != "none" and focus_style[1] == "3px" and focus_style[2] != "none"
    create.send_keys(Keys.ENTER)
    workspace.wait_for_feedback("Task created")
    workspace.task_card("Keyboard workflow task")

    profile = tab_to_testid(driver, "profile-name")
    profile.send_keys(Keys.CONTROL, "a")
    profile.send_keys("Keyboard Member")
    save_profile = tab_to_testid(driver, "save-profile")
    save_profile.send_keys(Keys.ENTER)
    workspace.wait_for_feedback("Profile updated")

    search = tab_to_testid(driver, "task-search")
    search.send_keys("keyboard workflow")
    workspace.wait_for_titles({"Keyboard workflow task"})
    search.send_keys(Keys.TAB)
    assert driver.switch_to.active_element.get_attribute("data-testid") == "task-filter"
    toggle = tab_to_testid(driver, "task-toggle")
    toggle.send_keys(Keys.ENTER)
    workspace.wait_for_feedback("Task completed")

    task_filter = tab_to_testid(driver, "task-filter")
    task_filter.send_keys("Completed")
    workspace.wait_for_titles({"Keyboard workflow task"})
    delete = tab_to_testid(driver, "task-delete")
    delete.send_keys(Keys.ENTER)
    alert = driver.switch_to.alert
    assert "Keyboard workflow task" in alert.text
    alert.accept()
    workspace.wait_for_feedback("Task deleted")
    sign_out = tab_to_testid(driver, "sign-out")
    sign_out.send_keys(Keys.ENTER)
    assert LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded().heading == "Welcome back"


def test_semantics_and_live_feedback(driver: WebDriver, settings: Settings) -> None:
    """TC-ACCESS-002 semantic and announcement precheck."""
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    assert driver.find_element(By.CSS_SELECTOR, "header h1").get_attribute("tagName").lower() == "h1"
    labels = driver.execute_script(
        "return [...document.querySelectorAll('input,textarea,select,button')].map(e=>({"
        "name:e.getAttribute('aria-label')||e.closest('label')?.firstChild?.textContent?.trim()||e.textContent.trim(),"
        "tag:e.tagName.toLowerCase()}))"
    )
    assert labels and all(item["name"] for item in labels)
    workspace.create_task(f"Announcement {uuid4().hex[:8]}", "success feedback")
    assert workspace.visible(workspace.FEEDBACK).get_attribute("role") == "status"

    workspace.fill(workspace.TASK_TITLE, " ")
    driver.execute_script("arguments[0].removeAttribute('required')", workspace.visible(workspace.TASK_TITLE))
    workspace.click(workspace.CREATE_TASK)
    workspace.wait_for_feedback("Check the submitted values")
    assert workspace.visible(workspace.FEEDBACK).get_attribute("role") == "alert"


def test_component_and_text_contrast(driver: WebDriver, settings: Settings) -> None:
    """TC-ACCESS-003."""
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    measurements = driver.execute_script(
        "const rgb=c=>c.match(/\\d+/g).slice(0,3).map(Number);"
        "const lum=c=>{const v=rgb(c).map(x=>x/255).map(x=>x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4));"
        "return .2126*v[0]+.7152*v[1]+.0722*v[2]};"
        "const ratio=(a,b)=>{let x=lum(a),y=lum(b);if(x<y){const z=x;x=y;y=z}return (x+.05)/(y+.05)};"
        "const result=[];"
        "for(const e of document.querySelectorAll('button,input,textarea,select,.view-note,.task p,.alert')){"
        "const s=getComputedStyle(e);let bg=s.backgroundColor;"
        "if(bg==='rgba(0, 0, 0, 0)')bg='rgb(255, 255, 255)';"
        "result.push({tag:e.tagName,text:e.textContent.trim(),textRatio:ratio(s.color,bg),borderRatio:"
        "['INPUT','TEXTAREA','SELECT'].includes(e.tagName)?ratio(s.borderColor,'rgb(255, 255, 255)'):null});}"
        "return result;"
    )
    assert all(item["textRatio"] >= 4.5 for item in measurements if item["text"] or item["tag"] != "BUTTON")
    assert all(item["borderRatio"] is None or item["borderRatio"] >= 3 for item in measurements)
    title = workspace.visible(workspace.TASK_TITLE)
    title.send_keys(Keys.TAB, Keys.SHIFT, Keys.TAB)
    focus = driver.execute_script(
        "const s=getComputedStyle(arguments[0]);return {outline:s.outlineColor,width:s.outlineWidth,shadow:s.boxShadow}",
        title,
    )
    assert focus["width"] == "3px" and focus["shadow"] != "none"


@pytest.mark.parametrize("width", [320, 760, 1280])
def test_responsive_core_workflow(driver: WebDriver, settings: Settings, width: int) -> None:
    """TC-COMPAT-001."""
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": False},
    )
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    title = f"Responsive {width} {uuid4().hex[:6]}"
    workspace.create_task(title, "responsive check")
    assert workspace.has_task(title)
    assert driver.execute_script("return document.documentElement.scrollWidth <= document.documentElement.clientWidth")
    for locator in (
        workspace.TASK_TITLE,
        workspace.TASK_SEARCH,
        workspace.TASK_FILTER,
        workspace.PROFILE_NAME,
        workspace.SIGN_OUT,
    ):
        element = workspace.visible(locator)
        assert element.rect["x"] >= 0
        viewport_width = driver.execute_script("return document.documentElement.clientWidth")
        assert element.rect["x"] + element.rect["width"] <= viewport_width + 1


def test_refresh_preserves_session_without_duplicate_mutation(driver: WebDriver, settings: Settings) -> None:
    """TC-REMOTE-001."""
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    title = f"Refresh once {uuid4().hex[:8]}"
    workspace.create_task(title, "must remain singular")
    before = len(workspace.task_cards())
    driver.refresh()
    workspace.wait_until_loaded()
    assert len(workspace.task_cards()) == before
    assert sum(card.text.count(title) for card in workspace.task_cards()) == 1


def test_connection_interruption_has_no_false_success(driver: WebDriver, settings: Settings) -> None:
    """TC-REMOTE-002."""
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    title = f"Interrupted {uuid4().hex[:8]}"
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["http://127.0.0.1:8000/api/*"]})
    workspace.fill(workspace.TASK_TITLE, title)
    workspace.fill(workspace.TASK_DESCRIPTION, "must not be confirmed")
    workspace.click(workspace.CREATE_TASK)
    workspace.wait.until(lambda _: workspace.visible(workspace.FEEDBACK).text.strip() != "")
    assert workspace.visible(workspace.FEEDBACK).get_attribute("class").find("error") >= 0
    assert workspace.visible(workspace.FEEDBACK).text != "Task created"

    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": []})
    driver.refresh()
    workspace.wait_until_loaded()
    assert not workspace.has_task(title)
    assert "member" in workspace.profile_summary.lower()


def test_action_feedback_and_delete_confirmation(driver: WebDriver, settings: Settings) -> None:
    """TC-USABILITY-001."""
    workspace = authenticated_workspace(driver, settings, synthetic_user())
    title = f"Clarity {uuid4().hex[:8]}"
    workspace.create_task(title, "feedback review")
    assert workspace.task_action_labels(title) == {"Complete", "Edit", "Delete"}
    workspace.toggle_task(title, "Task completed")
    assert "Reopen" in workspace.task_action_labels(title)
    workspace.toggle_task(title, "Task reopened")

    workspace.task_card(title).find_element(By.CSS_SELECTOR, '[data-testid="task-delete"]').click()
    alert = driver.switch_to.alert
    assert alert.text == f'Delete "{title}"?'
    alert.dismiss()
    assert workspace.has_task(title)

    workspace.delete_task(title)
    assert not workspace.has_task(title)
