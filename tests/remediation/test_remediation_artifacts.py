import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_csv(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_required_phase12_artifacts_are_present() -> None:
    required = (
        "remediation/REMEDIATION_PLAN.md",
        "remediation/RETEST_EXECUTION_GUIDE.md",
        "remediation/REGRESSION_IMPACT_ANALYSIS.md",
        "remediation/DEFECT_RETEST_MATRIX.csv",
        "remediation/PHASE_12_RETEST_SUMMARY.md",
        "test-management/PHASE_12_RETEST_REGISTER.xlsx",
    )
    assert all((ROOT / path).is_file() for path in required)


def test_every_confirmed_defect_has_a_phase12_confirmation() -> None:
    matrix = read_csv("remediation/DEFECT_RETEST_MATRIX.csv")
    assert {row["Defect ID"] for row in matrix} == {
        "DEF-P3-001", "DEF-P3-002", "DEF-P8-001", "DEF-P8-002"
    }
    assert len({row["Phase 12 Execution"] for row in matrix}) == 4
    assert all(row["Original Result"] == "Fail" for row in matrix)
    assert all("Pass" in row["Original Retest"] for row in matrix)
    assert all(row["Final Status"] == "Closed" for row in matrix)


def test_phase12_executions_resolve_to_closed_defects_and_cases() -> None:
    matrix = read_csv("remediation/DEFECT_RETEST_MATRIX.csv")
    executions = read_csv("test-management/TEST_EXECUTIONS.csv")
    cases = {row["Test Case ID"] for row in read_csv("test-management/TEST_CASES.csv")}
    phase12 = {row["Execution ID"]: row for row in executions if row["Cycle ID"] == "CYCLE-PH12-REMEDIATION-20260810"}
    for row in matrix:
        execution = phase12[row["Phase 12 Execution"]]
        assert execution["Test Case ID"] == row["Source Case"]
        assert execution["Test Case ID"] in cases
        assert execution["Linked Defect"] == row["Defect ID"]
        assert execution["Final Case Result"] == "Pass"


def test_phase12_cycle_counts_reconcile() -> None:
    cycles = {row["Cycle ID"]: row for row in read_csv("test-management/TEST_CYCLES.csv")}
    cycle = cycles["CYCLE-PH12-REMEDIATION-20260810"]
    executions = [row for row in read_csv("test-management/TEST_EXECUTIONS.csv") if row["Cycle ID"] == cycle["Cycle ID"]]
    result_counts = {result: sum(row["Final Case Result"] == result for row in executions) for result in ("Pass", "Fail", "Blocked", "Not Run")}
    assert len(executions) == int(cycle["Planned Tests"]) == 10
    assert result_counts["Pass"] == int(cycle["Passed"]) == 10
    assert result_counts["Fail"] == int(cycle["Failed"]) == 0
    assert result_counts["Blocked"] == int(cycle["Blocked"]) == 0
    assert result_counts["Not Run"] == int(cycle["Not Run"]) == 0
    assert cycle["Status"] == "Completed"


def test_phase12_contains_four_retests_and_six_regression_executions() -> None:
    executions = [row for row in read_csv("test-management/TEST_EXECUTIONS.csv") if row["Cycle ID"] == "CYCLE-PH12-REMEDIATION-20260810"]
    assert sum(row["Attempt"] == "Retest confirmation" for row in executions) == 4
    assert sum(row["Attempt"] == "Regression" for row in executions) == 6
    assert all(row["Final Case Result"] == "Pass" for row in executions)


def test_uat_items_are_not_misrepresented_as_fixed_defects() -> None:
    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in (
        "remediation/REMEDIATION_PLAN.md",
        "remediation/REGRESSION_IMPACT_ANALYSIS.md",
        "remediation/PHASE_12_RETEST_SUMMARY.md",
        "uat/UAT_RETEST_RESULTS.md",
    ))
    assert "UAT-OBS-001" in combined
    assert "UAT-ENH-001" in combined
    assert "no product change" in combined.lower()
    assert "ENH-002 remains deferred" in combined


def test_defect_register_has_phase12_evidence_for_every_closed_defect() -> None:
    defect_log = (ROOT / "DEFECT_LOG.md").read_text(encoding="utf-8")
    for index in range(1, 5):
        assert f"PH12-20260810-00{index}" in defect_log
