# WorkBoard Test Strategy

## 1. Purpose

This document defines how WorkBoard quality is evaluated and how test effort is selected, implemented, maintained, and used for release decisions. It explains the testing approach and decision rules; [TEST_PLAN.md](TEST_PLAN.md) separately defines the planned scope, roles, schedule, estimates, entry criteria, and delivery checkpoints.

The strategy is risk based. Authentication, authorization, task ownership, data integrity, critical user workflows, accessibility barriers, and misleading success feedback receive the strongest coverage because failures in those areas have the greatest user or release impact.

## 2. Quality objectives

The test approach is designed to provide evidence that:

- members can authenticate and manage only their own work;
- administrators can review team work without gaining unauthorized mutation rights;
- user-interface, REST API, and persisted database state agree;
- invalid input and interrupted operations fail clearly without creating false success;
- corrected defects remain corrected under focused retest and impact-based regression;
- critical workflows remain usable with keyboard and assistive-technology support;
- the bounded local workload meets its defined development baseline;
- every release recommendation is traceable to requirements, cases, executions, defects, and retained evidence.

## 3. Guiding principles

1. Test behavior at the lowest useful layer, then add cross-layer coverage where integration risk warrants it.
2. Keep browser assertions focused on behavior visible through the interface; do not bypass the interface to make a UI test pass.
3. Use independent API contracts and SQL queries so tests do not merely repeat application implementation details.
4. Automate deterministic, repeatable, high-value checks. Keep judgment-based accessibility, usability, and business interpretation primarily manual.
5. Treat a test failure as evidence to investigate, not as permission to rerun until it passes.
6. Preserve failed attempts and link them to triage, correction, retest, and final status.
7. Use only synthetic identities, isolated databases, and environment-backed credentials.
8. State evidence boundaries explicitly. Local results do not establish production capacity, legal compliance, or real-client acceptance.

## 4. Risk model

| Risk area | Potential effect | Primary controls |
|---|---|---|
| Authentication and session recovery | Unauthorized access or misleading signed-in state | UI negative tests, API authentication contracts, refresh and invalid-session recovery |
| Authorization and ownership | One user reads or changes another user's records | API denial checks, database unchanged-state checks, administrator read-only regression |
| Task persistence and transformations | Lost, duplicated, stale, or incorrectly filtered work | Browser CRUD regression, API contracts, independent SQL comparison |
| Critical workflow regression | A release cannot support normal member work | Smoke suite, selected critical regression, blocking pipeline gates |
| Accessibility barriers | Keyboard or screen-reader users cannot complete a task | axe-core, browser semantics, keyboard review, Lighthouse, WAVE, NVDA, remediation retest |
| Interrupted or slow interaction | Duplicate mutations, false success, or changed authorization | Local interruption and refresh tests plus documented design-only remote scenarios |
| Test unreliability | False confidence or wasted investigation | Explicit waits, stable selectors, isolated data, deterministic cleanup, no blanket retry |
| Incomplete evidence | A release decision cannot be defended | Traceability checks, JUnit and HTML results, failure screenshots, defect and retest records |

Priority is based on user impact, likelihood, change exposure, and detectability. Critical authentication, authorization, smoke, and corrected-defect checks run more often than exploratory or environment-specific assessments.

## 5. Test layers and responsibilities

### Browser interface

Selenium tests exercise registration, login, logout, validation, profile persistence, task CRUD, search and filtering, navigation, role behavior, responsive behavior, recovery, and negative paths. Page Objects in [framework/pages](framework/pages) own locators, waits, and reusable interactions, while assertions remain in [tests/ui](tests/ui) so expected behavior stays visible in test intent.

Smoke coverage answers whether critical paths are usable enough for broader testing. Functional coverage evaluates individual requirements. Regression coverage selects stable, high-risk workflows and every corrected-defect area. Browser tests also support cross-layer confidence, but direct persistence assertions remain in the database layer.

### REST API and web services

The reusable client in [framework/clients/workboard_api.py](framework/clients/workboard_api.py) constructs requests and bearer-token headers. Independent response contracts in [framework/clients/contracts.py](framework/clients/contracts.py) validate status, structure, content, authentication, authorization, invalid input, error handling, and controlled service failure behavior.

REST is the implemented web-service interface. A comparable SOAP test would construct an XML envelope, set the required content type and action, validate namespaces and an XML schema, and distinguish a SOAP Fault from an HTTP transport error. WorkBoard has no SOAP endpoint, so no SOAP execution or interoperability claim is made.

### Database and integration

Database tests create an isolated SQLite database, build the application schema, and verify columns, nullability, uniqueness, foreign keys, cascading behavior, password storage, inserts, updates, deletes, transformations, ownership, and row counts. Queries in [framework/database/inspector.py](framework/database/inspector.py) remain independent of API response construction.

Integration checks compare API results and rejected operations with database state. This proves that a correct response is backed by the expected persistence behavior and that authorization failures leave records unchanged.

### Accessibility and usability

Automated axe-core and browser-semantic checks provide repeatable regression coverage. Lighthouse and WAVE add tool-specific review, while keyboard-only and NVDA execution evaluate focus, announcements, reading order, dialog behavior, and human interpretation that automation cannot determine reliably. Findings, remediation, and limitations are recorded in the [accessibility evidence set](accessibility/ACCESSIBILITY_TEST_PLAN.md).

Automated success is not treated as accessibility certification or a legal-compliance determination. Manual observations remain required for the criteria identified in the accessibility plan.

### Performance baseline

The Locust module measures response time, throughput, concurrency, and request error rate against the loopback-only application. It is a short development baseline with a fixed safe workload, not a stress, soak, spike, service-level, or production-capacity test. The workload is excluded from every-commit execution and uses the manual workflow described in [docs/CI_CD.md](docs/CI_CD.md).

### User acceptance testing

The UAT exercise uses business-goal scenarios, synthetic data, observation before clarification, and explicit classification of defects, misunderstandings, and enhancements. It is a disclosed simulation and does not represent a real client engagement or customer sign-off. See [uat/UAT_PLAN.md](uat/UAT_PLAN.md) for facilitation and disposition rules.

### Remote-session concepts

Executed local checks cover refresh, simulated request interruption, reconnection, false-success prevention, and authorization consistency. Login over a genuine remote session, elapsed token timeout, controlled latency, and remote-display infrastructure remain design-only. The evidence and claim boundary are detailed in [docs/REMOTE_ACCESS_TESTING.md](docs/REMOTE_ACCESS_TESTING.md).

### Remediation, reporting, and delivery gates

Each confirmed defect retains its original failed execution, triage decision, approved correction, passing focused retest, and relevant regression result. The [defect log](DEFECT_LOG.md) and [Phase 12 retest matrix](remediation/DEFECT_RETEST_MATRIX.csv) preserve that chain.

GitHub Actions builds the frontend and runs artifact, API, database, smoke, critical-regression, and accessibility stages. The executable evaluator blocks on a missing result, failure, error, required skip, regression below the configured threshold, an open Critical defect, or missing acceptance-criteria coverage. Performance remains separately triggered.

## 6. Automation selection

| Prefer automation when | Prefer manual or tool-assisted assessment when |
|---|---|
| The expected result is deterministic and repeatable | Human perception or interpretation determines quality |
| The behavior protects a critical or frequently changed path | The scenario is exploratory or performed once per environment |
| Data setup and cleanup can be isolated safely | Assistive-technology output must be heard and interpreted |
| Failure can be diagnosed from stable evidence | Business-user questions or usability observations must be facilitated |
| The check adds value at browser, API, database, or pipeline level | The automation cost exceeds the regression value |

Automation is not selected merely to increase test count. Duplicate coverage is intentional only when layers answer different risk questions, such as an API authorization response and an independent database unchanged-state assertion.

## 7. Environments and test data

| Environment | Use | Boundary |
|---|---|---|
| Windows 11 with headless or headed Brave | Primary local browser execution and manual observation | Local workstation evidence only |
| Local Edge smoke selection | Limited compatibility evidence | Not a full browser matrix |
| GitHub-hosted Ubuntu with headless Chrome | Repeatable build and blocking quality gates | Hosted runner evidence, not production |
| Isolated SQLite files | API, database, pipeline, and performance data | No PostgreSQL portability claim |
| Loopback FastAPI and Vite services | Functional and bounded performance execution | No external target or network-service claim |

Tests generate unique synthetic accounts and task titles. Privileged credentials are passed through environment variables and created for the current local or hosted run. Databases, browser profiles, reports, logs, and screenshots are disposable or ignored unless intentionally retained as sanitized portfolio evidence. Real personal information, customer records, production credentials, and external-system test data are prohibited.

Controlled defect switches reproduce approved historical baselines locally. They are disabled by default, must not be enabled in a corrected-baseline release run, and do not count as open defects merely because the switch exists.

## 8. Reliability and flake prevention

- Prefer stable `data-testid`, semantic names, and behavior-focused selectors over layout-dependent paths.
- Use explicit condition-based waits; fixed sleeps are not used to synchronize browser assertions.
- Create unique synthetic records and isolate database fixtures to prevent order dependence.
- Clean owned test data when cleanup is safe, and use disposable environments where complete cleanup is simpler.
- Capture the failing node, environment, report, screenshot, and relevant service or driver logs before changing code.
- Reproduce a suspected failure and classify product, test, data, or environment cause before creating a defect.
- Do not enable blanket retries. A narrow retry requires a documented uncontrollable transient condition and must not hide a reproducible failure.
- Treat a skipped required test as incomplete evidence, not as a passing result.

## 9. Entry, exit, and blocking gates

Execution begins when the approved requirement and case versions are known, the corrected baseline is selected, required services are healthy, synthetic data and credentials are available, and the chosen browser and dependencies are installed.

A release-quality decision requires:

- every planned gate result to exist;
- zero failures, errors, or required skips in the selected stages;
- all smoke checks to pass;
- the configured critical-regression pass threshold to be met;
- no open Critical defect;
- every approved acceptance criterion to have managed case coverage;
- every confirmed correction to have focused retest and appropriate regression evidence;
- residual risks and exclusions to be stated in the final summary.

A failed gate blocks the release-quality decision until the cause is understood and the approved correction, focused retest, impact-based regression, and complete applicable gate pass. The repository does not deploy a production environment, so gate success is not a deployment claim.

## 10. Evidence and traceability

Pytest produces self-contained HTML and JUnit results, and browser failures produce timestamped screenshots when a driver is available. Hosted runs retain reports, service logs, screenshots, and driver diagnostics for the configured artifact period. Generated runtime artifacts remain outside source control unless a sanitized example is intentionally selected for durable documentation.

The evidence chain is:

`Requirement -> Acceptance criterion -> Test case -> Automated or manual check -> Test cycle -> Execution -> Defect when applicable -> Retest -> Final status`

Readable links are summarized in [TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md); machine-readable sources are maintained under [test-management](test-management). Current release metrics and evidence boundaries belong in [TEST_SUMMARY_REPORT.md](TEST_SUMMARY_REPORT.md), rather than being copied into this strategy and allowed to become stale.

## 11. Maintenance and change control

For each approved product or requirement change:

1. identify affected requirements, data, components, interfaces, and users;
2. update acceptance criteria and case links before changing expected results;
3. select focused tests and regression by impact and risk;
4. update Page Objects, clients, contracts, inspectors, or fixtures without weakening assertions;
5. execute the focused selection, relevant regression, and required pipeline gates;
6. record new failures and retests without overwriting history;
7. update the test summary when the evidence changes the release decision or its limitations.

Selectors, schemas, browser versions, dependencies, accessibility rules, and hosted runner behavior are reviewed when related changes occur. Deferred enhancements remain backlog items until separately approved; they are not silently introduced as defect corrections.

## 12. Limitations

- Testing uses a small demonstration application and synthetic data.
- SQLite is validated; PostgreSQL execution and migration behavior are not.
- Browser evidence is strongest for local Brave and hosted gate selections in Chrome; it is not a comprehensive browser or device matrix.
- Remote-session infrastructure, controlled latency, and elapsed timeout behavior are not executed.
- Performance evidence is a short loopback baseline and does not establish production capacity.
- Accessibility evidence is sampled and environment-specific and does not establish formal conformance or certification.
- UAT is simulated and does not establish real-client participation or acceptance.
- There is no production deployment, production monitoring, paid test-management administration, or external-system testing.

These limitations are accepted for the portfolio scope and must be reconsidered before applying the strategy to a production release.
