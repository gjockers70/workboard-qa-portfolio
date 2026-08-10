# User Stories

## Story format

Each story includes its user value, linked requirements, assumptions, and completion boundary. Acceptance criteria are maintained separately in `ACCEPTANCE_CRITERIA.md` so test cases can reference stable criterion IDs.

## US-001 — Register and sign in

**Story:** As a visitor, I want to create an account and sign in so that I can manage my own work.

- Priority: Must
- Estimate: 5 points
- Requirements: BR-001, FR-AUTH-001, FR-AUTH-002, NFR-SEC-001, NFR-DATA-001
- Assumptions: The user supplies a synthetic unique email address and a password of at least eight characters.
- Done boundary: AC-US001-01 through AC-US001-05 pass, with negative credential behavior included.

## US-002 — End or recover a session

**Story:** As a signed-in user, I want to sign out or recover from an invalid session so that my account state is predictable.

- Priority: Must
- Estimate: 3 points
- Requirements: FR-AUTH-003, NFR-REL-001
- Done boundary: AC-US002-01 through AC-US002-04 pass.

## US-003 — Manage personal tasks

**Story:** As a member, I want to create, review, change, complete, reopen, and delete my tasks so that I can manage my work lifecycle.

- Priority: Must
- Estimate: 8 points
- Requirements: BR-001, FR-TASK-001, FR-TASK-002, FR-TASK-003, FR-TASK-004, FR-TASK-005
- Assumptions: A delete action is final for the local demonstration and requires confirmation.
- Done boundary: AC-US003-01 through AC-US003-09 pass across UI, API, and database layers.

## US-004 — Find relevant tasks

**Story:** As a member, I want to search and filter my tasks so that I can quickly find work in a particular state.

- Priority: Must
- Estimate: 5 points
- Requirements: FR-TASK-006
- Done boundary: AC-US004-01 through AC-US004-06 pass, including combined search and state filtering.

## US-005 — Maintain a profile

**Story:** As a signed-in user, I want to update my display name so that the interface shows my preferred synthetic identity.

- Priority: Should
- Estimate: 3 points
- Requirements: FR-PROFILE-001
- Done boundary: AC-US005-01 through AC-US005-04 pass, including persistence after a new login.

## US-006 — Review team work

**Story:** As an administrator, I want to review tasks across users so that I can understand team workload without changing another person's task.

- Priority: Must
- Estimate: 5 points
- Requirements: BR-002, FR-ADMIN-001, FR-ADMIN-002
- Done boundary: AC-US006-01 through AC-US006-05 pass for both administrator and member roles.

## US-007 — Protect task ownership

**Story:** As a member, I want task ownership enforced by the backend so that another user cannot access or change my records.

- Priority: Must
- Estimate: 5 points
- Requirements: FR-AUTHZ-001, NFR-SEC-001
- Done boundary: AC-US007-01 through AC-US007-05 pass through direct API requests and database checks.

## US-008 — Use core workflows accessibly

**Story:** As a keyboard or screen-reader user, I want clear structure, names, feedback, focus, and contrast so that I can complete core workflows without relying on a mouse or vision alone.

- Priority: Must
- Estimate: 8 points
- Requirements: BR-003, NFR-ACC-001, NFR-ACC-002, NFR-ACC-003, NFR-ACC-004, NFR-ACC-005, NFR-COMPAT-001
- Done boundary: AC-US008-01 through AC-US008-08 pass using a combination of automated checks, keyboard review, and NVDA review.
- Limitation: Passing these criteria supports the project assessment but does not establish legal compliance.

## US-009 — Continue after interruption

**Story:** As a remotely connected user, I want refresh, interruption, and reconnection behavior to be understandable so that I do not lose authorization context or unknowingly repeat an action.

- Priority: Should
- Estimate: 5 points
- Requirements: NFR-REL-001, NFR-REMOTE-001
- Done boundary: AC-US009-01 through AC-US009-04 pass in a controlled local simulation.

## US-010 — Make a release decision

**Story:** As a release stakeholder, I want traceable test results and defined quality gates so that I can make an evidence-based release decision.

- Priority: Must
- Estimate: 8 points
- Requirements: BR-004, NFR-PERF-001
- Done boundary: AC-US010-01 through AC-US010-06 pass and the final status records any accepted exceptions.
