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

The repository currently contains the approved application, project-management artifacts, manual test suite, and Selenium foundation through Phase 4.

## Project progress

| Phase | Status | Evidence |
|---|---|---|
| Phase 1 — Demo application | Approved and published | React/FastAPI/SQLite application and verified member/admin workflows |
| Phase 2 — Backlog, requirements, and acceptance criteria | Approved and published | [Requirements](docs/REQUIREMENTS.md), [Product backlog](agile/PRODUCT_BACKLOG.md), [User stories](agile/USER_STORIES.md), [Acceptance criteria](agile/ACCEPTANCE_CRITERIA.md), [Sprint plan](agile/SPRINT_PLAN.md) |
| Phase 3 — Manual test plan and cases | Execution approved locally | 37 of 37 cases have a final Pass result; two findings were corrected and passed retest. See the [execution CSV](test-management/TEST_EXECUTIONS.csv) and [formatted execution register](test-management/PHASE_3_EXECUTION_REGISTER.xlsx) |
| Phase 4 — Selenium framework | Approved and published | Browser fixtures, Page Objects, explicit waits, failure screenshots, HTML/JUnit reporting, and verified Brave and Edge smoke tests |
| Phase 5 — Functional and regression automation | Approved and published | Eight Brave UI tests pass, including six tests selected by the regression marker |

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

These switches are for local test execution only and remain disabled by default.

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
