import re
from datetime import datetime, timezone
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return cleaned or "unnamed-test"


def save_failure_screenshot(driver: WebDriver, directory: Path, test_name: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = directory / f"{safe_name(test_name)}_{timestamp}.png"
    driver.save_screenshot(str(destination))
    return destination

