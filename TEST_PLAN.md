# WorkBoard Test Plan

## 1. Document control

| Field | Value |
|---|---|
| Project | WorkBoard QA Portfolio |
| Plan status | Draft for Phase 3 review |
| Product baseline | Local React, FastAPI, and SQLite application |
| Test approach | Risk-based, traceable, incremental |
| Cost target | $0 using local and free tools |

Approval of this plan authorizes test design and execution against the stated scope. It does not authorize publication or production deployment.

## 2. Objective

Demonstrate whether WorkBoard satisfies its approved requirements by combining manual functional testing with later UI, API, database, accessibility, integration, performance, and CI validation. The plan emphasizes evidence, reproducibility, controlled defect handling, and honest release reporting.

## 3. Scope

### In scope

- Registration, sign-in, sign-out, and invalid-session recovery
- Profile display and update persistence
- Personal task creation, viewing, editing, completion, reopening, and deletion
- Search and active/completed filtering, including combined conditions
- Member and administrator role behavior
- Task ownership and backend authorization
- User-facing validation and feedback
- Keyboard, screen-reader, semantic, focus, and contrast assessment
- REST API contracts and error handling
- SQLite persistence, uniqueness, ownership, row counts, and state changes
- Local integration between browser, API, and database
- Small local performance baseline
- Simulated remote-session interruption and reconnection behavior
- Simulated UAT and remediation/retest workflow
- CI execution, reports, artifacts, and quality gates

### Out of scope

- Production hosting or production customer data
- Email verification, password reset, or multi-factor authentication
- Enterprise single sign-on
- Native mobile applications
- Destructive security testing
- External-system load or stress testing
- Legal certification of Section 508 or WCAG compliance
- Enterprise Jira, Confluence, or Zephyr Scale administration

## 4. References

- `docs/REQUIREMENTS.md`
- `agile/PRODUCT_BACKLOG.md`
- `agile/USER_STORIES.md`
- `agile/ACCEPTANCE_CRITERIA.md`
- `agile/SPRINT_PLAN.md`
- `test-management/TEST_CASES.csv`

## 5. Test items

| Item | Layer | Primary risks |
|---|---|---|
| React frontend | Browser UI | Incorrect workflow, unclear feedback, keyboard barriers, responsive layout |
| FastAPI service | REST API | Contract failure, missing validation, authentication or authorization failure |
| SQLite database | Persistence | Missing, duplicated, stale, or incorrectly owned records |
| Authentication/session flow | Cross-layer | Unauthorized access, stale session state, unclear recovery |
| Administrator oversight | Cross-layer | Member data exposure or unauthorized mutation |
| CI workflows | Delivery | Tests not executed, reports missing, unsuitable gate behavior |

## 6. Test strategy

### Manual functional testing

Execute critical positive and negative business workflows before automating them. Manual execution establishes expected behavior, reveals usability issues, and confirms that automation will assert the correct outcome.

### Smoke testing

The smoke set covers health, valid sign-in, task creation, task completion, and sign-out. Smoke failures stop broader execution until the environment or build is corrected.

### Regression testing

The regression set grows from stable functional cases, every corrected defect, authorization boundaries, and high-risk integration paths. Regression scope is selected by requirement impact rather than rerunning every case indiscriminately.

### UI automation

Selenium with pytest will automate stable, valuable browser workflows. Page Objects will separate locators and reusable actions from test intent. Explicit waits, stable selectors, synthetic data, cleanup, and failure screenshots will reduce flakiness.

### API and integration testing

Reusable API clients will validate status codes, schemas, authentication, authorization, validation, error handling, and response-time baselines. Integration cases will compare API or UI outcomes with database state.

### Database testing

SQL-based checks will confirm inserts, updates, deletes, uniqueness, null handling, ownership, row counts, and unchanged state after rejected requests. Database tests will use isolated synthetic records.

### Accessibility testing

Automated axe and Lighthouse checks will be combined with WAVE review, keyboard-only execution, contrast measurement, and NVDA testing. Automated results alone cannot establish accessibility or legal compliance.

### Usability testing

Manual exploratory sessions will examine labels, navigation, error clarity, destructive-action confirmation, task discoverability, and recovery behavior. Subjective observations will be separated from requirement failures.

### Performance baseline

A small Locust test will measure response time, throughput, concurrency, and errors against the local API only. It will not run on every commit and will not be represented as production capacity.

### UAT

A simulated business user will attempt goal-oriented scenarios without being coached through failures. Results will distinguish defects, requirement misunderstandings, and enhancements before retest and sign-off status are recorded.

## 7. Manual versus automated coverage

| Keep primarily manual | Automate when stable |
|---|---|
| Keyboard flow and focus order | Sign-in and sign-out smoke flow |
| NVDA announcements and usability | Task CRUD and validation |
| WAVE interpretation | Search and status filters |
| Visual contrast review | Role and ownership API rules |
| UAT observation and communication | API contracts and error responses |
| Exploratory usability assessment | Database persistence and cleanup |
| One-time environment/reconnection observations | Selected repeatable axe checks |

Manual testing remains necessary where human perception, assistive-technology behavior, or business interpretation determines quality. Automation is favored for deterministic, repeatable, high-value regression checks.

## 8. Environments

| Environment | Purpose | Configuration |
|---|---|---|
| Local corrected baseline | Normal development and regression | Controlled defect switches disabled |
| Local functional-defect baseline | Defect detection exercise | Backend functional switch enabled deliberately |
| Local accessibility-defect baseline | Accessibility finding exercise | Frontend accessibility switch enabled deliberately |
| GitHub Actions | Repeatable CI execution | Headless Chrome, ephemeral test data, retained reports |

Initial browser scope is the current stable Chrome release on Windows at desktop and responsive widths. Broader cross-browser coverage is deferred until the Chrome suite is stable.

## 9. Roles and responsibilities

| Role | Responsibility |
|---|---|
| Product owner | Approves requirements, priorities, acceptance criteria, and accepted risks |
| Test engineer | Designs cases, prepares data, executes tests, records evidence, reports defects, and recommends release status |
| Developer | Investigates assigned defects, implements fixes, and identifies changed components |
| UAT participant | Attempts business scenarios, explains expectations, and accepts or rejects outcomes |
| Release stakeholder | Reviews test summary, exceptions, residual risks, and release recommendation |

One person may perform multiple roles in this portfolio simulation, but artifacts will identify the role being represented. Simulated participation will not be presented as real client experience.

## 10. Test data

- Use only synthetic names, reserved domains such as `example.test`, and unique local passwords.
- Create separate member and administrator identities.
- Include active and completed tasks, boundary-length values, duplicate emails, blank inputs, and ownership conflicts.
- Generate unique identifiers so cases can run repeatedly.
- Clean created records after execution when cleanup does not destroy required evidence.
- Never place credentials in tracked files, screenshots intended for publication, or test reports.

## 11. Entry criteria

Test execution begins when:

- Requirements and acceptance criteria for the target story are approved.
- The application starts locally and the health endpoint responds.
- Required accounts and synthetic test data are available.
- The test case has preconditions, steps, and expected results.
- The intended corrected or controlled-defect baseline is identified.
- Known environment blockers are recorded.

## 12. Exit criteria

A release-readiness cycle finishes when:

- All planned Must-requirement cases have an execution status.
- Smoke tests pass.
- No critical functional, authorization, API-contract, or accessibility defect remains open.
- Regression pass rate is at least 95%, excluding documented blocked cases from the denominator.
- Every failed case links to a defect or an approved disposition.
- Fixed blocking defects have passed focused retest and appropriate regression.
- Accessibility results include manual keyboard and screen-reader evidence.
- UAT results and outstanding exceptions are documented.
- The test summary states unresolved risks and a release recommendation.

The 95% regression threshold is a proposed gate, not evidence of current performance. A single failed critical case can block release even when the percentage threshold is met.

## 13. Suspension and resumption criteria

Pause execution when the application cannot start, the database cannot be isolated, smoke testing fails, required synthetic data is unavailable, or results are invalidated by an environment fault. Resume after the blocker is corrected, the smoke set passes, and affected cases are reset or rerun.

## 14. Defect process

1. Reproduce the failure against the identified environment and baseline.
2. Capture exact steps, expected result, actual result, evidence, and linked requirement.
3. Assign severity based on user or system impact and priority based on delivery urgency.
4. Triage as defect, requirement misunderstanding, environment issue, duplicate, or enhancement.
5. Move valid defects through New, Triaged, Assigned, In Progress, and Ready for Retest.
6. Execute focused retest and risk-based regression.
7. Close only when evidence demonstrates the expected behavior or an approved disposition is documented.

## 15. Reporting

Execution records will include case ID, cycle, environment, result, tester role, date, evidence, and linked defect. Reports will provide:

- Planned, executed, passed, failed, blocked, and not-run counts
- Results by test type and requirement priority
- Defects by severity and status
- Regression, accessibility, UAT, and performance summaries
- Unresolved risks and quality-gate outcomes
- Technical release recommendation
- Short stakeholder-facing summary

## 16. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Portfolio scope becomes too large | Incomplete or shallow evidence | Keep each phase reviewable and automate only stable, valuable cases |
| Local environment differs from CI | False failures or missed issues | Record versions, use reproducible configuration, and retain CI artifacts |
| Tests share data | Order dependence and flaky results | Use unique synthetic data and explicit cleanup |
| UI locators change | Brittle Selenium suite | Prefer stable test IDs and behavior-focused Page Objects |
| Retry logic hides defects | False confidence | Allow narrow retries only for a justified external transient condition |
| Accessibility automation is overtrusted | Barriers remain undetected | Require keyboard, NVDA, WAVE, and contrast review |
| Controlled defects are mistaken for production behavior | Misleading portfolio claims | Identify the active baseline in every affected execution |
| Simulated UAT is presented as client work | Misrepresentation | Label every simulated session and resume statement accurately |

## 17. Assumptions and dependencies

- Python, Node.js, Chrome, and Git remain available locally.
- SQLite is the initial database; PostgreSQL portability remains optional.
- The application continues to expose stable test selectors for critical controls.
- GitHub public-repository Actions can be used at no cost within applicable limits.
- NVDA, WAVE, Lighthouse, and the selected accessibility libraries remain available at no cost.
- Schedule and effort change if requirements or supported environments expand.

## 18. Schedule

| Milestone | Planned work | Exit evidence |
|---|---|---|
| Phase 3 | Manual plan and cases | Approved plan and case register |
| Phases 4–5 | Selenium framework and functional regression | Repeatable UI results and failure evidence |
| Phases 6–7 | API and database testing | Contract, authorization, and persistence results |
| Phase 8 | Accessibility testing | Automated and manual findings |
| Phase 9 | Agile management and traceability | Cycles, executions, defects, and matrix |
| Phases 10–12 | Performance, UAT, remediation | Baseline, session results, retest evidence |
| Phases 13–14 | CI, gates, and reporting | Retained artifacts and release recommendation |

## 19. Level-of-effort estimates

These are planning ranges, not guarantees. They assume one contributor learning while implementing and documenting the work.

| Activity | Estimated focused effort | Basis |
|---|---:|---|
| Manual test design | 10–16 hours | Requirements review, cases, test data, peer-style self-review |
| Initial manual execution | 6–10 hours | Functional, usability, role, and recovery checks with evidence |
| Automation framework | 16–28 hours | Fixtures, configuration, Page Objects, data, reporting, cleanup |
| Functional regression automation | 18–30 hours | Stable workflows, negative cases, debugging, flake reduction |
| API and database coverage | 14–24 hours | Reusable clients, contracts, SQL validation, isolation |
| Accessibility assessment | 14–24 hours | Tools, keyboard, NVDA, evidence, remediation guidance |
| UAT preparation and facilitation | 6–10 hours | Scenarios, data, session, triage, retest summary |
| CI and quality gates | 10–18 hours | Workflows, artifacts, headless browser, gate logic |
| Reporting and final documentation | 10–16 hours | Results, limitations, runbook, portfolio cleanup |

LOE is built from scope size, test-data needs, environment setup, automation complexity, evidence requirements, uncertainty, and review/rework allowance. Estimates will be revised using actual execution experience rather than treated as fixed commitments.

## 20. Approval checkpoint

Phase 3 approval confirms that the scope, risk priorities, entry/exit criteria, manual test catalog, and proposed estimates are suitable for the next implementation phase. It does not record any case as executed.

