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

The repository currently contains the approved application and test evidence through Phase 9.

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

## Agile Test Management

Phase 9 connects the local product backlog to execution evidence with a complete workflow: story and acceptance criteria -> test case -> automated check -> test cycle and execution -> defect when applicable -> retest -> final status.

- The [Agile working model and tool mapping](docs/AGILE_TEST_MANAGEMENT.md) explains how local artifacts correspond to Jira stories and bugs, Confluence pages, and Zephyr Scale cases, cycles, and executions without requiring a hosted product.
- [TEST_CASES.csv](test-management/TEST_CASES.csv) contains 49 Zephyr-style cases: 47 approved and two future release cases intentionally left Draft.
- [TEST_CYCLES.csv](test-management/TEST_CYCLES.csv) records completed functional, regression, API, database, and accessibility cycles plus explicitly planned future cycles.
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
