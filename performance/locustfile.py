from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from uuid import uuid4

import locust
from locust import HttpUser, between, events, task

from performance.config import (
    READ_REQUEST_NAMES,
    THRESHOLDS,
    terminate_if_target_is_not_local,
    validate_local_base_url,
)
from performance.metrics import (
    EndpointMetric,
    endpoint_metric_to_dict,
    evaluate_quality_gate,
    merge_histograms,
    percentile_from_histogram,
)


_observed_peak_users = 0


class WorkBoardReadUser(HttpUser):
    wait_time = between(0.2, 0.5)

    def on_start(self) -> None:
        identity = uuid4().hex
        response = self.client.post(
            "/api/auth/register",
            name="SETUP /api/auth/register",
            json={
                "email": f"phase10.{identity}@example.test",
                "display_name": "Phase 10 Member",
                "password": f"Synthetic-{identity}",
            },
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(3)
    def list_tasks(self) -> None:
        self.client.get("/api/tasks?state=all", name="GET /api/tasks")

    @task(2)
    def read_profile(self) -> None:
        self.client.get("/api/profile", name="GET /api/profile")

    @task(1)
    def search_active_tasks(self) -> None:
        self.client.get(
            "/api/tasks?search=phase&state=active",
            name="GET /api/tasks?search&state",
        )


@events.init_command_line_parser.add_listener
def validate_target_from_options(parser, **_kwargs) -> None:
    parser.add_argument(
        "--result-json",
        env_var="WORKBOARD_PERF_RESULT_JSON",
        default="reports/performance/baseline-results.json",
        help="Path for the evaluated baseline result.",
    )


@events.test_start.add_listener
def validate_local_target(environment, **_kwargs) -> None:
    terminate_if_target_is_not_local(environment)


@events.spawning_complete.add_listener
def record_peak_users(user_count: int, **_kwargs) -> None:
    global _observed_peak_users
    _observed_peak_users = max(_observed_peak_users, user_count)


@events.test_stop.add_listener
def write_evaluated_result(environment, **_kwargs) -> None:
    entries = [environment.stats.get(name, "GET") for name in READ_REQUEST_NAMES]
    total_requests = sum(entry.num_requests for entry in entries)
    total_failures = sum(entry.num_failures for entry in entries)
    total_response_time = sum(entry.total_response_time for entry in entries)
    response_histogram = merge_histograms(entry.response_times for entry in entries)
    p95_ms = percentile_from_histogram(response_histogram, 0.95)
    error_rate_percent = (total_failures / total_requests * 100.0) if total_requests else 0.0
    average_ms = (total_response_time / total_requests) if total_requests else 0.0
    throughput = sum(entry.total_rps for entry in entries)
    setup_entry = environment.stats.get("SETUP /api/auth/register", "POST")

    endpoint_metrics = []
    for entry in entries:
        endpoint_metrics.append(
            EndpointMetric(
                name=entry.name,
                requests=entry.num_requests,
                failures=entry.num_failures,
                average_ms=round(entry.avg_response_time, 2),
                p95_ms=round(entry.get_response_time_percentile(0.95) or 0.0, 2),
                requests_per_second=round(entry.total_rps, 2),
            )
        )

    gate = evaluate_quality_gate(
        p95_ms=p95_ms,
        error_rate_percent=error_rate_percent,
        peak_users=_observed_peak_users,
        request_count=total_requests,
        setup_failures=setup_entry.num_failures,
        thresholds=THRESHOLDS,
    )
    result = {
        "result": "Pass" if gate.passed else "Fail",
        "scope": "Bounded local baseline; not a production capacity statement.",
        "environment": {
            "operating_system": platform.platform(),
            "python": platform.python_version(),
            "locust": locust.__version__,
            "target": validate_local_base_url(environment.host),
        },
        "workload": {
            "peak_concurrent_users": _observed_peak_users,
            "spawn_rate_users_per_second": environment.parsed_options.spawn_rate,
            "run_time": environment.parsed_options.run_time,
            "wait_time_seconds": "0.2-0.5",
        },
        "observations": {
            "authenticated_read_requests": total_requests,
            "failures": total_failures,
            "error_rate_percent": round(error_rate_percent, 4),
            "average_response_ms": round(average_ms, 2),
            "p95_response_ms": round(p95_ms, 2),
            "throughput_requests_per_second": round(throughput, 2),
            "setup_failures": setup_entry.num_failures,
            "endpoints": [endpoint_metric_to_dict(item) for item in endpoint_metrics],
        },
        "target": {
            "p95_response_ms_below": THRESHOLDS.p95_ms,
            "error_rate_percent_below": THRESHOLDS.error_rate_percent,
            "concurrent_users": THRESHOLDS.concurrent_users,
        },
        "quality_gate": gate.checks,
    }
    output_path = Path(environment.parsed_options.result_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if not gate.passed and environment.process_exit_code in {None, 0}:
        environment.process_exit_code = 1
