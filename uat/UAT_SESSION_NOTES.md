# Simulated UAT session notes

## Disclosure

This was a single-person role-play conducted for portfolio practice on August 10, 2026. The operations-coordinator participant was simulated; no external client or customer took part, and the result is not a real client sign-off.

## Environment

- Corrected local WorkBoard baseline
- Windows 11
- Brave 151.1.93.134
- Synthetic member and administrator identities
- Local FastAPI, React, and SQLite application

## Facilitation record

The facilitator introduced each business goal without naming the exact controls to use. Questions were recorded before clarification, and answers were given only after the simulated participant attempted the goal. Product behavior was compared with the approved requirement before an observation was classified.

## Scenario observations

| Scenario | What the participant attempted | Expected result | Actual result | Issue found | Severity | Disposition | Retest outcome | Final result |
|---|---|---|---|---|---|---|---|---|
| UAT-001 | Registered a new member and reviewed the workspace identity. | Authenticated member workspace opens with understandable identity and role. | Workspace opened and displayed the member identity and role. | None | Not applicable | Accepted | Not required | Pass |
| UAT-002 | Updated the profile and completed the create, edit, complete, reopen, cancel-delete, and confirm-delete task lifecycle. | Each intended change persists with clear feedback and deletion requires confirmation. | Every action produced the expected state and feedback. A request for due dates and priority was recorded. | UAT-ENH-001 | Not applicable | Enhancement returned to backlog; baseline accepted | Not required | Pass |
| UAT-003 | Combined a business search term with active and completed filters. | Every result satisfies both the search and state selection. | Results matched both conditions and All restored the complete personal list. | None | Not applicable | Accepted | Not required | Pass |
| UAT-004 | Refreshed an authenticated workspace after creating a uniquely named task. | Session remains valid and the task is not duplicated. | The member remained signed in and exactly one matching task remained. | None | Not applicable | Accepted | Not required | Pass |
| UAT-005 | Opened team oversight, identified task ownership, and looked for available actions. | Member tasks are identifiable and read-only in team view. | Owner information was visible and no mutation actions appeared. An initial expectation of reprioritization was clarified. | UAT-OBS-001 | Not applicable | Requirement misunderstanding clarified after the attempt | Not required | Pass |
| UAT-006 | Signed out and refreshed the page. | Sign-in page remains displayed and the workspace does not reopen. | Sign-out returned to the sign-in page and refresh preserved signed-out state. | None | Not applicable | Accepted | Not required | Pass |

## Session totals

- Planned: 6
- Passed: 6
- Failed: 0
- Blocked: 0
- Not run: 0
- Confirmed UAT defects: 0
- Requirement misunderstandings: 1
- Enhancement requests: 1

The Brave browser replay passed the same accepted paths and is supporting evidence, not a substitute for business acceptance judgment.
