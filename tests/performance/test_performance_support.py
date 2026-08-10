from __future__ import annotations

from types import SimpleNamespace

import pytest

from performance.config import (
    PerformanceThresholds,
    terminate_if_target_is_not_local,
    validate_local_base_url,
)
from performance.metrics import evaluate_quality_gate, merge_histograms, percentile_from_histogram


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("http://127.0.0.1:8010", "http://127.0.0.1:8010"),
        ("http://localhost:9000/", "http://localhost:9000"),
    ],
)
def test_local_target_guard_accepts_loopback(value: str, expected: str) -> None:
    assert validate_local_base_url(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "https://127.0.0.1:8010",
        "http://example.test:8010",
        "http://127.0.0.1",
        "http://127.0.0.1:8010/api",
        "http://user:pass@127.0.0.1:8010",
        "http://127.0.0.1:8010?mode=test",
    ],
)
def test_local_target_guard_rejects_out_of_scope_targets(value: str) -> None:
    with pytest.raises(ValueError):
        validate_local_base_url(value)


def test_locust_run_terminates_before_using_an_external_target() -> None:
    environment = SimpleNamespace(host="http://example.test:8010", process_exit_code=0)
    with pytest.raises(SystemExit, match="loopback host"):
        terminate_if_target_is_not_local(environment)
    assert environment.process_exit_code == 2


def test_histograms_merge_and_return_combined_percentile() -> None:
    merged = merge_histograms([{10: 90, 20: 5}, {30: 5}])
    assert merged == {10: 90, 20: 5, 30: 5}
    assert percentile_from_histogram(merged, 0.95) == 20.0


def test_percentile_returns_zero_without_samples() -> None:
    assert percentile_from_histogram({}, 0.95) == 0.0


def test_quality_gate_passes_only_when_every_condition_passes() -> None:
    gate = evaluate_quality_gate(
        p95_ms=499.0,
        error_rate_percent=0.99,
        peak_users=10,
        request_count=50,
        setup_failures=0,
        thresholds=PerformanceThresholds(),
    )
    assert gate.passed
    assert all(gate.checks.values())


@pytest.mark.parametrize(
    "overrides",
    [
        {"p95_ms": 500.0},
        {"error_rate_percent": 1.0},
        {"peak_users": 9},
        {"request_count": 0},
        {"setup_failures": 1},
    ],
)
def test_quality_gate_rejects_each_failed_boundary(overrides: dict[str, float | int]) -> None:
    values = {
        "p95_ms": 100.0,
        "error_rate_percent": 0.0,
        "peak_users": 10,
        "request_count": 50,
        "setup_failures": 0,
    }
    values.update(overrides)
    gate = evaluate_quality_gate(**values, thresholds=PerformanceThresholds())
    assert not gate.passed
