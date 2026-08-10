# WorkBoard Test Automation Architecture

## Phase 4 framework foundation

Phase 4 created the reusable Selenium foundation and one authenticated smoke test.

## Phase 5 automation boundary

Phase 5 adds browser-functional and regression coverage for registration, sign-in rejection, sign-out, task creation and mutation, validation, combined search and filtering, profile persistence, and administrator read-only oversight. Direct API assertions, SQL validation, accessibility evaluation, and performance measurement remain assigned to later phases.

Each member scenario registers a unique synthetic identity through the interface. Tests own uniquely named tasks and delete them when safe. The administrator scenario reads credentials from environment variables because privileged credentials must not be stored in source control.

## Layers

```text
pytest test intent
    ↓
fixtures and configuration
    ↓
Page Objects and reusable waits
    ↓
Selenium WebDriver
    ↓
WorkBoard browser interface
```

The browser test interacts only through visible user-interface behavior. Later API and database helpers will remain separate so a UI assertion does not silently bypass the interface it is meant to test.

## Repository structure

```text
framework/
├── config/          environment-backed settings
├── drivers/         browser creation and options
├── pages/           Page Objects and explicit waits
└── utilities/       evidence and reusable helpers
tests/
└── ui/              browser test intent and assertions
conftest.py           pytest fixtures, hooks, and CLI options
pytest.ini            markers and report configuration
```

## Page Object Model

Page Objects centralize locators, waits, and reusable page actions. Tests can describe intent such as signing in without duplicating selectors or WebDriver calls. When the interface changes, a locator is updated in one place.

Tradeoffs:

- Small pages require additional files and abstractions.
- Oversized Page Objects can hide test intent or become difficult to maintain.
- Assertions should generally remain in tests so Page Objects do not decide whether behavior is correct.
- A Page Object should represent a meaningful page or component boundary, not every individual element.

## Browser configuration

The framework supports `brave`, `chrome`, and `edge` through `WORKBOARD_BROWSER` or `--browser`. Brave is the verified default for Phase 4 and starts through a local automation endpoint with a disposable profile that is removed after each test. Edge is also verified locally. Google Chrome remains the intended CI target and must be verified before a Google Chrome compatibility claim is made.

Headless execution is the default. Use `--headed` only when observing or troubleshooting the UI adds value.

## Wait strategy

The framework uses explicit waits for visible or clickable conditions. It does not set an implicit wait and does not use fixed sleep calls.

Fixed sleeps are unreliable because they wait too long on fast systems and may still be too short on slow systems. Condition-based waits proceed when the interface is actually ready and fail with a meaningful timeout when it is not.

## Selector strategy

- Prefer stable `data-testid` attributes for controls used by automation.
- Use semantic text or role-based selectors when the user-facing name is itself part of the expected behavior.
- Avoid deeply nested CSS selectors, generated class names, and absolute XPath expressions.
- Keep selectors inside Page Objects rather than tests.

## Test data and credentials

Member scenarios create unique synthetic accounts through the browser. The administrator scenario reads credentials from `WORKBOARD_TEST_USER_EMAIL` and `WORKBOARD_TEST_USER_PASSWORD`. Values are never stored in the repository. Tests use synthetic identities only.

## Phase 5 execution profiles

- `smoke` covers release-gating browser workflows.
- `functional` covers user-visible behavior against approved requirements.
- `negative` covers rejected credentials and invalid values.
- `regression` covers stable workflows rerun after changes.

The markers overlap intentionally because one scenario can be both functional and regression-critical. Marker selection changes execution scope; it does not duplicate the test implementation.

## Reporting and failure evidence

Every run produces:

- Self-contained HTML report
- JUnit XML report
- UTC-timestamped screenshot when a test fails after browser setup

Reports and screenshots are local artifacts and are excluded from source control. CI will retain them as workflow artifacts in a later phase.

## Retry policy

No blanket retry plugin is enabled. A failed test should be investigated for product behavior, environment problems, bad synchronization, shared data, or unstable selectors. A narrow retry may be introduced only for a documented transient dependency that cannot be controlled and must not conceal a reproducible failure.

## Command-line examples

```powershell
$env:WORKBOARD_TEST_USER_EMAIL = "synthetic.user@example.test"
$env:WORKBOARD_TEST_USER_PASSWORD = "local-synthetic-password"
.venv\Scripts\python -m pytest -m smoke --browser brave
Remove-Item Env:WORKBOARD_TEST_USER_EMAIL
Remove-Item Env:WORKBOARD_TEST_USER_PASSWORD
```

Use only local synthetic credentials. A missing credential causes the authenticated test to skip rather than embedding a password in test code.
