from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UAT = ROOT / "uat"


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8-sig")


def read_csv(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def test_required_uat_artifacts_are_present() -> None:
    required = {
        "ACCEPTANCE_CRITERIA.md",
        "SESSION_RESULTS.csv",
        "UAT_DEFECT_LOG.md",
        "UAT_PLAN.md",
        "UAT_RETEST_RESULTS.md",
        "UAT_SCENARIOS.md",
        "UAT_SESSION_NOTES.md",
        "UAT_SIGNOFF_TEMPLATE.md",
        "UAT_SUMMARY.md",
        "UAT_TEST_DATA.md",
        "UAT_TRACEABILITY.csv",
    }
    assert {path.name for path in UAT.iterdir() if path.is_file()} == required
    assert (ROOT / "test-management" / "PHASE_11_UAT_REGISTER.xlsx").is_file()


def test_six_uat_scenarios_have_unique_passing_results() -> None:
    results = read_csv("uat/SESSION_RESULTS.csv")
    assert len(results) == 6
    assert {row["Scenario ID"] for row in results} == {f"UAT-{number:03d}" for number in range(1, 7)}
    assert {row["UAT Criterion ID"] for row in results} == {f"UAT-AC-{number:03d}" for number in range(1, 7)}
    assert {row["Final Result"] for row in results} == {"Pass"}


def test_uat_cases_and_executions_resolve_to_management_registers() -> None:
    results = read_csv("uat/SESSION_RESULTS.csv")
    case_ids = {row["Test Case ID"] for row in read_csv("test-management/TEST_CASES.csv")}
    execution_ids = {row["Execution ID"] for row in read_csv("test-management/TEST_EXECUTIONS.csv")}
    assert {row["Test Case ID"] for row in results} <= case_ids
    assert {row["Execution ID"] for row in results} <= execution_ids


def test_uat_cycle_counts_reconcile_and_is_completed() -> None:
    cycle = next(
        row
        for row in read_csv("test-management/TEST_CYCLES.csv")
        if row["Cycle ID"] == "CYCLE-PH11-UAT"
    )
    assert cycle["Status"] == "Completed"
    assert int(cycle["Planned Tests"]) == 6
    assert int(cycle["Passed"]) == 6
    assert sum(int(cycle[column]) for column in ("Failed", "Blocked", "Not Run")) == 0


def test_uat_traceability_resolves_every_session_result() -> None:
    results = read_csv("uat/SESSION_RESULTS.csv")
    traces = read_csv("uat/UAT_TRACEABILITY.csv")
    assert len(traces) == 6
    assert {row["UAT Scenario ID"] for row in traces} == {row["Scenario ID"] for row in results}
    assert {row["Execution ID"] for row in traces} == {row["Execution ID"] for row in results}
    assert all(row["Requirement ID"] and row["Acceptance Criterion ID"] for row in traces)
    assert all(row["Final Status"].startswith("Accepted") for row in traces)


def test_observations_distinguish_misunderstanding_and_enhancement_from_defects() -> None:
    results = read_csv("uat/SESSION_RESULTS.csv")
    classified = {row["Issue ID"]: row["Classification"] for row in results if row["Issue ID"]}
    assert classified == {
        "UAT-ENH-001": "Enhancement request",
        "UAT-OBS-001": "Requirement misunderstanding",
    }
    issue_log = read_text("uat/UAT_DEFECT_LOG.md")
    assert "| Defect | 0 | 0 |" in issue_log
    assert "no UAT defect ID was created" in issue_log


def test_simulated_participation_is_disclosed_without_client_claim() -> None:
    combined = "\n".join(
        read_text(path)
        for path in (
            "uat/UAT_PLAN.md",
            "uat/UAT_SESSION_NOTES.md",
            "uat/UAT_SUMMARY.md",
        )
    ).lower()
    assert "single-person" in combined
    assert "simulated" in combined
    assert "no external client" in combined
    assert "not a real client" in combined


def test_uat_data_is_synthetic_and_contains_no_recorded_password() -> None:
    data = read_text("uat/UAT_TEST_DATA.md")
    assert "@example.test" in data
    assert "never written into UAT evidence" in data
    assert not re.search(r"password\s*[:=]\s*\S+", data, flags=re.IGNORECASE)


def test_retest_record_does_not_claim_an_unexecuted_fix() -> None:
    retest = read_text("uat/UAT_RETEST_RESULTS.md")
    assert "no corrective retest was required" in retest
    assert "must not be changed to “Passed retest”" in retest


def test_signoff_template_requires_participation_type_and_exceptions() -> None:
    template = read_text("uat/UAT_SIGNOFF_TEMPLATE.md")
    for field in (
        "Participation type",
        "Accepted exceptions",
        "Deferred enhancements",
        "Decision rationale",
        "Outstanding actions",
    ):
        assert field in template
