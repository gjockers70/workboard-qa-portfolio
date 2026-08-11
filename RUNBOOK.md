# WorkBoard Test Execution Runbook

## Purpose

This runbook provides a repeatable Windows PowerShell procedure for preparing WorkBoard, starting the local application, executing its test suites, preserving evidence, troubleshooting failures, and cleaning up safely.

Use it with the [test plan](TEST_PLAN.md), [automation architecture](ARCHITECTURE.md), [CI/CD quality-gate policy](docs/CI_CD.md), and [final test summary](TEST_SUMMARY_REPORT.md). All commands below begin at the repository root unless a step explicitly changes directory.

## Operating rules

- Use one Python virtual environment at the repository root: `.venv`.
- Use only synthetic identities and task data. Reserved addresses under `example.test` are suitable.
- Keep passwords and other secrets in temporary environment variables. Never place them in source, screenshots, reports, command history intended for publication, or issue records.
- Keep the controlled defect switches disabled unless a documented test explicitly requires a seeded baseline.
- Treat every failure, error, blocked test, or skip as an incomplete result until its cause is understood.
- Do not repeatedly rerun a failing test merely to obtain a passing result.
- Preserve the original failure evidence before correcting code, data, configuration, or documentation.
- Run performance work only against the loopback target created by the supplied runner.

## Prerequisites

- Windows PowerShell
- Python 3.11 or later
- Node.js 22.12 or later and npm compatible with the committed frontend lockfile; Node.js 24 is used locally and in CI
- Brave, Chrome, or Edge for browser tests
- Git for recording the exact revision under test

Brave is the default local browser. Its default executable location is:

```text
C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe
```

## First-time setup

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r app\backend\requirements.txt -r requirements-test.txt
npm.cmd ci --prefix app\frontend
```

Use `npm ci` so the installed frontend dependency set matches `app/frontend/package-lock.json`.

Confirm the primary tools:

```powershell
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe -m pytest --version
npm.cmd --version
```

## Prepare the synthetic administrator

The administrator management command and the running backend must use the same database. The normal local procedure uses the ignored database at `app/backend/workboard.db`.

In the PowerShell window that will later run the tests:

```powershell
$env:WORKBOARD_TEST_USER_EMAIL = "synthetic.admin@example.test"
$env:WORKBOARD_TEST_USER_PASSWORD = "choose-a-unique-local-password"
$env:WORKBOARD_ADMIN_PASSWORD = $env:WORKBOARD_TEST_USER_PASSWORD

Push-Location app\backend
..\..\.venv\Scripts\python.exe -m app.manage create-admin `
  --email $env:WORKBOARD_TEST_USER_EMAIL `
  --display-name "Synthetic Test Administrator"
Pop-Location

Remove-Item Env:WORKBOARD_ADMIN_PASSWORD
```

The password must contain at least 12 characters. Keep `WORKBOARD_TEST_USER_EMAIL` and `WORKBOARD_TEST_USER_PASSWORD` in this test window until authenticated UI and API testing is complete. If a disposable database is selected with `WORKBOARD_DATABASE_URL`, set the identical value before creating the administrator and before starting the backend.

## Start the local application

### Terminal 1: backend

From the repository root:

```powershell
Push-Location app\backend
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app `
  --host 127.0.0.1 `
  --port 8000
```

Leave this terminal running. The API is available at `http://127.0.0.1:8000`, and its interactive reference is at `http://127.0.0.1:8000/docs`.

### Terminal 2: frontend

From the repository root:

```powershell
npm.cmd --prefix app\frontend run dev -- --port 5173 --strictPort
```

Leave this terminal running. The user interface is available at `http://127.0.0.1:5173`.

## Readiness check

In the test terminal, verify both services before executing browser or API coverage:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
(Invoke-WebRequest -UseBasicParsing -Uri http://127.0.0.1:5173/).StatusCode
```

Expected results:

- the health response contains `status` equal to `ok`;
- the frontend response status is `200`;
- the administrator environment variables remain present in the test terminal;
- the controlled defect variables are absent or set to `false`.

Check the active values without printing the password:

```powershell
$env:WORKBOARD_TEST_USER_EMAIL
$env:WORKBOARD_DATABASE_URL
$env:WORKBOARD_SEEDED_FUNCTIONAL_DEFECTS
$env:VITE_SEEDED_ACCESSIBILITY_DEFECTS
```

An empty database URL means the normal ignored local database is in use. Do not print `WORKBOARD_TEST_USER_PASSWORD`.

## Normal test commands

Browser and API commands require the local services and the prepared administrator. Database tests use isolated temporary databases.

### Frontend production build

```powershell
npm.cmd --prefix app\frontend run build
```

### Smoke tests

```powershell
.venv\Scripts\python.exe -m pytest -m smoke --browser brave
```

### Functional and regression browser tests

```powershell
.venv\Scripts\python.exe -m pytest tests\ui --browser brave
.venv\Scripts\python.exe -m pytest -m regression --browser brave
```

Use `--headed` only when visual observation is needed for investigation:

```powershell
.venv\Scripts\python.exe -m pytest -m smoke --browser brave --headed
```

### API tests

```powershell
.venv\Scripts\python.exe -m pytest tests\api
```

### Database and integration tests

```powershell
.venv\Scripts\python.exe -m pytest tests\database -W error::DeprecationWarning
```

### Accessibility automation

```powershell
.venv\Scripts\python.exe -m pytest tests\accessibility `
  --browser brave `
  -W error::DeprecationWarning
```

Automated accessibility results must be considered with the keyboard, WAVE, Lighthouse, and NVDA procedures in the [accessibility test plan](accessibility/ACCESSIBILITY_TEST_PLAN.md). They do not establish legal compliance or certification.

### UAT support checks

```powershell
.venv\Scripts\python.exe -m pytest tests\uat --browser brave
```

These checks support the disclosed simulated workflow in the [UAT plan](uat/UAT_PLAN.md); they are not evidence of a real client engagement.

### Complete project regression

```powershell
.venv\Scripts\python.exe -m pytest --browser brave
```

Review the terminal summary and generated reports. A run with a failure, error, or skip is not a completed all-pass regression.

### Documentation image refresh

Refresh the tracked workspace image only through the supplied disposable capture:

```powershell
.venv\Scripts\python.exe scripts\capture_documentation_images.py --workspace
```

After the complete repository regression passes with zero failures, errors, or skips, capture the top of that generated HTML report:

```powershell
.venv\Scripts\python.exe scripts\capture_documentation_images.py `
  --report `
  --expected-tests 157
```

The expected count must equal the complete collected suite; update the argument whenever the suite inventory changes. The script rejects a mismatched count, any non-passing result, any skip, a personal machine path, or a non-synthetic email address before capture.

Inspect both files under `docs/images/` before retaining them. The workspace uses a disposable database and synthetic identity. The report image must correspond to the successful run being described and must not expose a credential, token, or unrelated environment value.

### Bounded performance baseline

The performance runner starts and stops its own API on port `8010`, uses a disposable database, and refuses non-loopback targets:

```powershell
.venv\Scripts\python.exe scripts\run_performance_baseline.py
```

Run it only when deliberately refreshing the approved baseline. It updates `performance/baseline-results.json` and `performance/PERFORMANCE_RESULTS.md`; review those tracked changes before retaining them. See the [performance test plan](performance/PERFORMANCE_TEST_PLAN.md).

## Evidence locations

| Evidence | Location | Handling |
|---|---|---|
| Default pytest HTML report | `reports/pytest-report.html` | Generated locally; ignored by Git |
| Default JUnit report | `reports/junit.xml` | Generated locally; ignored by Git |
| Selenium failure screenshots | `reports/screenshots/` | Generated only after browser setup and a failed test |
| Browser-driver diagnostics | `reports/chromedriver.log` | Use for startup and session failures |
| CI stage reports and gate decision | `reports/ci/` | Local equivalent of hosted evidence |
| Accessibility raw reports | `reports/` | Interpret with the tracked accessibility records |
| Performance raw evidence | `reports/performance/` | Created by the bounded runner |
| Approved performance record | `performance/PERFORMANCE_RESULTS.md` | Tracked decision record |
| Manual cases, cycles, and executions | `test-management/` | Preserve attempt history and trace links |
| Defect lifecycle | `DEFECT_LOG.md` | Record confirmed defects and retests |
| UAT records | `uat/` | Separate defects, misunderstandings, and enhancements |
| Release decision | `TEST_SUMMARY_REPORT.md` | Scoped technical and stakeholder summary |

The hosted quality-gate workflow retains its uploaded artifact for 14 days. See the [CI/CD documentation](docs/CI_CD.md) for its exact stages and blocking rules.

Before rerunning a failed command, preserve the relevant report, screenshot, log, test node ID, revision, browser, environment, expected result, and actual result. Generated evidence is intentionally ignored by Git; only reviewed summaries and management records belong in source control.

## Troubleshooting

### Selenium browser failure

1. Confirm the backend and frontend readiness checks pass.
2. Confirm the selected browser is installed and not awaiting an update or first-run dialog.
3. For Brave, verify the default path or set an explicit local path:

   ```powershell
   $env:WORKBOARD_BROWSER_BINARY = "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
   ```

4. Run one focused test with `--headed` and observe browser startup without changing the test.
5. Review `reports/chromedriver.log` and any screenshot under `reports/screenshots/`.
6. Confirm ports `8000` and `5173` belong to the intended WorkBoard services.
7. If the browser or driver version is incompatible, update the local browser or the pinned Selenium dependency deliberately, then rerun focused and regression coverage.

Do not add fixed sleeps or a blanket retry to conceal startup, selector, synchronization, or product failures. The framework's selector, wait, and retry policies are documented in [ARCHITECTURE.md](ARCHITECTURE.md).

### Flaky test

1. Preserve the first failure report, driver log, screenshot, node ID, and test data identifiers.
2. Run the exact node once in the same environment to determine whether the failure is reproducible.
3. Check explicit wait conditions, stable selectors, unique synthetic data, cleanup, shared database state, and test ordering.
4. Compare headed and headless behavior only as a diagnostic; do not accept a mode-specific unexplained pass.
5. Record an intermittent result as a reliability risk until the cause is controlled.
6. Add a narrow retry only for a documented transient dependency that cannot be controlled, and prove that it cannot hide a reproducible product defect.

### API test failure

1. Verify `http://127.0.0.1:8000/health` responds successfully.
2. Confirm `WORKBOARD_API_URL` is unset or points to the intended local API.
3. Confirm the synthetic administrator exists in the same database used by the backend.
4. Capture the HTTP method, path, sanitized request, response status, response body, and expected contract.
5. Review the backend terminal before changing the reusable client in `framework/clients/workboard_api.py` or its strict contracts.
6. Distinguish an environment or fixture failure from a reproducible service-contract defect.

Never place bearer tokens or passwords in retained evidence.

### Database mismatch

1. Record the effective `WORKBOARD_DATABASE_URL` for the administrator command and backend without exposing credentials.
2. Confirm both processes use the same URL. An unset value selects `app/backend/workboard.db`.
3. Reproduce database behavior with the isolated suite before inspecting the development database manually.
4. Compare API results with the independent SQL inspection methods in `framework/database/inspector.py`.
5. Check uniqueness, foreign-key enforcement, ownership, row counts, transaction rollback, and cleanup.
6. Do not edit a row manually to make a failing assertion pass. Correct the application, fixture, or expected result after triage, then rerun focused and integration coverage.

### Accessibility regression

1. Confirm `VITE_SEEDED_ACCESSIBILITY_DEFECTS` is absent or `false` and that no defect-mode query parameter is active.
2. Preserve the axe result, page state, browser, viewport, and screenshot when useful.
3. Reproduce the affected workflow with keyboard-only operation.
4. Review focus order and visibility, names and labels, semantics, error announcements, reflow, and contrast as applicable.
5. Use WAVE, Lighthouse, or NVDA for the method assigned in the [accessibility plan](accessibility/ACCESSIBILITY_TEST_PLAN.md).
6. Link a confirmed finding to the relevant requirement and accessibility reference, correct it, and run focused plus impact-based regression.

A passing automated scan does not replace manual keyboard or screen-reader evaluation.

### CI failure

1. Open the failing `Build, test, and evaluate` step rather than relying only on the overall status.
2. Download the retained artifact and inspect its JUnit, HTML, service log, screenshot, gate decision, and driver log.
3. Identify whether the failure occurred during dependency installation, build, service startup, test execution, gate evaluation, cleanup, or artifact upload.
4. Reproduce the exact workflow command locally with equivalent environment values and the appropriate local browser.
5. Check runner-only path, permission, shell, browser, and timing differences.
6. Correct the cause, run focused and impact-based tests, then rerun the complete gate.

Do not rerun CI repeatedly without explaining an intermittent failure. The repository has no deployment job; a passing workflow is release-gate evidence, not production deployment evidence.

### Missing test data

1. Verify `WORKBOARD_TEST_USER_EMAIL` is present without printing the password.
2. Recreate or update the synthetic administrator with the procedure above.
3. Confirm the administrator command and backend use the same database.
4. Let member scenarios generate their own unique synthetic accounts and tasks.
5. Do not reuse a production account, customer record, personal address, or shared password.
6. If a test skips because credentials are missing, stop and correct the setup; do not report that run as complete.

### Failed regression suite

1. Treat the failed suite as a blocked release gate.
2. Preserve the report and original failed execution instead of overwriting or deleting it.
3. Reproduce the smallest failing node and classify product, test, data, or environment cause.
4. Link a confirmed product failure to the requirement, acceptance criterion, test case, execution, and defect.
5. Apply an approved correction, run focused retest, run impact-based regression, and then run the complete suite.
6. Close a defect only when the expected result and regression evidence both pass.

Use the [defect log](DEFECT_LOG.md), [traceability matrix](TRACEABILITY_MATRIX.md), and [remediation guide](remediation/RETEST_EXECUTION_GUIDE.md).

### UAT defect escalation

1. Allow the simulated participant to complete the attempt before clarifying the workflow.
2. Record the business goal, expected result, actual result, observation, question, and evidence.
3. Compare the result with the approved requirement before classifying it.
4. Distinguish a confirmed defect from a requirement misunderstanding, enhancement request, or environment issue.
5. For a defect, assign severity and priority independently, link the UAT scenario and acceptance criterion, and enter it in `uat/UAT_DEFECT_LOG.md` and the main defect workflow when applicable.
6. Escalate Critical or Major product impact immediately to the represented product owner and test lead roles; do not proceed to sign-off with an unexplained blocker.
7. Coordinate correction, focused retest, regression, and documented disposition before updating sign-off status.

Follow the [UAT plan](uat/UAT_PLAN.md) and preserve the disclosed simulated-session boundary.

### Report-generation failure

1. Confirm `pytest-html` is installed in the root virtual environment:

   ```powershell
   .venv\Scripts\python.exe -m pip show pytest-html
   ```

2. Confirm the repository `reports` directory is writable and that a previously opened report is not locked by another application.
3. Review the terminal for the first report-plugin or filesystem error.
4. Run one focused passing test with explicit output paths:

   ```powershell
   .venv\Scripts\python.exe -m pytest tests\ci\test_workflow_artifacts.py `
     --html=reports\report-check.html `
     --self-contained-html `
     --junitxml=reports\report-check.xml
   ```

5. Verify both files exist and contain the executed test count.
6. If tests pass but required reports are absent or incomplete, treat the evidence stage as failed and correct report generation before publishing results.

## Escalation and evidence discipline

Escalate when a smoke path fails, a Critical or Major defect is confirmed, authorization is inconsistent, required data cannot be prepared safely, accessibility blocks core keyboard or screen-reader use, CI cannot reproduce a local pass, or evidence cannot support the reported result.

Every escalation should include:

- repository revision and tested baseline;
- date, environment, browser, and relevant dependency versions;
- test case and automated node IDs;
- synthetic data identifiers without passwords or tokens;
- exact reproduction steps;
- expected and actual results;
- sanitized logs, report paths, and screenshots;
- requirement, acceptance criterion, and defect links;
- severity, priority, owner role, next action, and retest scope.

Never delete a failed execution after a passing retest. Preserve the sequence `Fail -> defect -> correction -> retest -> final status` in the management records. The [manual execution guide](test-management/MANUAL_EXECUTION_GUIDE.md) contains the corresponding case-level recording procedure.

## Stop and cleanup

1. Stop the frontend and backend with `Ctrl+C` in their exact terminals.
2. Return Terminal 1 to the repository root if needed:

   ```powershell
   Pop-Location
   ```

3. Remove temporary environment variables from every terminal where they were set:

   ```powershell
   Remove-Item Env:WORKBOARD_TEST_USER_EMAIL -ErrorAction SilentlyContinue
   Remove-Item Env:WORKBOARD_TEST_USER_PASSWORD -ErrorAction SilentlyContinue
   Remove-Item Env:WORKBOARD_ADMIN_PASSWORD -ErrorAction SilentlyContinue
   Remove-Item Env:WORKBOARD_DATABASE_URL -ErrorAction SilentlyContinue
   Remove-Item Env:WORKBOARD_BROWSER_BINARY -ErrorAction SilentlyContinue
   Remove-Item Env:WORKBOARD_SEEDED_FUNCTIONAL_DEFECTS -ErrorAction SilentlyContinue
   Remove-Item Env:VITE_SEEDED_ACCESSIBILITY_DEFECTS -ErrorAction SilentlyContinue
   ```

4. Confirm the local endpoints no longer respond. If a process remains, identify the exact listener before stopping it:

   ```powershell
   Get-NetTCPConnection -State Listen -LocalPort 8000,5173 `
     -ErrorAction SilentlyContinue |
     Select-Object LocalAddress,LocalPort,OwningProcess
   ```

   Stop only a verified WorkBoard process by its specific process ID. Do not terminate every Python, Node.js, or browser process on the machine.

5. Keep `reports/` until triage and review are complete. It is ignored by Git.
6. The default database contains only local synthetic data and is ignored by Git. To remove it, first stop the backend and display the exact resolved target:

   ```powershell
   $workboardDatabase = Resolve-Path -LiteralPath app\backend\workboard.db `
     -ErrorAction SilentlyContinue
   $workboardDatabase.Path
   ```

   After confirming that the path is the repository's `app/backend/workboard.db`, remove only that file:

   ```powershell
   Remove-Item -LiteralPath $workboardDatabase.Path
   ```

   This permanently deletes the local synthetic accounts and tasks. It does not affect tracked test evidence.

7. Finish with a source-control check:

   ```powershell
   git status -sb
   ```

Generated reports, browser profiles, build output, local databases, and environment files should remain untracked. Investigate any unexpected file before staging changes.
