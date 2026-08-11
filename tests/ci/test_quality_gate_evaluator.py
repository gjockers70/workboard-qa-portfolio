from __future__ import annotations

import csv
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from scripts.evaluate_quality_gates import STAGE_FILES, evaluate_quality_gates


pytestmark = pytest.mark.ci


def write_junit(
    path: Path,
    *,
    tests: int = 2,
    failures: int = 0,
    errors: int = 0,
    skipped: int = 0,
) -> None:
    root = ET.Element("testsuites")
    ET.SubElement(
        root,
        "testsuite",
        tests=str(tests),
        failures=str(failures),
        errors=str(errors),
        skipped=str(skipped),
    )
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def create_project(tmp_path: Path) -> tuple[Path, Path]:
    (tmp_path / "agile").mkdir()
    (tmp_path / "test-management").mkdir()
    results = tmp_path / "reports" / "ci"
    results.mkdir(parents=True)
    (tmp_path / "agile" / "ACCEPTANCE_CRITERIA.md").write_text(
        "# Criteria\n\nAC-US001-01 must be covered.\n", encoding="utf-8"
    )
    with (tmp_path / "test-management" / "TEST_CASES.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=["Acceptance Criteria IDs"])
        writer.writeheader()
        writer.writerow({"Acceptance Criteria IDs": "AC-US001-01"})
    (tmp_path / "DEFECT_LOG.md").write_text(
        "| Defect ID | Summary | Source cycle | Case | Severity | Priority | Owner role | Status | Resolution | Retest evidence |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n"
        "| DEF-001 | Example | CYCLE-1 | TC-1 | Major | High | Developer | Closed | Fixed | Passed |\n",
        encoding="utf-8",
    )
    for file_name in STAGE_FILES.values():
        write_junit(results / file_name)
    return tmp_path, results


def test_healthy_evidence_passes_every_gate(tmp_path: Path) -> None:
    project, results = create_project(tmp_path)
    decision = evaluate_quality_gates(project, results)
    assert decision["status"] == "PASS"
    assert all(check["status"] == "PASS" for check in decision["checks"])


@pytest.mark.parametrize("failures,errors,skipped", [(1, 0, 0), (0, 1, 0), (0, 0, 1)])
def test_failed_error_or_skipped_test_blocks_the_pipeline(
    tmp_path: Path, failures: int, errors: int, skipped: int
) -> None:
    project, results = create_project(tmp_path)
    write_junit(
        results / STAGE_FILES["smoke"],
        failures=failures,
        errors=errors,
        skipped=skipped,
    )
    assert evaluate_quality_gates(project, results)["status"] == "BLOCK"


def test_missing_stage_result_blocks_the_pipeline(tmp_path: Path) -> None:
    project, results = create_project(tmp_path)
    (results / STAGE_FILES["api"]).unlink()
    assert evaluate_quality_gates(project, results)["status"] == "BLOCK"


def test_open_critical_defect_blocks_the_pipeline(tmp_path: Path) -> None:
    project, results = create_project(tmp_path)
    (project / "DEFECT_LOG.md").write_text(
        "| Defect ID | Summary | Source cycle | Case | Severity | Priority | Owner role | Status | Resolution | Retest evidence |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n"
        "| DEF-CRIT-001 | Example | CYCLE-1 | TC-1 | Critical | Critical | Developer | Assigned | Pending | Pending |\n",
        encoding="utf-8",
    )
    assert evaluate_quality_gates(project, results)["status"] == "BLOCK"


def test_missing_acceptance_coverage_blocks_the_pipeline(tmp_path: Path) -> None:
    project, results = create_project(tmp_path)
    (project / "agile" / "ACCEPTANCE_CRITERIA.md").write_text(
        "AC-US001-01 and AC-US001-02 must be covered.\n", encoding="utf-8"
    )
    assert evaluate_quality_gates(project, results)["status"] == "BLOCK"
