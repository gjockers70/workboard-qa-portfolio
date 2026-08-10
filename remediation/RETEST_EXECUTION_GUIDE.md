# Phase 12 Retest Execution Guide

## Preconditions

Install the backend and test requirements, install the frontend packages, and leave the normal controlled-defect switches disabled. The Selenium fixtures use a disposable Brave profile and synthetic local data.

## Defect-oriented confirmation

From the repository root, run:

```powershell
.venv\Scripts\python.exe -m pytest tests/ui/test_phase3_catalog.py::test_component_and_text_contrast tests/ui/test_phase3_catalog.py::test_responsive_core_workflow tests/accessibility/test_accessibility.py::test_success_and_error_updates_use_live_region_roles tests/accessibility/test_accessibility.py::test_corrected_controls_have_accessible_names_and_heading_order --browser brave
```

Expected result: six passing automated checks. The responsive case expands to three viewport parameters, while the other three selections each run once.

## Risk-based regression

Create or update a synthetic local administrator, export its address and password only for the test process, and run the six approved case nodes:

```powershell
$env:WORKBOARD_ADMIN_PASSWORD = "local-synthetic-password"
Push-Location app\backend
..\..\.venv\Scripts\python.exe -m app.manage create-admin --email "phase12.admin@example.test" --display-name "Phase 12 Administrator"
Pop-Location
Remove-Item Env:WORKBOARD_ADMIN_PASSWORD
$env:WORKBOARD_TEST_USER_EMAIL = "phase12.admin@example.test"
$env:WORKBOARD_TEST_USER_PASSWORD = "local-synthetic-password"
.venv\Scripts\python.exe -m pytest tests/ui/test_functional_regression.py::test_incorrect_password_does_not_create_session tests/ui/test_functional_regression.py::test_member_task_lifecycle tests/ui/test_functional_regression.py::test_blank_task_title_is_rejected tests/ui/test_functional_regression.py::test_search_and_status_filter_apply_together tests/ui/test_functional_regression.py::test_profile_name_persists_across_sessions tests/ui/test_functional_regression.py::test_administrator_team_view_is_read_only_for_member_task --browser brave
```

Expected result: six passing tests covering invalid authentication, member task lifecycle, blank-title validation, combined search and status filtering, profile persistence, and read-only administrator oversight.

## Artifact verification

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/remediation tests/test_management tests/uat --browser brave
```

Expected result: 27 passing checks with no skips. The synthetic administrator variables remain set for this command and the complete suite.

## Complete regression and build

Run the complete suite and frontend build:

```powershell
.venv\Scripts\python.exe -m pytest --browser brave
Remove-Item Env:WORKBOARD_TEST_USER_EMAIL
Remove-Item Env:WORKBOARD_TEST_USER_PASSWORD
cd app\frontend
npm.cmd run build
```

Expected result: 121 passing tests with no skips, followed by a successful production build.

## Result handling

- Record each managed case once in `test-management/TEST_EXECUTIONS.csv` for this cycle.
- Preserve the automated check count separately from the managed case count.
- Link every defect confirmation to one closed defect and one approved case.
- If any command fails or skips a required check, stop the checkpoint, retain the evidence, and follow the failure-handling procedure in the plan.
