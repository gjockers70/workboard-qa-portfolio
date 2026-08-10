from collections.abc import Generator
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from framework.config.settings import Settings, load_settings
from framework.data.factories import SyntheticUser, synthetic_user
from framework.drivers.browser import close_driver, create_driver
from framework.pages.login_page import LoginPage
from framework.pages.workspace_page import WorkspacePage
from framework.utilities.artifacts import save_failure_screenshot


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("workboard")
    group.addoption("--base-url", action="store", default=None, help="WorkBoard frontend URL")
    group.addoption("--browser", action="store", default=None, choices=("brave", "chrome", "edge"))
    group.addoption("--headed", action="store_true", default=False, help="Show the browser window")


def pytest_sessionstart(session: pytest.Session) -> None:
    settings = load_settings()
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.screenshots_dir.mkdir(parents=True, exist_ok=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"report_{report.when}", report)


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    return load_settings(
        base_url=pytestconfig.getoption("--base-url"),
        browser=pytestconfig.getoption("--browser"),
        headless=not pytestconfig.getoption("--headed"),
    )


@pytest.fixture
def driver(request: pytest.FixtureRequest, settings: Settings) -> Generator[WebDriver, None, None]:
    browser = create_driver(settings)
    try:
        yield browser
        report = getattr(request.node, "report_call", None)
        if report is not None and report.failed:
            save_failure_screenshot(browser, settings.screenshots_dir, request.node.nodeid)
    finally:
        close_driver(browser)


@pytest.fixture(scope="session")
def test_credentials(settings: Settings) -> tuple[str, str]:
    if not settings.test_user_email or not settings.test_user_password:
        pytest.skip("Set WORKBOARD_TEST_USER_EMAIL and WORKBOARD_TEST_USER_PASSWORD for authenticated UI tests.")
    return settings.test_user_email, settings.test_user_password


@pytest.fixture
def member_data() -> SyntheticUser:
    return synthetic_user()


@pytest.fixture
def registered_workspace(
    driver: WebDriver,
    settings: Settings,
    member_data: SyntheticUser,
) -> tuple[SyntheticUser, WorkspacePage]:
    login_page = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).load()
    login_page.register(member_data.display_name, member_data.email, member_data.password)
    workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
    return member_data, workspace
