from __future__ import annotations

import re
from pathlib import Path

from framework.management import RegisterSet, split_ids


ROOT = Path(__file__).resolve().parents[2]


def test_required_phase9_artifacts_and_csv_headers_are_present() -> None:
    required = {
        "agile/PRODUCT_BACKLOG.md",
        "agile/SPRINT_PLAN.md",
        "agile/USER_STORIES.md",
        "agile/ACCEPTANCE_CRITERIA.md",
        "agile/DEFECT_TRIAGE.md",
        "agile/SPRINT_REVIEW_NOTES.md",
        "agile/SPRINT_TEST_SUMMARY.md",
        "DEFECT_LOG.md",
        "TRACEABILITY_MATRIX.md",
        "docs/AGILE_TEST_MANAGEMENT.md",
        "test-management/TEST_CASES.csv",
        "test-management/TEST_CYCLES.csv",
        "test-management/TEST_EXECUTIONS.csv",
        "test-management/REQUIREMENTS_TRACEABILITY.csv",
        "performance/PERFORMANCE_TEST_PLAN.md",
        "performance/PERFORMANCE_RESULTS.md",
        "performance/baseline-results.json",
    }
    assert not [relative for relative in sorted(required) if not (ROOT / relative).is_file()]

    registers = RegisterSet.load(ROOT)
    assert set(registers.cases[0]) == {
        "Test Case ID", "Title", "Objective", "Type", "Priority", "Requirement IDs",
        "Acceptance Criteria IDs", "Preconditions", "Test Data", "Steps", "Expected Result",
        "Labels", "Automation Candidate", "Case Status", "Version",
    }
    assert {"Cycle ID", "Planned Tests", "Passed", "Failed", "Blocked", "Not Run", "Status"} <= set(registers.cycles[0])
    assert {"Execution ID", "Cycle ID", "Test Case ID", "Final Case Result", "Linked Defect"} <= set(registers.executions[0])


def test_register_identifiers_are_unique() -> None:
    registers = RegisterSet.load(ROOT)
    assert len(registers.unique_values(registers.cases, "Test Case ID")) == 55
    assert len(registers.unique_values(registers.cycles, "Cycle ID")) == 9
    assert len(registers.unique_values(registers.executions, "Execution ID")) == 70


def test_execution_references_resolve_to_cases_and_cycles() -> None:
    registers = RegisterSet.load(ROOT)
    case_ids = registers.unique_values(registers.cases, "Test Case ID")
    cycle_ids = registers.unique_values(registers.cycles, "Cycle ID")
    assert not {row["Test Case ID"] for row in registers.executions} - case_ids
    assert not {row["Cycle ID"] for row in registers.executions} - cycle_ids


def test_every_acceptance_criterion_is_covered_by_a_case() -> None:
    registers = RegisterSet.load(ROOT)
    criteria_text = (ROOT / "agile" / "ACCEPTANCE_CRITERIA.md").read_text(encoding="utf-8-sig")
    criterion_ids = set(re.findall(r"AC-US\d{3}-\d{2}", criteria_text))
    covered = set().union(*(split_ids(row["Acceptance Criteria IDs"]) for row in registers.cases))
    assert len(criterion_ids) == 56
    assert criterion_ids == covered


def test_traceability_has_a_resolvable_chain_for_every_story() -> None:
    registers = RegisterSet.load(ROOT)
    case_ids = registers.unique_values(registers.cases, "Test Case ID")
    cycle_ids = registers.unique_values(registers.cycles, "Cycle ID")
    execution_ids = registers.unique_values(registers.executions, "Execution ID")
    story_ids = {f"US-{number:03d}" for number in range(1, 11)}

    assert {row["User Story ID"] for row in registers.traceability} == story_ids
    for row in registers.traceability:
        assert row["Requirement ID"]
        assert re.fullmatch(r"AC-US\d{3}-\d{2}", row["Acceptance Criteria ID"])
        assert row["Test Case ID"] in case_ids
        assert row["Test Cycle ID"] in cycle_ids
        assert row["Automated Test"]
        if row["Execution ID"]:
            assert row["Execution ID"] in execution_ids


def test_completed_cycle_counts_reconcile() -> None:
    registers = RegisterSet.load(ROOT)
    completed = [row for row in registers.cycles if row["Status"] == "Completed"]
    assert len(completed) == 9
    for row in completed:
        planned = int(row["Planned Tests"])
        accounted = sum(int(row[column]) for column in ("Passed", "Failed", "Blocked", "Not Run"))
        assert planned == accounted, row["Cycle ID"]
        assert int(row["Failed"]) == 0
        assert int(row["Blocked"]) == 0


def test_failed_executions_have_closed_defects_and_passing_retests() -> None:
    registers = RegisterSet.load(ROOT)
    defect_log = (ROOT / "DEFECT_LOG.md").read_text(encoding="utf-8-sig")
    closed_defects = set(re.findall(r"\| (DEF-[A-Z0-9-]+) \|[^\n]+\| Closed \|", defect_log))
    failed = [row for row in registers.executions if row["Final Case Result"] == "Fail"]
    assert len(failed) == 2
    for row in failed:
        assert row["Linked Defect"] in closed_defects
        assert any(
            candidate["Test Case ID"] == row["Test Case ID"]
            and row["Linked Defect"] in split_ids(candidate["Linked Defect"])
            and candidate["Attempt"] == "Retest"
            and candidate["Final Case Result"] == "Pass"
            for candidate in registers.executions
        )


def test_readme_and_mapping_document_show_the_management_workflow() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    mapping = (ROOT / "docs" / "AGILE_TEST_MANAGEMENT.md").read_text(encoding="utf-8-sig")
    assert "## Agile Test Management" in readme
    for term in ("Jira", "Confluence", "Zephyr Scale"):
        assert term in readme
        assert term in mapping
    for required_example in ("US-007", "TC-API-AUTHZ-001", "DEF-P3-001", "CYCLE-PH5-REGRESSION-20260810"):
        assert required_example in readme + mapping
