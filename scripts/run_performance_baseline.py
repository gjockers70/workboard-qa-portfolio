from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"
REPORTS = ROOT / "reports" / "performance"
TRACKED_RESULT = ROOT / "performance" / "baseline-results.json"
TRACKED_REPORT = ROOT / "performance" / "PERFORMANCE_RESULTS.md"


def wait_until_ready(url: str, process: subprocess.Popen[str], timeout_seconds: int = 20) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Local API exited before startup with code {process.returncode}.")
        try:
            with urlopen(f"{url}/health", timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.2)
    raise TimeoutError("Local API did not become ready within 20 seconds.")


def ensure_port_available(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        if probe.connect_ex((host, port)) == 0:
            raise RuntimeError(f"Port {port} is already in use. Stop that local process and retry.")


def render_markdown(result: dict[str, object], command: str) -> str:
    observations = result["observations"]
    workload = result["workload"]
    target = result["target"]
    environment = result["environment"]
    endpoints = observations["endpoints"]
    endpoint_rows = "\n".join(
        f"| `{item['name']}` | {item['requests']} | {item['failures']} | "
        f"{item['average_ms']:.2f} ms | {item['p95_ms']:.2f} ms | "
        f"{item['requests_per_second']:.2f} req/s |"
        for item in endpoints
    )
    checks = result["quality_gate"]
    check_rows = "\n".join(
        f"| {name.replace('_', ' ').capitalize()} | {'Pass' if passed else 'Fail'} |"
        for name, passed in checks.items()
    )
    return f"""# Phase 10 performance results

## Decision

**{result['result']}** against the bounded local target in NFR-PERF-001.

This result describes one repeatable local test run. It is not a production capacity statement and does not establish a service-level commitment.

## Workload

| Measure | Observed or configured value |
|---|---:|
| Peak concurrent users | {workload['peak_concurrent_users']} |
| Spawn rate | {workload['spawn_rate_users_per_second']} users/second |
| Run time | {workload['run_time']} seconds |
| Wait time | {workload['wait_time_seconds']} seconds |
| Authenticated read requests | {observations['authenticated_read_requests']} |

## Aggregate observations

| Measure | Observation | Target | Result |
|---|---:|---:|---|
| 95th-percentile response time | {observations['p95_response_ms']:.2f} ms | Below {target['p95_response_ms_below']:.0f} ms | {'Pass' if checks['p95_below_target'] else 'Fail'} |
| Request error rate | {observations['error_rate_percent']:.4f}% | Below {target['error_rate_percent_below']:.0f}% | {'Pass' if checks['error_rate_below_target'] else 'Fail'} |
| Throughput | {observations['throughput_requests_per_second']:.2f} req/s | Observe and report | Recorded |
| Concurrency | {workload['peak_concurrent_users']} users | {target['concurrent_users']} users | {'Pass' if checks['concurrency_reached'] else 'Fail'} |

## Endpoint observations

| Request | Samples | Failures | Average | p95 | Throughput |
|---|---:|---:|---:|---:|---:|
{endpoint_rows}

## Quality gate

| Check | Result |
|---|---|
{check_rows}

## Environment

- Target: `{environment['target']}`
- Operating system: `{environment['operating_system']}`
- Python: `{environment['python']}`
- Locust: `{environment['locust']}`
- Data: unique synthetic accounts in a disposable SQLite database

## Reproduce

From the repository root:

```powershell
{command}
```

Raw CSV and HTML output is written to the ignored `reports/performance/` directory. The runner refuses non-loopback targets and starts the API against an isolated database.
"""


def run_baseline(*, users: int, spawn_rate: int, run_time: str, port: int) -> int:
    if users != 10:
        raise ValueError("The approved local baseline requires exactly 10 users.")
    if spawn_rate <= 0 or spawn_rate > users:
        raise ValueError("Spawn rate must be between 1 and the user count.")
    if not run_time.endswith("s") or not run_time[:-1].isdigit():
        raise ValueError("Run time must be expressed as whole seconds, such as 30s.")

    host = "127.0.0.1"
    base_url = f"http://{host}:{port}"
    ensure_port_available(host, port)
    REPORTS.mkdir(parents=True, exist_ok=True)
    database_path = REPORTS / "workboard-performance.db"
    if database_path.exists():
        database_path.unlink()

    environment = os.environ.copy()
    environment["WORKBOARD_DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
    environment["WORKBOARD_SEEDED_FUNCTIONAL_DEFECTS"] = "false"
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            host,
            "--port",
            str(port),
        ],
        cwd=BACKEND,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )
    raw_result = REPORTS / "baseline-results.json"
    csv_prefix = REPORTS / "locust"
    command = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        str(ROOT / "performance" / "locustfile.py"),
        "--headless",
        "--users",
        str(users),
        "--spawn-rate",
        str(spawn_rate),
        "--run-time",
        run_time,
        "--host",
        base_url,
        "--csv",
        str(csv_prefix),
        "--html",
        str(REPORTS / "locust-report.html"),
        "--result-json",
        str(raw_result),
        "--only-summary",
    ]
    try:
        wait_until_ready(base_url, server)
        completed = subprocess.run(command, cwd=ROOT, env=environment, check=False)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)

    if not raw_result.exists():
        raise RuntimeError("Locust did not write the evaluated result.")
    result = json.loads(raw_result.read_text(encoding="utf-8"))
    TRACKED_RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    display_command = ".venv\\Scripts\\python.exe scripts\\run_performance_baseline.py"
    TRACKED_REPORT.write_text(render_markdown(result, display_command), encoding="utf-8")
    print(f"Phase 10 quality gate: {result['result']}")
    print(f"Results: {TRACKED_REPORT.relative_to(ROOT)}")
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded local WorkBoard performance baseline.")
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--spawn-rate", type=int, default=2)
    parser.add_argument("--run-time", default="30s")
    parser.add_argument("--port", type=int, default=8010)
    options = parser.parse_args()
    return run_baseline(
        users=options.users,
        spawn_rate=options.spawn_rate,
        run_time=options.run_time,
        port=options.port,
    )


if __name__ == "__main__":
    raise SystemExit(main())
