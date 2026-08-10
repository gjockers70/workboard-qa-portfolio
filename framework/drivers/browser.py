from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.remote.webdriver import WebDriver

from framework.config.settings import Settings


def common_arguments(headless: bool) -> list[str]:
    arguments = [
        "--window-size=1440,900",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-notifications",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    if headless:
        arguments.append("--headless=new")
    return arguments


def available_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as local_socket:
        local_socket.bind(("127.0.0.1", 0))
        return int(local_socket.getsockname()[1])


def wait_for_debugging_endpoint(port: int, process: subprocess.Popen[bytes]) -> None:
    endpoint = f"http://127.0.0.1:{port}/json/version"
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Brave exited before its automation endpoint was ready.")
        try:
            with urlopen(endpoint, timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, URLError):
            time.sleep(0.2)
    raise RuntimeError("Brave did not expose its automation endpoint within 10 seconds.")


def create_brave_driver(settings: Settings) -> WebDriver:
    if not settings.browser_binary or not Path(settings.browser_binary).is_file():
        raise FileNotFoundError(
            "Brave was selected but its executable was not found. "
            "Set WORKBOARD_BROWSER_BINARY to the Brave executable path."
        )

    port = available_local_port()
    profile_directory = Path(tempfile.mkdtemp(prefix="workboard-brave-"))
    command = [
        settings.browser_binary,
        *common_arguments(settings.headless),
        f"--remote-debugging-port={port}",
        "--remote-debugging-address=127.0.0.1",
        f"--user-data-dir={profile_directory}",
        "about:blank",
    ]
    creation_flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
    process = subprocess.Popen(command, creationflags=creation_flags)

    try:
        wait_for_debugging_endpoint(port, process)
        options = ChromeOptions()
        options.debugger_address = f"127.0.0.1:{port}"
        service = ChromeService(
            log_output=str(settings.reports_dir / "chromedriver.log"),
            service_args=["--verbose"],
        )
        driver = webdriver.Chrome(service=service, options=options)
    except Exception:
        process.terminate()
        process.wait(timeout=5)
        shutil.rmtree(profile_directory, ignore_errors=True)
        raise

    setattr(driver, "_workboard_brave_process", process)
    setattr(driver, "_workboard_brave_profile", profile_directory)
    return driver


def close_driver(driver: WebDriver) -> None:
    process = getattr(driver, "_workboard_brave_process", None)
    profile_directory = getattr(driver, "_workboard_brave_profile", None)
    try:
        if process is not None:
            try:
                driver.execute_cdp_cmd("Browser.close", {})
            except Exception:
                pass
        driver.quit()
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if profile_directory is not None:
            shutil.rmtree(profile_directory, ignore_errors=True)


def create_driver(settings: Settings) -> WebDriver:
    if settings.browser == "brave":
        driver = create_brave_driver(settings)
    elif settings.browser == "chrome":
        options = ChromeOptions()
        for argument in common_arguments(settings.headless):
            options.add_argument(argument)
        service = ChromeService(
            log_output=str(settings.reports_dir / "chromedriver.log"),
            service_args=["--verbose"],
        )
        driver = webdriver.Chrome(service=service, options=options)
    elif settings.browser == "edge":
        options = EdgeOptions()
        for argument in common_arguments(settings.headless):
            options.add_argument(argument)
        driver = webdriver.Edge(options=options)
    else:
        raise ValueError(f"Unsupported browser: {settings.browser}. Use brave, chrome, or edge.")

    driver.set_page_load_timeout(30)
    return driver
