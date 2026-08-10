from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from math import ceil

from performance.config import PerformanceThresholds


@dataclass(frozen=True)
class EndpointMetric:
    name: str
    requests: int
    failures: int
    average_ms: float
    p95_ms: float
    requests_per_second: float


@dataclass(frozen=True)
class QualityGate:
    passed: bool
    checks: dict[str, bool]


def percentile_from_histogram(response_times: Mapping[int, int], percentile: float) -> float:
    sample_count = sum(response_times.values())
    if sample_count == 0:
        return 0.0
    target_rank = max(1, ceil(sample_count * percentile))
    observed = 0
    for response_time, count in sorted(response_times.items()):
        observed += count
        if observed >= target_rank:
            return float(response_time)
    return float(max(response_times))


def merge_histograms(histograms: Iterable[Mapping[int, int]]) -> dict[int, int]:
    merged: dict[int, int] = {}
    for histogram in histograms:
        for response_time, count in histogram.items():
            merged[response_time] = merged.get(response_time, 0) + count
    return merged


def evaluate_quality_gate(
    *,
    p95_ms: float,
    error_rate_percent: float,
    peak_users: int,
    request_count: int,
    setup_failures: int,
    thresholds: PerformanceThresholds,
) -> QualityGate:
    checks = {
        "read_samples_recorded": request_count > 0,
        "p95_below_target": p95_ms < thresholds.p95_ms,
        "error_rate_below_target": error_rate_percent < thresholds.error_rate_percent,
        "concurrency_reached": peak_users == thresholds.concurrent_users,
        "setup_succeeded": setup_failures == 0,
    }
    return QualityGate(passed=all(checks.values()), checks=checks)


def endpoint_metric_to_dict(metric: EndpointMetric) -> dict[str, object]:
    return asdict(metric)
