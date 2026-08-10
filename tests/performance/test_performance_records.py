from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_csv(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def test_recorded_baseline_passes_every_quality_gate() -> None:
    result = json.loads((ROOT / "performance" / "baseline-results.json").read_text(encoding="utf-8"))
    assert result["result"] == "Pass"
    assert all(result["quality_gate"].values())
    assert result["workload"]["peak_concurrent_users"] == 10
    assert result["observations"]["authenticated_read_requests"] > 0
    assert result["observations"]["p95_response_ms"] < 500
    assert result["observations"]["error_rate_percent"] < 1
    assert result["observations"]["throughput_requests_per_second"] > 0


def test_recorded_target_is_loopback_and_scope_is_bounded() -> None:
    result = json.loads((ROOT / "performance" / "baseline-results.json").read_text(encoding="utf-8"))
    assert result["environment"]["target"].startswith("http://127.0.0.1:")
    assert "not a production capacity statement" in result["scope"]


def test_performance_execution_links_case_cycle_and_traceability() -> None:
    cases = {row["Test Case ID"]: row for row in read_csv("test-management/TEST_CASES.csv")}
    cycles = {row["Cycle ID"]: row for row in read_csv("test-management/TEST_CYCLES.csv")}
    executions = {row["Execution ID"]: row for row in read_csv("test-management/TEST_EXECUTIONS.csv")}
    trace_rows = read_csv("test-management/REQUIREMENTS_TRACEABILITY.csv")

    assert cases["TC-RELEASE-005"]["Case Status"] == "Approved"
    assert cycles["CYCLE-PH10-PERFORMANCE"]["Status"] == "Completed"
    assert executions["PH10-20260810-001"]["Final Case Result"] == "Pass"
    assert any(
        row["Requirement ID"] == "NFR-PERF-001"
        and row["Test Case ID"] == "TC-RELEASE-005"
        and row["Execution ID"] == "PH10-20260810-001"
        for row in trace_rows
    )
