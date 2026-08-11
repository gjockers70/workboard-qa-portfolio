from __future__ import annotations

import csv
import json
from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.reporting
ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "TEST_SUMMARY_REPORT.md"


def read_csv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def report_text() -> str:
    return REPORT.read_text(encoding="utf-8-sig")


def test_report_contains_required_technical_and_stakeholder_sections() -> None:
    text = report_text()
    for heading in (
        "## 2. Executive summary",
        "## 5. Test inventory and execution summary",
        "## 7. Defect summary",
        "## 8. Accessibility results",
        "## 9. UAT and accepted exceptions",
        "## 10. Performance and pipeline results",
        "## 11. Residual risks and limitations",
        "## 12. Technical release recommendation",
        "## 13. Stakeholder-facing summary",
    ):
        assert heading in text


def test_managed_inventory_and_execution_counts_match_the_report() -> None:
    cases = read_csv("test-management/TEST_CASES.csv")
    executions = read_csv("test-management/TEST_EXECUTIONS.csv")
    assert len(cases) == 55
    assert {row["Case Status"] for row in cases} == {"Approved"}
    assert len(executions) == 77
    assert sum(row["Final Case Result"] == "Pass" for row in executions) == 75
    assert sum(row["Final Case Result"] == "Fail" for row in executions) == 2
    for expected in ("Unique managed test cases | 55", "Recorded execution rows | 77", "Pass rows | 75", "Historical Fail rows | 2"):
        assert expected in report_text()


def test_completed_cycle_totals_match_the_report() -> None:
    cycles = read_csv("test-management/TEST_CYCLES.csv")
    completed = [row for row in cycles if row["Status"] == "Completed"]
    assert len(completed) == 11
    assert sum(int(row["Planned Tests"]) for row in completed) == 125
    assert sum(int(row["Passed"]) for row in completed) == 125
    assert sum(int(row[column]) for row in completed for column in ("Failed", "Blocked", "Not Run")) == 0
    assert "Planned checks across completed cycles | 125" in report_text()


def test_defect_severity_and_closure_counts_match_the_report() -> None:
    lines = (ROOT / "DEFECT_LOG.md").read_text(encoding="utf-8-sig").splitlines()
    rows = [[part.strip() for part in line.strip("|").split("|")] for line in lines if line.startswith("| DEF-")]
    assert len(rows) == 4
    assert sum(row[4] == "Major" for row in rows) == 3
    assert sum(row[4] == "Minor" for row in rows) == 1
    assert all(row[7] == "Closed" for row in rows)
    assert "**Total** | **4** | **4** | **0**" in report_text()


def test_acceptance_criteria_coverage_matches_the_report() -> None:
    criteria = set(re.findall(r"AC-US\d{3}-\d{2}", (ROOT / "agile" / "ACCEPTANCE_CRITERIA.md").read_text(encoding="utf-8-sig")))
    covered: set[str] = set()
    for row in read_csv("test-management/TEST_CASES.csv"):
        covered.update(value.strip() for value in row["Acceptance Criteria IDs"].split(";") if value.strip())
    assert len(criteria) == 56
    assert criteria == covered
    assert "Acceptance criteria with case coverage | 56" in report_text()


def test_specialized_results_are_reported_without_overclaiming() -> None:
    performance = json.loads((ROOT / "performance" / "baseline-results.json").read_text(encoding="utf-8"))
    assert performance["result"] == "Pass"
    text = report_text()
    for expected in (
        "p95 response time | 17 ms",
        "Error rate | 0.0000%",
        "6 of 6 business scenarios passed",
        "Lighthouse accessibility score: 100",
        "not legal certification",
        "not a production-capacity",
        "no real-client experience",
    ):
        assert expected in text


def test_release_recommendation_is_supported_by_exit_criteria() -> None:
    cycles = read_csv("test-management/TEST_CYCLES.csv")
    defect_lines = (ROOT / "DEFECT_LOG.md").read_text(encoding="utf-8-sig").splitlines()
    defects = [
        [part.strip() for part in line.strip("|").split("|")]
        for line in defect_lines
        if line.startswith("| DEF-")
    ]
    assert all(row["Status"] == "Completed" for row in cycles)
    assert all(int(row["Failed"]) == int(row["Blocked"]) == int(row["Not Run"]) == 0 for row in cycles)
    assert not [row[0] for row in defects if row[4] in {"Critical", "Major"} and row[7] != "Closed"]
    assert "**RELEASE** the corrected WorkBoard baseline for the tested portfolio scope." in report_text()


def test_phase14_traceability_and_status_records_resolve() -> None:
    text = report_text()
    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    backlog = (ROOT / "agile" / "PRODUCT_BACKLOG.md").read_text(encoding="utf-8-sig")
    traceability = read_csv("test-management/REQUIREMENTS_TRACEABILITY.csv")
    assert "Phase 14 - Test summary reporting" in readme
    assert re.search(r"\| 10 \| US-010 \| Story \|[^\n]+\| Done \|", backlog)
    assert any(
        row["Acceptance Criteria ID"] == "AC-US010-06"
        and row["Test Case ID"] == "TC-RELEASE-006"
        and row["Execution ID"] == "PH14-20260810-001"
        and row["Final Status"] == "Release recommended"
        for row in traceability
    )
    assert "Approved; hosted validation pending" in text
