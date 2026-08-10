# Phase 10 performance results

## Decision

**Pass** against the bounded local target in NFR-PERF-001.

This result describes one repeatable local test run. It is not a production capacity statement and does not establish a service-level commitment.

## Workload

| Measure | Observed or configured value |
|---|---:|
| Peak concurrent users | 10 |
| Spawn rate | 2.0 users/second |
| Run time | 30 seconds |
| Wait time | 0.2-0.5 seconds |
| Authenticated read requests | 749 |

## Aggregate observations

| Measure | Observation | Target | Result |
|---|---:|---:|---|
| 95th-percentile response time | 17.00 ms | Below 500 ms | Pass |
| Request error rate | 0.0000% | Below 1% | Pass |
| Throughput | 25.45 req/s | Observe and report | Recorded |
| Concurrency | 10 users | 10 users | Pass |

## Endpoint observations

| Request | Samples | Failures | Average | p95 | Throughput |
|---|---:|---:|---:|---:|---:|
| `GET /api/profile` | 224 | 0 | 4.31 ms | 17.00 ms | 7.61 req/s |
| `GET /api/tasks` | 395 | 0 | 4.71 ms | 18.00 ms | 13.42 req/s |
| `GET /api/tasks?search&state` | 130 | 0 | 4.77 ms | 17.00 ms | 4.42 req/s |

## Quality gate

| Check | Result |
|---|---|
| Read samples recorded | Pass |
| P95 below target | Pass |
| Error rate below target | Pass |
| Concurrency reached | Pass |
| Setup succeeded | Pass |

## Environment

- Target: `http://127.0.0.1:8010`
- Operating system: `Windows-11-10.0.26200-SP0`
- Python: `3.12.10`
- Locust: `2.46.0`
- Data: unique synthetic accounts in a disposable SQLite database

## Reproduce

From the repository root:

```powershell
.venv\Scripts\python.exe scripts\run_performance_baseline.py
```

Raw CSV and HTML output is written to the ignored `reports/performance/` directory. The runner refuses non-loopback targets and starts the API against an isolated database.
