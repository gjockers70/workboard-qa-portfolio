# Proposed Agile Sprint Plan

## Status and intent

This is a portfolio simulation plan. The application baseline was implemented during project Phase 1 before these sprint artifacts were created. The plan therefore describes how the remaining test workload will be organized; it does not retroactively claim completed sprint ceremonies or executions.

## Cadence

- Simulated sprint length: one week of part-time portfolio work
- Planning unit: relative story points
- Daily coordination: short written update covering completed work, next work, and blockers
- Review checkpoint: working evidence and artifact review at the end of each sprint
- Retrospective: one improvement to retain and one process change for the next sprint

## Sprint 1 — Requirements and manual functional baseline

**Goal:** Establish approved requirements and execute the first traceable manual functional cycle.

Planned items:

- US-001 through US-007
- QE-001 manual functional test design and execution
- Initial test data and environment checklist
- First defect records only if execution produces reproducible failures

Exit target:

- Every Must product story has approved acceptance criteria.
- Critical account, task, role, and authorization workflows have manual cases.
- The first functional cycle has execution evidence and honest pass/fail status.

## Sprint 2 — Automation and backend validation

**Goal:** Create maintainable Selenium, API, integration, and database coverage for critical risks.

Planned items:

- QE-002 through QE-005
- Smoke and regression markers
- Page Object Model and reusable fixtures
- API client, SQL helpers, synthetic data setup, and cleanup
- Failure screenshots and machine-readable reports

Exit target:

- Critical smoke workflow runs repeatably.
- API authorization and CRUD contracts are covered.
- Database state is compared with API or UI outcomes.
- Flaky behavior is investigated rather than hidden with broad retries.

## Sprint 3 — Accessibility, reliability, and remediation

**Goal:** Execute the controlled baselines, document findings, remediate selected failures, and prove them with regression tests.

Planned items:

- US-008 and US-009
- QE-006 and QE-007
- axe, Lighthouse, WAVE, keyboard, and NVDA assessments
- Controlled functional and accessibility baseline cycles
- Defect triage, remediation, retest, and regression evidence

Exit target:

- Each accessibility finding records evidence, severity, relevance, remediation, and retest result.
- At least one failed case follows the full defect lifecycle.
- No claim of legal compliance is made from automated results alone.

## Sprint 4 — UAT, performance, CI, and release decision

**Goal:** Complete stakeholder-oriented validation and produce a defensible release recommendation.

Planned items:

- US-010
- QE-008 through QE-010
- Simulated UAT session and retest
- Small local performance baseline
- CI workflows, quality gates, retained artifacts, and summary reporting

Exit target:

- UAT outcomes distinguish defects, misunderstandings, and enhancements.
- Performance results are bounded to the local test environment.
- CI executes the appropriate suites and retains evidence.
- The final summary provides a technical result and a short stakeholder summary.

## Capacity and estimation assumptions

- Story points compare uncertainty, effort, and coordination; they are not converted directly to hours.
- Initial estimates will be revised after Sprint 1 reveals actual test-design and execution pace.
- Accessibility review and automation-framework work carry higher uncertainty than simple manual cases.
- Performance and UAT tasks remain small so the project stays safe and reproducible at no cost.
- Scope moves before quality gates are weakened when capacity is exceeded.

## Jira-style workflow

`Backlog → Selected for Sprint → In Progress → Ready for Test → In Test → Ready for Retest → Done`

Defects follow:

`New → Triaged → Assigned → In Progress → Ready for Retest → Retested → Closed`

A story reaches Done only when its acceptance criteria have execution evidence and any blocking defects are closed or explicitly accepted with a documented risk.

