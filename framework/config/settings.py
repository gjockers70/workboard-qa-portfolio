import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def environment_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    base_url: str
    browser: str
    browser_binary: str | None
    headless: bool
    explicit_wait_seconds: float
    test_user_email: str | None
    test_user_password: str | None
    reports_dir: Path
    screenshots_dir: Path


def load_settings(
    *,
    base_url: str | None = None,
    browser: str | None = None,
    headless: bool | None = None,
) -> Settings:
    reports_dir = PROJECT_ROOT / "reports"
    selected_browser = (browser or os.environ.get("WORKBOARD_BROWSER", "brave")).strip().lower()
    browser_binary = os.environ.get("WORKBOARD_BROWSER_BINARY")
    if selected_browser == "brave" and not browser_binary:
        browser_binary = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    return Settings(
        base_url=(base_url or os.environ.get("WORKBOARD_BASE_URL", "http://127.0.0.1:5173")).rstrip("/"),
        browser=selected_browser,
        browser_binary=browser_binary,
        headless=environment_flag("WORKBOARD_HEADLESS", True) if headless is None else headless,
        explicit_wait_seconds=float(os.environ.get("WORKBOARD_EXPLICIT_WAIT", "10")),
        test_user_email=os.environ.get("WORKBOARD_TEST_USER_EMAIL"),
        test_user_password=os.environ.get("WORKBOARD_TEST_USER_PASSWORD"),
        reports_dir=reports_dir,
        screenshots_dir=reports_dir / "screenshots",
    )
