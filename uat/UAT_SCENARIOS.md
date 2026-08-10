# UAT scenarios

The facilitator presents the goal and context, not the detailed control sequence. The prompts below are written for the simulated operations-coordinator persona.

## UAT-001 - Start a personal workspace

- Test case: TC-UAT-001
- UAT criterion: UAT-AC-001
- Goal: Create a new member identity and confirm the workspace is ready for personal task management.
- Data: UAT-MEMBER-A
- Expected result: Registration succeeds, the workspace opens, and the displayed identity and member role are understandable.

## UAT-002 - Maintain profile and daily work

- Test case: TC-UAT-002
- UAT criterion: UAT-AC-002
- Goal: Update the display name, create a task, revise its details, complete it, reopen it, cancel one deletion attempt, and then delete it deliberately.
- Data: UAT-MEMBER-A; UAT-TASK-DAILY
- Expected result: Every accepted change persists and produces clear feedback; canceled deletion leaves the task present and confirmed deletion removes it.

## UAT-003 - Find work that needs attention

- Test case: TC-UAT-003
- UAT criterion: UAT-AC-003
- Goal: Create active and completed work, then find only the items matching both a business search term and selected state.
- Data: UAT-TASK-ACTIVE; UAT-TASK-COMPLETE; UAT-TASK-OTHER
- Expected result: Search and filter results satisfy both conditions and All restores the complete personal list.

## UAT-004 - Continue after refreshing

- Test case: TC-UAT-004
- UAT criterion: UAT-AC-004
- Goal: Refresh during an authenticated work session and confirm the user returns safely without duplicating the last action.
- Data: UAT-MEMBER-A; UAT-TASK-REFRESH
- Expected result: The member remains signed in and the task list contains exactly the work created before refresh.

## UAT-005 - Review team workload

- Test case: TC-UAT-005
- UAT criterion: UAT-AC-005
- Goal: As an administrator, review a member's task, identify its owner, and determine what changes are permitted from team view.
- Data: UAT-MEMBER-B; UAT-ADMIN; UAT-TASK-TEAM
- Expected result: The team task shows owner identity, provides no mutation controls, and the administrator's personal view remains separate.

## UAT-006 - Finish the work session

- Test case: TC-UAT-006
- UAT criterion: UAT-AC-006
- Goal: End the current session and confirm a page refresh does not reopen the authenticated workspace.
- Data: UAT-MEMBER-A
- Expected result: Sign-out returns to the sign-in page and refresh preserves the signed-out state.
