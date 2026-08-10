# Phase 10 performance test plan

## Purpose

Establish a small, repeatable local baseline for NFR-PERF-001 and AC-US010-05. The test measures response time, throughput, basic concurrency, and request error rate for authenticated read operations.

The observations apply only to this local application and recorded environment. They are not production-capacity or service-level claims.

## Test types

| Type | Purpose | Phase 10 use |
|---|---|---|
| Load | Evaluates expected traffic at a defined user level. | Used: 10 concurrent users for 30 seconds. |
| Stress | Increases traffic beyond the expected level to find a breaking point. | Not used; unnecessary for this safe local baseline. |
| Soak | Holds traffic for an extended period to expose degradation or resource leaks. | Not used; the portfolio run is intentionally brief. |
| Spike | Applies a sudden, sharp traffic increase to evaluate recovery and queuing behavior. | Not used; the approved target uses a gradual spawn rate. |

## Scope

Included authenticated reads:

- `GET /api/profile`
- `GET /api/tasks?state=all`
- `GET /api/tasks?search=phase&state=active`

Account registration creates isolated synthetic users before measured reads begin. Registration is excluded from the read percentile and error-rate calculations, but any setup failure fails the quality gate.

Excluded:

- external or shared environments
- frontend rendering and browser timing
- write-operation capacity
- stress, soak, and spike testing
- production sizing or extrapolation

## Workload and target

| Item | Value |
|---|---|
| Tool | Locust 2.46.0 |
| Users | 10 |
| Spawn rate | 2 users per second |
| Duration | 30 seconds |
| Per-user wait | Random 0.2 to 0.5 seconds |
| Data | Unique synthetic accounts in a disposable SQLite database |
| Host restriction | `127.0.0.1` or `localhost` over HTTP with an explicit port |

NFR-PERF-001 passes when all of these conditions are satisfied:

- the 95th-percentile response time across measured authenticated reads is below 500 ms;
- the request error rate across measured authenticated reads is below 1%;
- the run reaches exactly 10 concurrent users;
- at least one authenticated read sample is recorded; and
- account setup completes with no failures.

Throughput is observed and reported in requests per second; no throughput pass threshold is asserted in this first local baseline.

## Procedure

1. Install the pinned test dependencies from `requirements-test.txt`.
2. From the repository root, run `.venv\Scripts\python.exe scripts\run_performance_baseline.py`.
3. The runner confirms port 8010 is unused, starts the API on loopback, and creates a disposable database under the ignored reports directory.
4. Locust spawns 10 users, executes the 30-second workload, and evaluates the gate.
5. Review `performance/PERFORMANCE_RESULTS.md` and `performance/baseline-results.json`.
6. Retain the generated HTML and CSV details under the ignored `reports/performance/` directory for local investigation.

The command exits nonzero if any gate condition fails. A failed baseline must not be presented as ready for review.
