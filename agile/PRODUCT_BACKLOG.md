# Product Backlog

## Backlog conventions

- Priority uses Must, Should, or Could.
- Story points are relative planning estimates, not hours.
- Status is honest current project state: `Done`, `In test`, or `Planned`.
- Sprint targets remain planned until execution evidence is recorded.

## Product stories

| Rank | ID | Type | Summary | Priority | Points | Status | Proposed sprint |
|---:|---|---|---|---|---:|---|---|
| 1 | US-001 | Story | Register and sign in with synthetic credentials | Must | 5 | Done | Sprint 1 |
| 2 | US-002 | Story | End or recover an authenticated session | Must | 3 | Done | Sprint 1 |
| 3 | US-003 | Story | Create, view, edit, complete, reopen, and delete personal tasks | Must | 8 | Done | Sprint 1 |
| 4 | US-007 | Story | Enforce task ownership at the backend | Must | 5 | Done | Sprint 1 |
| 5 | US-004 | Story | Search and filter personal tasks | Must | 5 | Done | Sprint 1 |
| 6 | US-006 | Story | Review all users' tasks as an administrator | Must | 5 | Done | Sprint 1 |
| 7 | US-008 | Story | Complete core workflows with keyboard and assistive technology | Must | 8 | Done | Sprint 3 |
| 8 | US-005 | Story | View and update a profile display name | Should | 3 | Done | Sprint 1 |
| 9 | US-009 | Story | Recover predictably after refresh, interruption, or reconnection | Should | 5 | Done | Sprint 3 |
| 10 | US-010 | Story | Evaluate release readiness from traceable quality evidence | Must | 8 | In test | Sprint 4 |

## Quality-engineering enablers

| Rank | ID | Type | Summary | Priority | Points | Status | Proposed sprint |
|---:|---|---|---|---|---:|---|---|
| 11 | QE-001 | Task | Design and execute manual functional test cases | Must | 8 | Done | Sprint 1 |
| 12 | QE-002 | Task | Build Selenium and pytest framework with failure evidence | Must | 13 | Done | Sprint 2 |
| 13 | QE-003 | Task | Automate critical functional and regression workflows | Must | 13 | Done | Sprint 2 |
| 14 | QE-004 | Task | Build reusable REST API tests | Must | 8 | Done | Sprint 2 |
| 15 | QE-005 | Task | Validate persistence and ownership with SQL | Must | 8 | Done | Sprint 2 |
| 16 | QE-006 | Task | Execute automated and manual accessibility assessments | Must | 13 | Done | Sprint 3 |
| 17 | QE-007 | Task | Run controlled defect, remediation, and regression cycles | Must | 8 | Done | Sprint 3 |
| 18 | QE-008 | Task | Facilitate and document a simulated UAT session | Should | 8 | Planned | Sprint 4 |
| 19 | QE-009 | Task | Establish a safe local performance baseline | Could | 5 | Planned | Sprint 4 |
| 20 | QE-010 | Task | Add CI workflows, reports, artifacts, and quality gates | Must | 13 | Planned | Sprint 4 |

## Backlog decision rules

- Must stories and their acceptance criteria take precedence over convenience features.
- A story cannot enter test execution until its acceptance criteria and test data are reviewable.
- A failed acceptance criterion becomes a defect only after the failure is reproduced and evidence is recorded.
- Critical regression or authorization failures block release readiness.
- Enhancements discovered during UAT return to the backlog instead of being mislabeled as defects.

## Deferred enhancements

| ID | Summary | Reason deferred |
|---|---|---|
| ENH-001 | Password-reset workflow | Adds email infrastructure without improving the core test objective. |
| ENH-002 | Task due dates and priority | Useful future regression scope after the base framework is stable. |
| ENH-003 | Cross-browser execution matrix | Deferred until one stable Chrome workflow exists. |
| ENH-004 | PostgreSQL execution profile | SQLite keeps early local setup simple; PostgreSQL remains a later portability exercise. |
