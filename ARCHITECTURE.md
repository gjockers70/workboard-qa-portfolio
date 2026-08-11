# WorkBoard Quality Engineering Architecture

## Purpose

WorkBoard separates a small full-stack application from the tools that evaluate it. The design keeps test intent readable, prevents one layer from silently validating itself, and supports repeatable local and hosted execution.

The application is intentionally compact. The framework, evidence chain, and operating discipline are the primary portfolio focus.

## System under test

```text
Browser
  |
  v
React + TypeScript + Vite          http://127.0.0.1:5173
  |
  | JSON over HTTP
  v
FastAPI + Pydantic                 http://127.0.0.1:8000
  |
  v
SQLAlchemy + SQLite                local or disposable database
```

The frontend provides registration, sign-in, profile editing, personal task CRUD, search, state filtering, and an administrator read-only team view. The API owns validation, authentication, authorization, and persistence rules. SQLite provides the verified local database implementation.

Two disabled-by-default environment switches reproduce approved historical defect baselines. Corrected-baseline runs keep both switches disabled.

## Test architecture

```text
                            requirements and acceptance criteria
                                          |
                                          v
manual cases -----> test intent -----> pytest collection -----> reports
                          |                    |                    |
              +-----------+----------+---------+---------+          |
              |                      |                   |          |
              v                      v                   v          v
       Selenium + pages       REST client +        SQL inspector   JUnit/HTML/
              |               contracts                 |          screenshots
              v                      v                   v
          React UI ------------> FastAPI ------------> SQLite
              |                      |                   |
              +----------- cross-layer comparisons -----+

CSV management records <---- traceability, cycles, executions, defects, retests
GitHub Actions -----------> build, selected gates, policy evaluation, artifacts
```

Each layer answers a different question:

- UI checks prove that a user can observe and complete behavior through the browser.
- API checks prove the service contract independently of interface rendering.
- Database checks prove persistence, constraints, ownership, and unchanged state.
- Integration checks prove service results agree with independent database state.
- Accessibility checks combine repeatable rules with manual human judgment.
- Management checks prove that plans, cases, executions, defects, and summaries reconcile.
- Delivery checks prove that the fast quality policy can be reproduced on a hosted runner.

## Repository structure

```text
app/
|-- frontend/                  React application
`-- backend/app/              FastAPI application and management command
framework/
|-- accessibility/            axe-core browser integration
|-- clients/                  HTTP client and response contracts
|-- config/                   environment-backed settings
|-- data/                     synthetic user and task factories
|-- database/                 independent SQL inspection
|-- drivers/                  browser creation and cleanup
|-- management/               test-register parsing and validation
|-- pages/                    Page Objects and explicit waits
`-- utilities/                runtime evidence helpers
tests/
|-- accessibility/            automated accessibility checks
|-- api/                      service and authorization checks
|-- ci/                       workflow and gate contracts
|-- database/                 schema, persistence, and integration checks
|-- documentation/            portfolio-document integrity checks
|-- performance/              runner and result-record checks
|-- remediation/              correction-chain checks
|-- reporting/                summary and decision reconciliation
|-- test_management/          case, cycle, execution, and traceability checks
|-- uat/                      artifact checks and browser replays
`-- ui/                       Selenium smoke, functional, and regression checks
accessibility/                plans, manual evidence, findings, and retests
agile/                        backlog, stories, sprint, triage, and summaries
test-management/              CSV and formatted management registers
uat/                          simulated UAT records
performance/                  safe workload and bounded results
remediation/                  retest and regression evidence
docs/                         operating and specialist guidance
.github/workflows/            quality-gate and performance workflows
```

## Page Object Model

Page Objects in `framework/pages/` centralize selectors, condition-based waits, and meaningful reusable interactions such as registration, sign-in, task creation, filtering, and profile update. Tests keep their own assertions so the expected result remains visible at the point of test intent.

Benefits:

- one controlled location for locator maintenance;
- less duplicated WebDriver code;
- readable workflows that describe user intent;
- shared synchronization behavior; and
- smaller changes when stable interface contracts move.

Tradeoffs:

- even a small interface requires additional files;
- oversized Page Objects can hide test intent;
- page methods can become fragile when they model incidental layout rather than behavior; and
- assertions inside Page Objects can couple interaction code to one test outcome.

The project therefore uses Page Objects for interaction and waiting, and test modules for assertions and risk-specific setup.

## Browser and driver boundary

`framework/drivers/browser.py` supports `brave`, `chrome`, and `edge` through `WORKBOARD_BROWSER` or `--browser`.

- Brave is the verified local default. It starts with a disposable profile and a local debugging endpoint, then Selenium attaches through ChromeDriver.
- Chrome is exercised by the hosted quality-gate selections.
- Edge has limited local smoke evidence.

These results do not constitute a complete cross-browser or device matrix. Every driver receives a page-load timeout and a fixed initial viewport. Browser profiles are disposable test state and must not be retained as portfolio evidence.

## Synchronization and selector policy

Page Objects use explicit conditions such as visibility, clickability, changed text, or expected task sets. Fixed sleeps are not used to synchronize assertions because they wait unnecessarily on fast systems and can still expire too early on slower systems.

Selectors prefer stable `data-testid` values and semantic identifiers over styling classes, document position, or long CSS paths. A selector should identify the behavior contract, not the current visual arrangement.

There is no blanket retry plugin. A failed check is investigated as a possible product, test, environment, data, or synchronization issue. A narrow retry would require a documented external transient condition and must not conceal a reproducible failure.

## REST client and contract boundary

`framework/clients/workboard_api.py` owns base URL handling, REST paths, bearer-token headers, request construction, timeouts, and normalized service-error handling. It returns raw HTTP responses so negative tests can inspect exact status and response content.

`framework/clients/contracts.py` defines strict independent response models. Rejecting unexpected fields helps reveal contract drift and avoids importing the backend's internal response classes into the tests that evaluate it.

The implemented interface is REST. The conceptual SOAP comparison, including XML envelope construction, authentication, schema validation, and fault handling, is documented in [docs/WEB_SERVICES_TESTING.md](docs/WEB_SERVICES_TESTING.md). No SOAP endpoint or execution is claimed.

## Database and integration boundary

`app/backend/app/database.py` provides the shared SQLAlchemy engine factory. SQLite connections enable foreign-key enforcement explicitly. `WORKBOARD_DATABASE_URL` allows a test or hosted runner to select a disposable file without embedding credentials or changing source.

`framework/database/inspector.py` uses independent parameterized SQL for users, tasks, row counts, ownership, and combined search/state results. Tests compare these queries with API outcomes, including proof that rejected authorization attempts leave records unchanged.

Every database test receives a new temporary SQLite file, builds the application schema, and overrides only the FastAPI database dependency. This prevents ordering contamination and protects the local development database.

PostgreSQL migrations and portability execution remain outside the validated scope.

## Accessibility boundary

`framework/accessibility/axe.py` runs axe-core rules against the current browser state. Automated regression is combined with Lighthouse, WAVE, keyboard-only operation, focus review, contrast checks, semantic inspection, and NVDA output recorded under `accessibility/`.

Automated tools cannot determine every reading-order, interaction, language, cognition, or assistive-technology issue. The architecture therefore retains manual evidence and does not treat an automated pass as certification or a legal-compliance determination.

## Configuration, data, and credentials

`framework/config/settings.py` reads URLs, browser selection, binary path, headless mode, waits, and reusable privileged test credentials from the environment. Privileged values are not hard coded; per-test member passwords are generated synthetic data, and negative tests use deliberately fictional inputs.

Most UI scenarios register unique synthetic members through the interface. Data factories add unique tokens to accounts and task titles so parallel or repeated runs do not collide. Privileged scenarios create a synthetic administrator through the backend management command and receive its email and password from temporary environment variables.

Generated databases, reports, screenshots, profiles, build output, dependency directories, and environment files are excluded from source control. Only reviewed, sanitized portfolio images and durable decision records are tracked.

## Evidence and management flow

Pytest writes a self-contained HTML report and JUnit XML. A browser failure after successful driver setup also writes a UTC-timestamped screenshot. CI retains stage reports, service logs, screenshots, and browser-driver diagnostics for 14 days.

The management chain is:

```text
Requirement
-> acceptance criterion
-> approved test case
-> automated or manual check
-> test cycle
-> execution attempt
-> defect when applicable
-> focused retest
-> regression
-> final status
```

Markdown holds readable intent and decisions. CSV files are the machine-readable source for cases, cycles, executions, and traceability. XLSX files are formatted review views. Original failed attempts remain in execution history after a retest passes.

`framework/management/` provides the reusable register loaders and consistency helpers used by management, reporting, remediation, and delivery checks.

## CI/CD boundary

`.github/workflows/quality-gates.yml` runs on pull requests, pushes to `main`, and manual dispatch. It installs dependencies, builds the frontend, runs fast artifact and product checks, evaluates the blocking policy, stops local services, and uploads evidence even when an earlier gate fails.

The quality-gate evaluator requires:

- all required result files;
- zero failures, errors, or required skips;
- 100% critical-regression pass rate;
- no open Critical defect; and
- complete acceptance-criteria coverage.

The performance baseline has a separate manual-only workflow. The repository has no deployment job. A passing workflow supports a scoped release decision but does not prove production deployment or production readiness.

Direct pushes to `main` currently land before the workflow completes because branch protection is not configured. A future protected-branch workflow should require the `Build, test, and evaluate` check before merge.

## Deliberate limits

- The frontend API address is fixed to the two local loopback ports used by the project.
- SQLite is the only executed database implementation.
- Browser coverage is intentionally bounded rather than exhaustive.
- Performance execution is short, local, and safe rather than a production-capacity exercise.
- Remote-access evidence uses local simulations; genuine remote infrastructure and controlled latency remain design-only.
- UAT is a disclosed simulation.
- Jira, Confluence, and Zephyr Scale are represented by local artifacts rather than hosted administration.
- The project produces release-quality evidence but does not deploy a production system.

These boundaries are tracked in [TEST_STRATEGY.md](TEST_STRATEGY.md), [TEST_PLAN.md](TEST_PLAN.md), and [TEST_SUMMARY_REPORT.md](TEST_SUMMARY_REPORT.md).
