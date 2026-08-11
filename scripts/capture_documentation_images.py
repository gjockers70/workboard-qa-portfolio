from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
from typing import Iterator
from urllib.error import URLError
from urllib.request import urlopen
from uuid import uuid4
import zlib


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"
FRONTEND = ROOT / "app" / "frontend"
IMAGES = ROOT / "docs" / "images"
WORKSPACE_IMAGE = IMAGES / "workboard-workspace.png"
REPORT_IMAGE = IMAGES / "pytest-html-report.png"
PYTEST_REPORT = ROOT / "reports" / "pytest-report.html"
CAPTURE_REPORTS = ROOT / "reports" / "documentation-capture"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from selenium.webdriver.remote.webdriver import WebDriver

from framework.config.settings import Settings, load_settings
from framework.data.factories import SyntheticUser
from framework.drivers.browser import close_driver, create_driver
from framework.pages.login_page import LoginPage
from framework.pages.workspace_page import WorkspacePage


def port_is_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        return probe.connect_ex(("127.0.0.1", port)) == 0


def ensure_port_available(port: int) -> None:
    if port_is_in_use(port):
        raise RuntimeError(f"Port {port} is already in use. Stop that exact local service and retry.")


def wait_until_ports_released(*ports: int) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if not any(port_is_in_use(port) for port in ports):
            return
        time.sleep(0.1)
    active = [str(port) for port in ports if port_is_in_use(port)]
    raise RuntimeError(f"Documentation services did not release port(s): {', '.join(active)}")


def wait_until_ready(url: str, processes: tuple[subprocess.Popen[str], ...]) -> None:
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        for process in processes:
            if process.poll() is not None:
                raise RuntimeError(f"A documentation service exited with code {process.returncode}.")
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, URLError):
            time.sleep(0.25)
    raise TimeoutError(f"{url} did not become ready within 25 seconds.")


def stop_process(process: subprocess.Popen[str] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def cleanup_services(frontend: subprocess.Popen[str] | None, backend: subprocess.Popen[str] | None) -> None:
    errors: list[Exception] = []
    for process in (frontend, backend):
        try:
            stop_process(process)
        except Exception as reason:
            errors.append(reason)
    time.sleep(0.25)
    try:
        wait_until_ports_released(8000, 5173)
    except Exception as reason:
        errors.append(reason)
    if errors:
        raise RuntimeError("Documentation service cleanup did not complete safely.") from errors[0]


@contextmanager
def local_application() -> Iterator[None]:
    ensure_port_available(8000)
    ensure_port_available(5173)
    node = shutil.which("node")
    vite = FRONTEND / "node_modules" / "vite" / "bin" / "vite.js"
    if not node or not vite.is_file():
        raise FileNotFoundError("Run npm ci --prefix app/frontend before capturing the workspace image.")

    creation_flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
    CAPTURE_REPORTS.mkdir(parents=True, exist_ok=True)
    backend: subprocess.Popen[str] | None = None
    frontend: subprocess.Popen[str] | None = None

    with tempfile.TemporaryDirectory(prefix="workboard-docs-", ignore_cleanup_errors=True) as temp_name:
        temp_dir = Path(temp_name)
        environment = os.environ.copy()
        environment["WORKBOARD_DATABASE_URL"] = f"sqlite:///{(temp_dir / 'workboard.db').as_posix()}"
        environment["WORKBOARD_SEEDED_FUNCTIONAL_DEFECTS"] = "false"
        environment["VITE_SEEDED_ACCESSIBILITY_DEFECTS"] = "false"

        backend_log_path = CAPTURE_REPORTS / "backend.log"
        frontend_log_path = CAPTURE_REPORTS / "frontend.log"
        with backend_log_path.open("w", encoding="utf-8") as backend_log, frontend_log_path.open(
            "w", encoding="utf-8"
        ) as frontend_log:
            try:
                backend = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "uvicorn",
                        "app.main:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8000",
                    ],
                    cwd=BACKEND,
                    env=environment,
                    stdout=backend_log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=creation_flags,
                )
                frontend = subprocess.Popen(
                    [
                        node,
                        str(vite),
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "5173",
                        "--strictPort",
                    ],
                    cwd=FRONTEND,
                    env=environment,
                    stdout=frontend_log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=creation_flags,
                )
                processes = (backend, frontend)
                try:
                    wait_until_ready("http://127.0.0.1:8000/health", processes)
                    wait_until_ready("http://127.0.0.1:5173/", processes)
                except Exception as reason:
                    raise RuntimeError(
                        f"Documentation services did not become ready. Review {backend_log_path} and {frontend_log_path}."
                    ) from reason
                yield
            finally:
                original_error = sys.exception()
                try:
                    cleanup_services(frontend, backend)
                except Exception as cleanup_error:
                    if original_error is None:
                        raise
                    original_error.add_note(f"Cleanup warning: {cleanup_error}")


def new_driver() -> tuple[Settings, WebDriver]:
    settings = load_settings(base_url="http://127.0.0.1:5173", browser="brave", headless=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.screenshots_dir.mkdir(parents=True, exist_ok=True)
    driver = create_driver(settings)
    try:
        driver.set_window_size(1440, 1000)
    except Exception:
        close_driver(driver)
        raise
    return settings, driver


def validate_png(path: Path) -> None:
    payload = path.read_bytes()
    if not payload.startswith(b"\x89PNG\r\n\x1a\n") or len(payload) < 24:
        raise RuntimeError(f"{path} is not a valid PNG image.")
    width, height = struct.unpack(">II", payload[16:24])
    if width < 1200 or height < 700:
        raise RuntimeError(f"{path} is too small for the README preview: {width}x{height}.")
    offset = 8
    chunk_index = 0
    found_end = False
    while offset < len(payload):
        if offset + 12 > len(payload):
            raise RuntimeError(f"{path} contains a truncated PNG chunk.")
        chunk_length = struct.unpack(">I", payload[offset:offset + 4])[0]
        chunk_type = payload[offset + 4:offset + 8]
        chunk_end = offset + chunk_length + 12
        if chunk_end > len(payload):
            raise RuntimeError(f"{path} contains an out-of-bounds PNG chunk.")
        if chunk_index == 0 and chunk_type != b"IHDR":
            raise RuntimeError(f"{path} does not begin with a PNG IHDR chunk.")
        chunk_data = payload[offset + 8:offset + 8 + chunk_length]
        expected_crc = struct.unpack(">I", payload[offset + 8 + chunk_length:chunk_end])[0]
        if zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF != expected_crc:
            raise RuntimeError(f"{path} contains an invalid PNG chunk checksum.")
        offset = chunk_end
        chunk_index += 1
        if chunk_type == b"IEND":
            found_end = True
            break
    if not found_end or offset != len(payload):
        raise RuntimeError(f"{path} does not end cleanly at its PNG IEND chunk.")


def report_summary(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    patterns = {
        "passed": r'class="passed">(\d+) Passed',
        "failed": r'class="failed">(\d+) Failed',
        "skipped": r'class="skipped">(\d+) Skipped',
        "xfailed": r'class="xfailed">(\d+) Expected failures?',
        "xpassed": r'class="xpassed">(\d+) Unexpected passes?',
        "errors": r'class="error">(\d+) Errors?',
        "reruns": r'class="rerun">(\d+) Reruns?',
        "retried": r'class="retried">(\d+) Retried',
    }
    required_labels = {"errors", "failed", "passed", "skipped", "xfailed", "xpassed"}
    summary: dict[str, int] = {}
    for label, pattern in patterns.items():
        match = re.search(pattern, text)
        if match is None and label in required_labels:
            raise RuntimeError(f"The pytest HTML report is missing its {label} result counter.")
        summary[label] = int(match.group(1)) if match else 0
    if "pytest" not in text.lower() or summary["passed"] < 1:
        raise RuntimeError("The selected file is not a completed pytest HTML report.")
    return summary


def validate_report(path: Path, expected_tests: int) -> dict[str, int]:
    if expected_tests < 1:
        raise ValueError("Expected test count must be positive.")
    if not path.is_file():
        raise FileNotFoundError("Run the complete pytest suite before capturing the HTML report image.")
    text = path.read_text(encoding="utf-8")
    summary = report_summary(path)
    nonpassing = sum(value for label, value in summary.items() if label != "passed")
    run_count = re.search(r'<p class="run-count">(\d+) tests took', text)
    if summary["passed"] != expected_tests or nonpassing or run_count is None or int(run_count.group(1)) != expected_tests:
        raise RuntimeError(
            f"The current report is not the expected {expected_tests}-test all-pass, no-skip result: {summary}."
        )
    if re.search(r"[A-Za-z]:[\\/]+Users[\\/]", text, re.I):
        raise RuntimeError("The report contains a personal machine path and cannot be published.")
    email_addresses = re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)
    if any(not address.lower().endswith("@example.test") for address in email_addresses):
        raise RuntimeError("The report contains a non-synthetic email address and cannot be published.")
    return summary


def capture_workspace(output: Path) -> None:
    with local_application():
        settings, driver = new_driver()
        try:
            token = uuid4().hex[:10]
            member = SyntheticUser(
                display_name="Portfolio Member",
                email=f"portfolio.member.{token}@example.test",
                password=f"Synthetic-{token}!",
            )
            login_page = LoginPage(driver, settings.base_url, settings.explicit_wait_seconds).load()
            login_page.register(member.display_name, member.email, member.password)
            workspace = WorkspacePage(driver, settings.base_url, settings.explicit_wait_seconds).wait_until_loaded()
            workspace.create_task("Review release checklist", "Confirm evidence and approval status.")
            workspace.create_task("Retest corrected finding", "Run focused checks and the affected regression set.")
            workspace.toggle_task("Retest corrected finding", "Task completed")
            workspace.create_task("Prepare sprint test summary", "Record scope, results, risks, and recommendation.")
            if not driver.save_screenshot(str(output)):
                raise RuntimeError("The browser did not save the workspace image.")
        finally:
            close_driver(driver)
    validate_png(output)


def capture_report(output: Path, expected_tests: int) -> None:
    validate_report(PYTEST_REPORT, expected_tests)
    _, driver = new_driver()
    try:
        driver.get(PYTEST_REPORT.resolve().as_uri())
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and "pytest" not in driver.title.lower():
            time.sleep(0.1)
        if "pytest" not in driver.page_source.lower():
            raise RuntimeError("The selected file does not appear to be a pytest HTML report.")
        if not driver.save_screenshot(str(output)):
            raise RuntimeError("The browser did not save the report image.")
    finally:
        close_driver(driver)
    validate_png(output)


def promote_assets(staged: list[tuple[Path, Path]], staging: Path) -> None:
    backups: dict[Path, Path] = {}
    promoted: list[Path] = []
    for _, destination in staged:
        if destination.is_file():
            backup = staging / f"{destination.name}.backup"
            shutil.copy2(destination, backup)
            backups[destination] = backup

    try:
        for source, destination in staged:
            source.replace(destination)
            promoted.append(destination)
    except Exception:
        for destination in reversed(promoted):
            backup = backups.get(destination)
            if backup is not None and backup.is_file():
                backup.replace(destination)
            else:
                destination.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture reviewed WorkBoard documentation images.")
    parser.add_argument("--workspace", action="store_true", help="Capture the populated member workspace.")
    parser.add_argument("--report", action="store_true", help="Capture the generated pytest HTML report.")
    parser.add_argument(
        "--expected-tests",
        type=int,
        help="Required passing count for report capture; use the complete regression count.",
    )
    args = parser.parse_args()

    capture_both = not args.workspace and not args.report
    selected_workspace = args.workspace or capture_both
    selected_report = args.report or capture_both
    if selected_report and args.expected_tests is None:
        parser.error("--expected-tests is required when capturing the report image.")

    IMAGES.mkdir(parents=True, exist_ok=True)
    if selected_report:
        validate_report(PYTEST_REPORT, args.expected_tests)

    staged: list[tuple[Path, Path]] = []
    with tempfile.TemporaryDirectory(prefix=".capture-", dir=IMAGES) as staging_name:
        staging = Path(staging_name)
        if selected_workspace:
            workspace_staged = staging / WORKSPACE_IMAGE.name
            capture_workspace(workspace_staged)
            staged.append((workspace_staged, WORKSPACE_IMAGE))
        if selected_report:
            report_staged = staging / REPORT_IMAGE.name
            capture_report(report_staged, args.expected_tests)
            staged.append((report_staged, REPORT_IMAGE))

        promote_assets(staged, staging)

    for _, destination in staged:
        print(f"Saved {destination.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
