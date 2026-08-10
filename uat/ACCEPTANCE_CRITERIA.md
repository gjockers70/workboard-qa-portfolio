# UAT acceptance criteria

These business-facing criteria summarize approved product requirements without replacing the canonical criteria in `agile/ACCEPTANCE_CRITERIA.md`.

| UAT criterion | Business outcome | Source criteria |
|---|---|---|
| UAT-AC-001 | A new member can create an account, enter the workspace, and understand their identity and role. | AC-US001-01; AC-US005-01 |
| UAT-AC-002 | A member can maintain a preferred display name and complete the normal task lifecycle with clear feedback. | AC-US003-01; AC-US003-04 through AC-US003-09; AC-US005-02; AC-US005-03 |
| UAT-AC-003 | A member can find relevant tasks by search term and completion state without seeing unrelated work. | AC-US004-01 through AC-US004-06 |
| UAT-AC-004 | Refreshing the workspace retains a valid session and does not repeat a task change. | AC-US002-04; AC-US009-01 |
| UAT-AC-005 | An administrator can review team work with owner information and cannot change another member's task. | AC-US006-01; AC-US006-02; AC-US006-05 |
| UAT-AC-006 | A signed-in user can end the session and cannot reopen the workspace by refreshing the signed-out page. | AC-US002-01 |

## Acceptance decision

The simulated UAT cycle is accepted when all six criteria pass, no confirmed Critical or Major UAT defect remains open, and any misunderstanding or enhancement request has a documented disposition.
