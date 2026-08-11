# WorkBoard QA Portfolio

WorkBoard is a small full-stack task application used to practice software testing across the user interface, REST API, and database layers.

## Application scope

The application includes:

- account registration and login
- authenticated profile retrieval
- profile editing
- personal task creation, editing, completion, deletion, search, and filtering
- administrator read-only oversight of all users' tasks
- React and TypeScript frontend
- FastAPI backend
- SQLite persistence through SQLAlchemy

The repository contains the approved application and test evidence through Phase 13. Hosted validation begins when the approved workflow is pushed.

## Project progress

| Phase | Status | Evidence |
|---|---|---|
| Phase 1 - Demo application | Approved and published | React/FastAPI/SQLite application and verified member/admin workflows |
| Phase 2 - Backlog, requirements, and acceptance criteria | Approved and published | [Requirements](docs/REQUIREMENTS.md), [Product backlog](agile/PRODUCT_BACKLOG.md), [User stories](agile/USER_STORIES.md), [Acceptance criteria](agile/ACCEPTANCE_CRITERIA.md), [Sprint plan](agile/SPRINT_PLAN.md) |
| Phase 3 - Manual test plan and cases | Approved and published | 37 of 37 cases have a final Pass result; two findings were corrected and passed retest. See the [execution CSV](test-management/TEST_EXECUTIONS.csv) and [formatted execution register](test-management/PHASE_3_EXECUTION_REGISTER.xlsx) |
| Phase 4 - Selenium framework | Approved and published | Browser fixtures, Page Objects, explicit waits, failure screenshots, HTML/JUnit reporting, and verified Brave and Edge smoke tests |
| Phase 5 - Functional and regression automation | Approved and published | Eight Brave UI tests pass, including six tests selected by the regression marker |
| Phase 6 - API and web-services testing | Approved and published | Reusable HTTP client, strict response contracts, authentication/authorization coverage, CRUD and validation tests, controlled 5xx handling, and 24 passing API tests |
| Phase 7 - SQL and database testing | Approved and published | Isolated SQLite fixtures, reusable SQL inspection, schema and constraint checks, persistence and row-count validation, API-to-database comparisons, and 16 passing database tests |
| Phase 8 - Accessibility and Section 508 testing | Approved and published | axe-core automation, Lighthouse, WAVE, keyboard and focus checks, NVDA evidence, documented findings, remediation, and retest results in the [accessibility evidence set](accessibility/ACCESSIBILITY_TEST_PLAN.md) |
| Phase 9 - Agile test management and traceability | Approved and published | Jira/Confluence/Zephyr mapping, cycles, executions, defect lifecycle, traceability, and sprint test summary |
| Phase 10 - Performance testing | Approved and published | Loopback-only Locust workload passed at 10 users with 749 authenticated reads, 17 ms p95, 25.45 req/s, and 0.0000% errors |
| Phase 11 - UAT planning and simulated client session | Approved and published | Six passing business scenarios, 20 passing focused checks, 114 passing project tests, one clarified misunderstanding, one deferred enhancement, and no confirmed UAT defect |
| Phase 12 - Remediation and retesting | Approved and published | Four closed defects independently confirmed, six managed regression cases passed, 12 focused checks passed, all 121 project tests passed, and no UAT observation was misclassified as a corrected defect |
| Phase 13 - CI/CD and quality gates | Approved; hosted validation pending | GitHub Actions build and test workflow, manual-only performance trigger, six blocking test groups, executable gate evaluation, 115 passing gate checks, and 132 passing project tests |

## Agile Test Management

Phase 9 connects the local product backlog to execution evidence with a complete workflow: story and acceptance criteria -> test case -> automated check -> test cycle and execution -> defect when applicable -> retest -> final status.

- The [Agile working model and tool mapping](docs/AGILE_TEST_MANAGEMENT.md) explains how local artifacts correspond to Jira stories and bugs, Confluence pages, and Zephyr Scale cases, cycles, and executions without requiring a hosted product.
- [TEST_CASES.csv](test-management/TEST_CASES.csv) contains 55 Zephyr-style cases: 54 approved and one future release case intentionally left Draft.
- [TEST_CYCLES.csv](test-management/TEST_CYCLES.csv) records completed functional, regression, API, database, accessibility, management, performance, and simulated UAT cycles.
- [TEST_EXECUTIONS.csv](test-management/TEST_EXECUTIONS.csv) preserves every Phase 3 attempt and selected trace links from later automated cycles.
- The [defect log](DEFECT_LOG.md) and [triage procedure](agile/DEFECT_TRIAGE.md) use `New -> Triaged -> Assigned -> In Progress -> Ready for Retest -> Retested -> Closed`.
- The [traceability matrix](TRACEABILITY_MATRIX.md) and [machine-readable register](test-management/REQUIREMENTS_TRACEABILITY.csv) show a full path for every story. DEF-P3-001 is the worked failed-execution, correction, retest, and closure example.
- The [sprint test summary](agile/SPRINT_TEST_SUMMARY.md) records that the six-test regression cycle, eight management-integrity tests, and complete 82-test regression passed; it does not claim the final release decision before later phases finish.

## Local setup

### Backend

```powershell
cd app/backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### Frontend

In a second terminal:

```powershell
cd app/frontend
npm install
npm run dev
```

The user interface runs at `http://127.0.0.1:5173`.

Create an account from the registration form. All local records use synthetic test data only.

## Local administrator

Administrator credentials are created locally and are never stored in the repository. From `app/backend`, set a temporary password and run the management command:

```powershell
$env:WORKBOARD_ADMIN_PASSWORD = "choose-a-local-synthetic-password"
.venv\Scripts\python -m app.manage create-admin --email "admin@example.test" --display-name "Test Administrator"
Remove-Item Env:WORKBOARD_ADMIN_PASSWORD
```

Use a synthetic address and a unique local password. The administrator can review all users' tasks but cannot modify tasks owned by another user.

## Controlled defect modes

The normal application starts with corrected behavior. Later test cycles can deliberately activate known defect baselines with environment switches:

- `WORKBOARD_SEEDED_FUNCTIONAL_DEFECTS=true` for the backend baseline
- `VITE_SEEDED_ACCESSIBILITY_DEFECTS=true` for the frontend baseline

During local frontend development, the accessibility baseline can also be opened with `?accessibility-defects=true`. Production builds ignore that query switch. These controls are for local test execution only and remain disabled by default.

## Selenium framework

Install the test dependencies into the project virtual environment:

```powershell
.venv\Scripts\python -m pip install -r requirements-test.txt
```

Most member tests register a unique synthetic account through the browser. The administrator scenario reads a synthetic local administrator from temporary environment variables. Run the smoke marker with:

```powershell
$env:WORKBOARD_TEST_USER_EMAIL = "synthetic.user@example.test"
$env:WORKBOARD_TEST_USER_PASSWORD = "local-synthetic-password"
.venv\Scripts\python -m pytest -m smoke --browser brave
Remove-Item Env:WORKBOARD_TEST_USER_EMAIL
Remove-Item Env:WORKBOARD_TEST_USER_PASSWORD
```

Run the Phase 5 regression marker with:

```powershell
.venv\Scripts\python -m pytest -m regression --browser brave
```

Run the complete browser suite with:

```powershell
.venv\Scripts\python -m pytest tests/ui --browser brave
```

The framework defaults to verified headless Brave execution using a disposable test profile. It writes a self-contained HTML report, JUnit XML, and failure screenshots under the ignored `reports/` directory. Edge is also verified locally and can be selected with `--browser edge`. Google Chrome can be selected with `--browser chrome`, but compatibility is not claimed until that browser completes the suite successfully.

The current local Phase 5 execution has six passing regression tests and eight passing UI tests overall. The sign-out navigation failure discovered during implementation was corrected and passed focused and full-suite retesting.

## API testing

Phase 6 exercises the REST service directly without using the browser. The reusable client keeps endpoint construction and bearer-token handling separate from test intent, while tests retain access to raw responses for negative status and payload assertions.

Run the API suite with a synthetic local administrator configured through temporary environment variables:

```powershell
$env:WORKBOARD_TEST_USER_EMAIL = "synthetic.admin@example.test"
$env:WORKBOARD_TEST_USER_PASSWORD = "local-synthetic-password"
.venv\Scripts\python -m pytest tests/api
Remove-Item Env:WORKBOARD_TEST_USER_EMAIL
Remove-Item Env:WORKBOARD_TEST_USER_PASSWORD
```

The local Phase 6 run has 24 passing tests. Timing checks are single-request development observations, not load-test results or production-capacity claims. Database-state assertions remain assigned to Phase 7.

## Database testing

Phase 7 runs against a new temporary SQLite file for every test. The development database is never used as test data, and the temporary engine uses the same foreign-key configuration as the application.

Run the isolated database suite with:

```powershell
.venv\Scripts\python -m pytest tests/database -W error::DeprecationWarning
```

The suite validates schema columns, required values, unique email enforcement, foreign keys, cascading deletes, salted password storage, inserts, transformations, updates, deletes, owner-specific row counts, unchanged state after rejected authorization, and API results against independent SQL queries. The local Phase 7 run has 16 passing tests with deprecation warnings treated as failures.

## Accessibility testing

Install the frontend development dependencies before running the axe-core suite:

```powershell
cd app/frontend
npm install
cd ../..
.venv\Scripts\python -m pytest tests/accessibility --browser brave -W error::DeprecationWarning
```

Run the reproducible Lighthouse accessibility audit with the local Brave binary:

```powershell
cd app/frontend
$env:CHROME_PATH = "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
npm run audit:accessibility -- http://127.0.0.1:5173/
Remove-Item Env:CHROME_PATH
```

Phase 8 has 10 passing dedicated tests and the complete project regression has 74 passing tests. Lighthouse scored 100, WAVE retests reported 0 errors, 0 contrast errors, and 0 alerts, and NVDA captured success and error announcements. See the [test plan](accessibility/ACCESSIBILITY_TEST_PLAN.md), [findings](accessibility/FINDINGS.md), and [remediation register](accessibility/REMEDIATION_RETEST.md). These results describe the tested local scope and are not a certification or legal-compliance claim.

## Performance testing

Phase 10 uses Locust for a bounded, loopback-only load test of authenticated profile and task reads. The runner starts the API against a disposable SQLite database, creates unique synthetic members, refuses non-loopback targets, and exits nonzero if the measured gate fails.

Run the approved baseline from the repository root:

```powershell
.venv\Scripts\python.exe scripts\run_performance_baseline.py
```

The recorded 30-second run reached 10 concurrent users and completed 749 authenticated reads at 25.45 requests per second, with a combined p95 response time of 17 ms and a 0.0000% request error rate. All 102 project tests also pass in verified headless Brave. See the [performance test plan](performance/PERFORMANCE_TEST_PLAN.md), [evaluated results](performance/PERFORMANCE_RESULTS.md), and [formatted register](test-management/PHASE_10_PERFORMANCE_REGISTER.xlsx).

The portfolio run is a load test at a defined user level. Stress testing searches beyond expected load for a breaking point, soak testing holds traffic for an extended period, and spike testing applies a sudden traffic jump; those three test types remain out of scope. The local observations are not production-capacity or service-level claims.

## User acceptance testing

Phase 11 models a professional UAT workflow without claiming real client experience. A disclosed single-person role-play used an operations-coordinator persona, business-goal scenario prompts, synthetic identities, observation before clarification, issue classification, and a separate Brave replay for technical corroboration.

All six scenarios passed. The session recorded one requirement misunderstanding about the administrator's intentionally read-only team view and one enhancement request for due dates and priority fields. Neither observation is a product defect or failed test, and the enhancement remains deferred for product prioritization.

The focused UAT and management verification passed 20 tests, including two Brave business-workflow replays. The complete project regression passed all 114 tests.

See the [UAT plan](uat/UAT_PLAN.md), [scenario cards](uat/UAT_SCENARIOS.md), [session notes](uat/UAT_SESSION_NOTES.md), [issue and defect log](uat/UAT_DEFECT_LOG.md), [summary](uat/UAT_SUMMARY.md), and [sign-off template](uat/UAT_SIGNOFF_TEMPLATE.md).

## Remediation and retesting

Phase 12 consolidates every genuine defect into an auditable failure-to-closure chain and then independently confirms the corrected behaviors in Brave. The managed cycle contains four defect confirmations and six impact-based regression cases. The focused commands produce 12 automated checks because the responsive compatibility case runs at three viewport widths.

No application change was required in this phase. All four defects had already been corrected and closed in their source cycles, and Phase 11 produced no product defect. The clarified UAT misunderstanding remains non-defect evidence, while the due-date and priority request remains deferred as ENH-002 rather than being represented as a correction.

The complete project suite passed all 121 tests with no skips, and the frontend production build passed.

See the [remediation plan](remediation/REMEDIATION_PLAN.md), [impact analysis](remediation/REGRESSION_IMPACT_ANALYSIS.md), [defect retest matrix](remediation/DEFECT_RETEST_MATRIX.csv), [execution guide](remediation/RETEST_EXECUTION_GUIDE.md), and [Phase 12 summary](remediation/PHASE_12_RETEST_SUMMARY.md).

## CI/CD

Phase 13 adds a GitHub Actions workflow for pull requests, pushes to `main`, and manual dispatch. The job builds the frontend; runs unit and artifact checks, API tests, database tests, headless Selenium smoke and regression tests, and accessibility automation; evaluates blocking defect and traceability rules; and retains JUnit, HTML, screenshot, service-log, and browser-driver evidence for 14 days.

The blocking policy requires every selected test to execute and pass, a 100% critical-regression pass rate, no open Critical defect, and complete acceptance-criteria coverage. The repository has no deployment job, so the workflow produces a release-quality decision without claiming production deployment.

The bounded Phase 10 performance baseline is isolated in a manual-only workflow and does not run on every commit. See the [CI/CD design and quality-gate policy](docs/CI_CD.md) and [Phase 13 validation record](ci/PHASE_13_VALIDATION.md).
