# CI/CD and Automated Quality Gates

## What Phase 13 adds

Phase 13 adds a GitHub Actions validation pipeline, a manual performance workflow, an executable gate evaluator, retained test artifacts, and management evidence that maps pipeline results to approved test cases.

Continuous integration matters because the same commands run for every pull request and every push to `main`. A failure becomes visible before a downstream deployment can consume the change. The project does not deploy an environment, so the workflow stops at a release-quality decision rather than implying production delivery.

## Fast workflow

`.github/workflows/quality-gates.yml` runs on pull requests, pushes to `main`, and manual dispatch. It has read-only repository permission, cancels superseded runs on the same ref, and has a 25-minute timeout.

| Stage | Scope | Blocking rule |
|---|---|---|
| Frontend build | TypeScript compile and Vite production build | Build command must exit successfully |
| Unit and artifact checks | Pipeline evaluator, performance helpers and records, management integrity, remediation, and UAT records | Every selected test must pass; no skip is accepted |
| API | Complete API suite | Zero failures, errors, or skips |
| Database | Complete isolated database suite with deprecation warnings treated as errors | Zero failures, errors, or skips |
| Smoke | Sign-in, registration/sign-out, and member task lifecycle in headless Chrome | All three tests must pass |
| Critical regression | Six approved Phase 12 regression cases | 100% pass rate; no skip is accepted |
| Accessibility | Complete axe-core and browser-semantic suite in headless Chrome | Zero failures, errors, or skips |
| Defect gate | Markdown defect register | No Critical defect may remain open |
| Traceability gate | Acceptance criteria and approved test cases | Every acceptance criterion must have case coverage |

The evaluator writes `reports/ci/quality-gates.json` and exits nonzero when any rule blocks. Pytest also writes a JUnit file and a self-contained HTML report for each stage.

## Test services and data

The hosted job starts FastAPI and Vite on loopback interfaces, creates a synthetic administrator, uses a disposable SQLite database under the runner's temporary directory, and runs Chrome headlessly. It generates and masks a new administrator password inside each job, then discards it with the runner. The workflow contains no stored credential, customer information, or persistent database.

The synthetic email in the workflow is a test identifier rather than a deliverable address. If a future integration needs a genuine secret, it must be stored as an encrypted repository or environment secret and exposed only to the job that requires it.

## Artifact retention

Reports, service logs, screenshots, and browser-driver diagnostics are uploaded even when an earlier step fails. GitHub retains the workflow artifact for 14 days. This makes failures diagnosable without storing generated reports in source control.

## Performance trigger boundary

`.github/workflows/performance-baseline.yml` uses `workflow_dispatch` only. It runs the approved 30-second, 10-user loopback baseline and uploads its evidence. It never runs automatically on a pull request or push, so normal feedback remains fast and the project does not present a short local workload as a production service-level test.

## When a gate blocks deployment

All fast-workflow failures are release blockers until the cause is understood. A downstream deployment job should declare `needs: quality-gates` and run only after that job succeeds. Repository branch protection should require the `Build, test, and evaluate` check before merge.

- A build failure blocks because the application artifact is not viable.
- A smoke failure blocks because broader results cannot compensate for a broken critical path.
- An API, database, regression, or accessibility failure blocks because an approved behavior regressed.
- A skipped required test blocks because it leaves the result unknown.
- An open Critical defect or uncovered acceptance criterion blocks because the evidence is incomplete.

The project has no deployment job in Phase 13. Therefore the implemented outcome is a validated release gate, not a deployment claim.

## Local reproduction

The exact hosted commands are readable in the workflow. A complete local equivalent requires the normal Python and frontend dependencies, a running backend and frontend, a synthetic administrator, and Brave substituted for hosted Chrome when reproducing on the verified Windows environment.

After the six JUnit files exist under `reports/ci`, evaluate the decision with:

```powershell
.venv\Scripts\python.exe scripts\evaluate_quality_gates.py --results-dir reports\ci --output reports\ci\quality-gates.json --minimum-regression-pass-rate 100
```

## Failure triage

1. Open the failed job step and its JUnit or HTML report.
2. Use backend, frontend, or browser-driver logs to distinguish service startup from test behavior.
3. Reproduce the exact failed node locally with the same browser and synthetic environment values.
4. Classify a reproducible product failure before creating or reopening a defect.
5. Apply an approved correction, rerun the focused test and impact-based regression, then rerun the complete gate.
6. Do not rerun repeatedly merely to obtain a passing result; an unexplained intermittent result remains a reliability risk.

## Validation boundary at the checkpoint

The workflow structure, evaluator, and every equivalent gate command are validated locally before Phase 13 approval. The first hosted run cannot exist until the approved workflow is committed and pushed. After approval, the hosted run must be monitored to completion and any runner-specific failure corrected before Phase 13 is treated as published successfully.
