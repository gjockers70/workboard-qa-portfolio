# WorkBoard Requirements Baseline

## Purpose

This document defines the approved behavior that later manual and automated tests will evaluate. It describes the product baseline, not test results. A requirement is considered covered only after it is linked to acceptance criteria and executed test cases.

## Business requirements

| ID | Requirement | Priority |
|---|---|---|
| BR-001 | Members must be able to manage a private list of work items through a clear browser interface. | Must |
| BR-002 | Administrators must be able to review work across users without changing another user's work. | Must |
| BR-003 | Core account and task workflows must be usable with a keyboard and common assistive technology. | Must |
| BR-004 | Release stakeholders must receive traceable evidence for functional, regression, accessibility, API, and database quality. | Must |

## Functional requirements

### Accounts and sessions

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-AUTH-001 | A visitor can register with a unique email address, display name, and password of at least eight characters. | Must | BR-001 |
| FR-AUTH-002 | A registered user can sign in with the correct email and password; incorrect credentials return a clear error without creating a session. | Must | BR-001 |
| FR-AUTH-003 | A signed-in user can sign out, and an invalid or expired token returns the user to the sign-in page. | Must | BR-001 |
| FR-PROFILE-001 | A signed-in user can view and update a nonblank display name, and the updated value persists after signing out and back in. | Should | BR-001 |

### Task management

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-TASK-001 | A member can create a task with a required title of 1–120 characters and an optional description of no more than 1,000 characters. | Must | BR-001 |
| FR-TASK-002 | A member can view their tasks with title, description, and current completion state. | Must | BR-001 |
| FR-TASK-003 | A member can edit the title and description of a task they own. | Must | BR-001 |
| FR-TASK-004 | A member can complete and reopen a task they own. | Must | BR-001 |
| FR-TASK-005 | A member can delete a task they own after confirming the action. | Must | BR-001 |
| FR-TASK-006 | A member can search task titles and descriptions and filter results by all, active, or completed state. | Must | BR-001 |

### Roles and authorization

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-ADMIN-001 | An administrator can switch between personal tasks and a team view containing all users' tasks with owner identification. | Must | BR-002 |
| FR-ADMIN-002 | Team oversight is read-only for tasks owned by another user. | Must | BR-002 |
| FR-AUTHZ-001 | A user cannot view, edit, complete, reopen, or delete another user's task through member task endpoints. | Must | BR-001, BR-002 |

## Nonfunctional requirements

### Accessibility and usability targets

| ID | Requirement | Priority |
|---|---|---|
| NFR-ACC-001 | Core registration, sign-in, profile, task, filtering, and sign-out workflows can be completed with a keyboard alone. | Must |
| NFR-ACC-002 | Form controls and actionable buttons have programmatic names that describe their purpose. | Must |
| NFR-ACC-003 | Validation, authentication, and success feedback is exposed to assistive technology without requiring focus to move to the message. | Must |
| NFR-ACC-004 | Keyboard focus is visibly apparent, and text and interactive controls meet the project's WCAG 2.2 AA contrast targets. | Must |
| NFR-ACC-005 | Page headings and regions communicate a logical structure without skipped heading levels in a content section. | Should |

These are verification targets for Section 508-oriented testing. They do not constitute a legal compliance claim.

### Security, reliability, compatibility, and performance targets

| ID | Requirement | Priority |
|---|---|---|
| NFR-SEC-001 | Passwords are stored as salted hashes, authorization is enforced by the backend, and credentials are not committed to source control. | Must |
| NFR-DATA-001 | Project data uses synthetic identities and contains no production credentials, customer information, or real personal data. | Must |
| NFR-REL-001 | A page refresh retains a valid local session; an invalidated session produces a clear recovery path. | Should |
| NFR-REMOTE-001 | After a short simulated connection interruption, the user receives a recoverable error and authorization remains unchanged after reconnection. | Should |
| NFR-COMPAT-001 | Core workflows operate in the current stable Chrome browser at desktop and narrow responsive widths from 320 to 1280 pixels. | Should |
| NFR-PERF-001 | During the bounded local baseline test, authenticated read endpoints target a 95th-percentile response time below 500 ms at 10 concurrent users with less than 1% request errors. | Could |

Phase 10 evaluated this target with a repeatable local baseline. The recorded result applies only to that bounded environment and is not a production service-level commitment.

## Data rules

- Email addresses used in testing must use reserved or clearly fictional domains such as `example.test`.
- Passwords must be unique synthetic test values and must not match personal or production credentials.
- Test cases must create or identify their own records and clean them up when safe to do so.
- No test depends on execution order or data left by an unrelated test.

## Controlled defect baselines

The application contains disabled switches for later defect-detection exercises. When enabled in a local test environment, the functional baseline intentionally violates selected requirements:

| Baseline condition | Expected requirement impact |
|---|---|
| Profile update reports success without persisting the new name | FR-PROFILE-001 |
| Search combined with a status filter returns tasks from the wrong state | FR-TASK-006 |
| Frontend accessibility baseline removes selected labels, names, feedback semantics, focus visibility, contrast, and heading structure | NFR-ACC-002 through NFR-ACC-005 |

These switches are test controls, not open defects. Defect records will be created only when a planned test execution observes and documents a failure.

## Out of scope

- Email delivery or email-address verification
- Password recovery and multi-factor authentication
- Production hosting, billing, or customer data
- Native mobile applications
- Changes to another user's tasks from the administrator team view
- Enterprise single sign-on
- Production-scale load, stress, soak, or security penetration testing

## Requirement change control

Changes to a Must requirement require the following before implementation:

1. Record the requested change and business reason.
2. Identify affected user stories, acceptance criteria, tests, and risks.
3. Re-estimate the backlog item and obtain approval.
4. Update this baseline and its traceability links.
5. Add or revise tests before release readiness is evaluated.
