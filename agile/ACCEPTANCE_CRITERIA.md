# Acceptance Criteria

## US-001 — Register and sign in

- **AC-US001-01:** Given a visitor supplies a unique valid synthetic email, display name, and password of at least eight characters, when registration is submitted, then an account is created and an authenticated member session begins.
- **AC-US001-02:** Given an email is already registered, when the same normalized email is submitted again, then registration is rejected with a conflict response and no duplicate user row is created.
- **AC-US001-03:** Given a registered user supplies correct credentials, when sign-in is submitted, then the API returns an access token and the task workspace is displayed.
- **AC-US001-04:** Given an incorrect password or unknown email, when sign-in is submitted, then access is denied with the same clear credential error and no session is stored.
- **AC-US001-05:** Given a new account, when its database record is inspected, then the stored password value is a salted hash rather than the submitted password.

## US-002 — End or recover a session

- **AC-US002-01:** Given an authenticated user, when Sign out is selected, then local session data is removed and the sign-in page is displayed.
- **AC-US002-02:** Given a signed-out user, when a protected API endpoint is requested without a bearer token, then the API returns 401.
- **AC-US002-03:** Given a token is invalid or expired, when the workspace loads, then the stale session is removed and the user receives a sign-in recovery message.
- **AC-US002-04:** Given a valid session, when the page is refreshed without restarting the backend, then the authenticated workspace remains available.

## US-003 — Manage personal tasks

- **AC-US003-01:** Given an authenticated member supplies a valid title and optional description, when the task is submitted, then one owned task is created and displayed.
- **AC-US003-02:** Given a title is blank or whitespace only, when task creation or update is submitted, then validation rejects it and no blank task is stored.
- **AC-US003-03:** Given a title exceeds 120 characters or a description exceeds 1,000 characters, when submitted, then validation rejects the payload.
- **AC-US003-04:** Given an owned task, when its title or description is edited with valid values, then the UI, API response, and database show the new values.
- **AC-US003-05:** Given an active owned task, when Complete is selected, then the task is stored and displayed as completed.
- **AC-US003-06:** Given a completed owned task, when Reopen is selected, then the task is stored and displayed as active.
- **AC-US003-07:** Given an owned task and the user cancels deletion, when the confirmation closes, then the task remains unchanged.
- **AC-US003-08:** Given an owned task and the user confirms deletion, when deletion completes, then the task is absent from the UI, API results, and database.
- **AC-US003-09:** Given a task mutation succeeds, when the updated list is rendered, then a clear success message identifies the completed action.

## US-004 — Find relevant tasks

- **AC-US004-01:** Given tasks with different titles or descriptions, when a case-insensitive matching term is searched, then only matching owned tasks are returned.
- **AC-US004-02:** Given no task matches a search term, when search completes, then an empty-state message is displayed without an error.
- **AC-US004-03:** Given active and completed tasks, when Active is selected, then only active tasks appear.
- **AC-US004-04:** Given active and completed tasks, when Completed is selected, then only completed tasks appear.
- **AC-US004-05:** Given a search term and status filter are both selected, when results load, then every result satisfies both conditions.
- **AC-US004-06:** Given All is selected and search is empty, when results load, then all tasks owned by the member appear.

## US-005 — Maintain a profile

- **AC-US005-01:** Given an authenticated user, when the workspace opens, then the current display name, email identity, and role are retrievable from the profile endpoint.
- **AC-US005-02:** Given a valid nonblank display name, when the profile form is saved, then the new name appears in the header and a success message is displayed.
- **AC-US005-03:** Given a successful display-name update, when the user signs out and signs back in, then the updated name persists.
- **AC-US005-04:** Given a blank or whitespace-only display name, when saved, then validation rejects it and the prior name remains stored.

## US-006 — Review team work

- **AC-US006-01:** Given an administrator, when All users' tasks is selected, then tasks from every user are returned with owner name and email.
- **AC-US006-02:** Given an administrator views another user's task, then edit, complete, reopen, and delete controls are not displayed for that task.
- **AC-US006-03:** Given an administrator uses the member task endpoint with another user's task ID, when an update or delete is attempted, then the API returns 404 without changing the task.
- **AC-US006-04:** Given a member requests the administrator task endpoint, then the API returns 403.
- **AC-US006-05:** Given an administrator switches to My tasks, then only tasks owned by that administrator are displayed and remain editable.

## US-007 — Protect task ownership

- **AC-US007-01:** Given two member accounts, when either member lists tasks, then only tasks owned by that member are returned.
- **AC-US007-02:** Given a member requests another user's task ID for update, then the API returns 404 and the database row is unchanged.
- **AC-US007-03:** Given a member requests another user's task ID for deletion, then the API returns 404 and the database row remains present.
- **AC-US007-04:** Given a missing or invalid bearer token, when any task endpoint is requested, then the API returns 401 without revealing task data.
- **AC-US007-05:** Given an authorization failure, when database state is compared before and after the request, then row values and counts are unchanged.

## US-008 — Use core workflows accessibly

- **AC-US008-01:** Given keyboard-only input, when registration, sign-in, task creation, filtering, profile update, and sign-out are performed, then every required control is reachable and operable in a logical order.
- **AC-US008-02:** Given keyboard focus is on an interactive control, then a visible focus indicator meets the project's contrast target.
- **AC-US008-03:** Given the page is inspected programmatically, then each form control and actionable button has an accessible name describing its purpose.
- **AC-US008-04:** Given an error or success message appears, then a screen reader announces the new message without forcing focus away from the current workflow.
- **AC-US008-05:** Given page headings and regions are reviewed, then their hierarchy and names communicate the page structure without a skipped level inside a content section.
- **AC-US008-06:** Given text and interactive component colors are measured, then applicable combinations meet WCAG 2.2 AA contrast targets.
- **AC-US008-07:** Given automated accessibility checks pass, then manual keyboard and NVDA checks are still completed and recorded before the criterion is considered fully tested.
- **AC-US008-08:** Given the current stable Chrome browser at widths of 320, 760, and 1280 pixels, when core workflows are exercised, then content remains readable and required controls remain visible and operable without unintended horizontal scrolling.

## US-009 — Continue after interruption

- **AC-US009-01:** Given a valid local session, when the page refreshes, then the user remains authenticated and no task mutation is repeated.
- **AC-US009-02:** Given the backend restarts with an invalidated signing key, when the old session is used, then the user is returned to sign-in with a recovery message.
- **AC-US009-03:** Given a temporary simulated connection failure, when a read or mutation cannot complete, then the interface reports the failure and does not report success.
- **AC-US009-04:** Given the connection is restored and the user signs in again, then role and task-ownership enforcement match the pre-interruption rules.

## US-010 — Make a release decision

- **AC-US010-01:** Given the release candidate, then every Must requirement links to at least one acceptance criterion and test case.
- **AC-US010-02:** Given the smoke cycle completes, then all smoke tests pass before broader release testing continues.
- **AC-US010-03:** Given API contract and authorization tests complete, then no critical contract or authorization test remains failed.
- **AC-US010-04:** Given accessibility testing completes, then no critical accessibility defect remains open and manual results are included in the decision.
- **AC-US010-05:** Given the local performance baseline runs, then observed response time, throughput, concurrency, and error rate are reported against NFR-PERF-001 without presenting the result as production capacity.
- **AC-US010-06:** Given all planned cycles finish, then a test summary records execution counts, open defects, accepted exceptions, unresolved risks, and a release recommendation.
