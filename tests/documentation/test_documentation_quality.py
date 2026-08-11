from __future__ import annotations

import json
from pathlib import Path
import re
import struct
import subprocess
from urllib.parse import unquote
import zipfile

import pytest

from scripts import capture_documentation_images as capture_images


pytestmark = pytest.mark.documentation
ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


def repository_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]


def text_files() -> list[Path]:
    return [path for path in repository_paths() if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8-sig")


def test_required_completion_documents_exist() -> None:
    required = (
        "README.md",
        "ARCHITECTURE.md",
        "TEST_STRATEGY.md",
        "TEST_PLAN.md",
        "TRACEABILITY_MATRIX.md",
        "DEFECT_LOG.md",
        "accessibility/ACCESSIBILITY_TEST_PLAN.md",
        "uat/UAT_PLAN.md",
        "agile/SPRINT_PLAN.md",
        "TEST_SUMMARY_REPORT.md",
        "RUNBOOK.md",
    )
    missing = [relative for relative in required if not (ROOT / relative).is_file()]
    assert not missing
    assert all((ROOT / relative).stat().st_size > 500 for relative in required)


def test_readme_contains_every_portfolio_section() -> None:
    text = read("README.md")
    headings = {line.strip() for line in text.splitlines() if line.startswith("#")}
    required_headings = (
        "## Project purpose",
        "## Screenshots",
        "## Example test report",
        "## Architecture",
        "## Technology stack",
        "## Testing types and evidence",
        "## Automation framework structure",
        "## Accessibility",
        "## User acceptance testing",
        "## Agile Test Management",
        "## CI/CD",
        "## Skills demonstrated",
        "## Known limitations",
    )
    assert not [heading for heading in required_headings if heading not in headings]


def test_documentation_images_are_valid_publication_assets() -> None:
    readme = read("README.md")
    images = (
        ROOT / "docs" / "images" / "workboard-workspace.png",
        ROOT / "docs" / "images" / "pytest-html-report.png",
    )
    for path in images:
        assert path.as_posix().split("/docs/images/")[-1] in readme
        capture_images.validate_png(path)
        payload = path.read_bytes()
        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
        width, height = struct.unpack(">II", payload[16:24])
        assert width >= 1200
        assert height >= 700
        offset = 8
        chunk_types: set[bytes] = set()
        while offset + 12 <= len(payload):
            chunk_length = struct.unpack(">I", payload[offset:offset + 4])[0]
            chunk_types.add(payload[offset + 4:offset + 8])
            offset += chunk_length + 12
        assert not chunk_types.intersection({b"eXIf", b"iTXt", b"tEXt", b"zTXt"})
    assert (ROOT / "scripts" / "capture_documentation_images.py").is_file()
    assert "scripts/capture_documentation_images.py" in readme


def test_all_local_markdown_links_resolve() -> None:
    unresolved: list[str] = []
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for document in (path for path in text_files() if path.suffix.lower() == ".md"):
        for raw_target in link_pattern.findall(document.read_text(encoding="utf-8-sig")):
            candidate = raw_target.strip()
            target = candidate[1:candidate.index(">")].strip() if candidate.startswith("<") else candidate.split(maxsplit=1)[0]
            if not target or target.startswith("#") or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            relative_target = unquote(target.split("#", 1)[0])
            if not relative_target:
                continue
            resolved = (document.parent / relative_target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                unresolved.append(f"{document.relative_to(ROOT)} escapes repository -> {target}")
                continue
            if not resolved.exists():
                unresolved.append(f"{document.relative_to(ROOT)} -> {target}")
    assert not unresolved


def test_published_text_has_clean_encoding_and_no_personal_machine_path() -> None:
    encoding_markers = {chr(0x00C2), chr(0x00C3), chr(0x00E2), chr(0xFFFD)}
    failures: list[str] = []
    for path in text_files():
        text = path.read_text(encoding="utf-8-sig")
        if any(marker in text for marker in encoding_markers):
            failures.append(f"encoding marker in {path.relative_to(ROOT)}")
        if re.search(r"[A-Za-z]:[\\/]+Users[\\/]", text, re.I):
            failures.append(f"personal machine path in {path.relative_to(ROOT)}")
    assert not failures


def test_publication_content_excludes_restricted_attribution() -> None:
    terms = (
        "".join(("a", "i")),
        "".join(("arti", "ficial", " intel", "ligence")),
        "".join(("chat", "gpt")),
        "".join(("open", "a", "i")),
        "".join(("co", "dex")),
        "".join(("gener", "ative", " ", "a", "i")),
        "".join(("large", " language", " model")),
        "".join(("l", "lm")),
    )
    patterns = [re.compile(rf"\b{re.escape(term)}\b", re.I) for term in terms]
    failures: list[str] = []

    for path in repository_paths():
        if not path.is_file():
            continue
        texts: list[str] = []
        if path.suffix.lower() == ".xlsx" and zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as archive:
                texts.extend(
                    archive.read(name).decode("utf-8", errors="ignore")
                    for name in archive.namelist()
                    if name.endswith((".xml", ".rels"))
                )
        elif path.suffix.lower() not in {".gif", ".jpeg", ".jpg", ".png", ".webp"}:
            payload = path.read_bytes()
            if b"\0" not in payload:
                try:
                    texts.append(payload.decode("utf-8-sig"))
                except UnicodeDecodeError:
                    continue
        for text in texts:
            if any(pattern.search(text) for pattern in patterns):
                failures.append(str(path.relative_to(ROOT)))
                break
    assert not failures


def test_setup_uses_one_root_virtual_environment_and_locked_frontend_install() -> None:
    combined = read("README.md") + read("RUNBOOK.md")
    assert "python -m venv .venv" in combined
    assert ".venv\\Scripts\\python.exe" in combined
    assert "app/backend/.venv" not in combined.replace("\\", "/")
    assert "npm.cmd ci --prefix app\\frontend" in combined
    assert "synthetic.admin@example.test" in combined


def test_strategy_defines_risk_selection_layers_gates_and_limits() -> None:
    text = read("TEST_STRATEGY.md")
    for expected in (
        "## 4. Risk model",
        "## 5. Test layers and responsibilities",
        "## 6. Automation selection",
        "## 7. Environments and test data",
        "## 8. Reliability and flake prevention",
        "## 9. Entry, exit, and blocking gates",
        "## 10. Evidence and traceability",
        "## 11. Maintenance and change control",
        "## 12. Limitations",
    ):
        assert expected in text


def test_runbook_contains_every_required_troubleshooting_path() -> None:
    text = read("RUNBOOK.md")
    required = (
        "### Selenium browser failure",
        "### Flaky test",
        "### API test failure",
        "### Database mismatch",
        "### Accessibility regression",
        "### CI failure",
        "### Missing test data",
        "### Failed regression suite",
        "### UAT defect escalation",
        "### Report-generation failure",
    )
    assert not [heading for heading in required if heading not in text]
    for expected in ("## Readiness check", "## Evidence locations", "## Stop and cleanup"):
        assert expected in text


def test_remote_access_notes_separate_executed_and_design_only_scope() -> None:
    text = read("docs/REMOTE_ACCESS_TESTING.md")
    for expected in (
        "## Executed local checks",
        "## Design-only scenarios",
        "## Timeout and persistence distinction",
        "## Latency-sensitive behavior",
        "## Authentication and authorization checks",
        "## Security considerations",
        "TC-REMOTE-001",
        "TC-REMOTE-002",
        "have not been executed",
    ):
        assert expected in text


def test_web_services_notes_cover_rest_and_conceptual_soap_testing() -> None:
    text = read("docs/WEB_SERVICES_TESTING.md")
    for expected in (
        "## Implemented REST approach",
        "## REST and SOAP comparison",
        "## Conceptual SOAP-style example",
        "Request construction",
        "Authentication",
        "Contract",
        "Content validation",
        "Error handling",
        "were not executed",
    ):
        assert expected in text


def test_architecture_represents_every_implemented_framework_layer() -> None:
    text = read("ARCHITECTURE.md")
    for expected in (
        "framework/pages/",
        "framework/clients/",
        "framework/database/inspector.py",
        "framework/accessibility/axe.py",
        "framework/management/",
        ".github/workflows/quality-gates.yml",
        "There is no blanket retry plugin",
    ):
        assert expected in text


def test_documentation_checks_are_part_of_the_fast_quality_workflow() -> None:
    workflow = read(".github/workflows/quality-gates.yml")
    pytest_config = read("pytest.ini")
    assert "tests/documentation" in workflow
    assert "documentation:" in pytest_config


def test_repository_hygiene_configuration_is_reproducible() -> None:
    ignore = read(".gitignore")
    attributes = read(".gitattributes")
    package = json.loads(read("app/frontend/package.json"))
    package_lock = json.loads(read("app/frontend/package-lock.json"))

    for expected in (".env.*", "!.env.example", "reports/", "*.sqlite", "*.log"):
        assert expected in ignore
    for expected in ("*.md text eol=lf", "*.csv text eol=crlf", "*.png binary", "*.xlsx binary"):
        assert expected in attributes

    direct = package["dependencies"] | package["devDependencies"]
    assert all(re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", value) for value in direct.values())
    assert set(package["dependencies"]) == {"react", "react-dom"}
    assert {"@vitejs/plugin-react", "typescript", "vite"} <= set(package["devDependencies"])
    locked_root = package_lock["packages"][""]
    assert locked_root["dependencies"] == package["dependencies"]
    assert locked_root["devDependencies"] == package["devDependencies"]

    requirement_pattern = re.compile(r"^[A-Za-z0-9_.-]+(?:\[[^\]]+\])?==[^\s]+$")
    requirements = read("requirements-test.txt").splitlines() + read("app/backend/requirements.txt").splitlines()
    assert all(requirement_pattern.fullmatch(line) for line in requirements if line and not line.startswith("#"))

    transient_parts = {".build", ".pytest_cache", ".venv", "dist", "evidence", "node_modules", "reports"}
    transient_suffixes = {".db", ".log", ".pid", ".sqlite", ".sqlite3"}
    leaked = [
        str(path.relative_to(ROOT))
        for path in repository_paths()
        if transient_parts.intersection(path.relative_to(ROOT).parts)
        or path.suffix.lower() in transient_suffixes
    ]
    assert not leaked


def test_report_capture_accepts_only_the_expected_all_pass_summary(tmp_path: Path) -> None:
    report = tmp_path / "report.html"
    report.write_text(
        '<html><title>pytest report</title><p class="run-count">3 tests took 1 ms.</p>'
        '<span class="failed">0 Failed,</span><span class="passed">3 Passed,</span>'
        '<span class="skipped">0 Skipped,</span><span class="xfailed">0 Expected failures,</span>'
        '<span class="xpassed">0 Unexpected passes,</span><span class="error">0 Errors,</span>'
        '<span class="rerun">0 Reruns</span><span class="retried">0 Retried,</span></html>',
        encoding="utf-8",
    )
    assert capture_images.validate_report(report, 3)["passed"] == 3


def test_report_capture_rejects_nonpassing_or_incomplete_provenance(tmp_path: Path) -> None:
    report = tmp_path / "report.html"
    report.write_text(
        '<html><title>pytest report</title><p class="run-count">3 tests took 1 ms.</p>'
        '<span class="failed">1 Failed,</span><span class="passed">2 Passed,</span>'
        '<span class="skipped">0 Skipped,</span><span class="xfailed">0 Expected failures,</span>'
        '<span class="xpassed">0 Unexpected passes,</span><span class="error">0 Errors,</span></html>',
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError):
        capture_images.validate_report(report, 3)

    report.write_text(report.read_text(encoding="utf-8").replace("1 Failed", "0 Failed").replace("2 Passed", "3 Passed"), encoding="utf-8")
    with pytest.raises(RuntimeError):
        capture_images.validate_report(report, 4)

    personal_path = "".join(("C:", "\\", "Users", "\\", "Example", "\\", "report"))
    report.write_text(report.read_text(encoding="utf-8").replace("</html>", f" {personal_path}</html>"), encoding="utf-8")
    with pytest.raises(RuntimeError):
        capture_images.validate_report(report, 3)

    non_synthetic_email = "".join(("person", "@", "sample", ".invalid"))
    report.write_text(report.read_text(encoding="utf-8").replace(f" {personal_path}", f" {non_synthetic_email}"), encoding="utf-8")
    with pytest.raises(RuntimeError):
        capture_images.validate_report(report, 3)


def test_service_startup_failure_stops_an_already_started_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeProcess:
        returncode: int | None = None

        def __init__(self) -> None:
            self.stopped = False

        def poll(self) -> int | None:
            return 0 if self.stopped else None

        def terminate(self) -> None:
            self.stopped = True
            self.returncode = 0

        def wait(self, timeout: int) -> int:
            self.stopped = True
            self.returncode = 0
            return 0

        def kill(self) -> None:
            self.terminate()

    frontend = tmp_path / "frontend"
    vite = frontend / "node_modules" / "vite" / "bin" / "vite.js"
    vite.parent.mkdir(parents=True)
    vite.write_text("", encoding="utf-8")
    backend = FakeProcess()
    starts = 0

    def fake_popen(*_args, **_kwargs):
        nonlocal starts
        starts += 1
        if starts == 1:
            return backend
        raise OSError("frontend launch failed")

    monkeypatch.setattr(capture_images, "BACKEND", tmp_path / "backend")
    monkeypatch.setattr(capture_images, "FRONTEND", frontend)
    monkeypatch.setattr(capture_images, "CAPTURE_REPORTS", tmp_path / "reports")
    monkeypatch.setattr(capture_images, "ensure_port_available", lambda _port: None)
    monkeypatch.setattr(capture_images, "wait_until_ports_released", lambda *_ports: None)
    monkeypatch.setattr(capture_images.shutil, "which", lambda _name: "node.exe")
    monkeypatch.setattr(capture_images.subprocess, "Popen", fake_popen)

    with pytest.raises(OSError, match="frontend launch failed"):
        with capture_images.local_application():
            pass
    assert backend.stopped
