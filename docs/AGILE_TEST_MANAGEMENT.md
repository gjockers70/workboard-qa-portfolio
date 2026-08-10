# Agile Test Management

## Working model

The repository uses a lightweight one-week sprint simulation. Product stories and acceptance criteria enter a sprint, test cases are selected into a cycle, every attempt is recorded, reproducible failures are triaged as defects, and corrections require focused retest plus relevant regression before closure.

The workflow is:

`Backlog â†’ Selected for Sprint â†’ In Progress â†’ Ready for Test â†’ In Test â†’ Ready for Retest â†’ Done`

The release gate uses the regression cycle as a decision point: a Critical regression or authorization failure stops further release testing; an all-pass regression result permits the next planned cycle.

## Local artifact mapping

No hosted or paid product is required to review this project. The local files use fields that can be imported or linked later.

| Local artifact | Jira mapping | Confluence mapping | Zephyr Scale mapping |
|---|---|---|---|
| `agile/PRODUCT_BACKLOG.md` and `agile/USER_STORIES.md` | Epic/story backlog, priority, estimate, sprint, status | Product scope and story reference page | Requirement links on test cases |
| `agile/ACCEPTANCE_CRITERIA.md` | Story description or acceptance-criteria field | Requirements baseline | Requirement coverage links |
| `test-management/TEST_CASES.csv` | Linked test issue where enabled | Test-design reference table | Test Case import |
| `test-management/TEST_CYCLES.csv` | Sprint/release version association | Cycle plan and status page | Test Cycle import |
| `test-management/TEST_EXECUTIONS.csv` | Execution evidence linked to story/defect | Execution report | Test Execution import |
| `DEFECT_LOG.md` | Bug issue with severity, priority, owner, and workflow status | Triage decision log | Defect link from failed execution |
| `test-management/REQUIREMENTS_TRACEABILITY.csv` | Issue links between story, test, and bug | Requirements traceability page | Requirement, case, cycle, execution, and defect links |
| `agile/SPRINT_TEST_SUMMARY.md` | Sprint review attachment or release comment | Sprint test-summary page | Cycle summary and final status |

## Example records

### Jira-style story

- Key: US-007
- Summary: Enforce task ownership at the backend
- Priority: Must
- Estimate: 5 points
- Status: Done
- Acceptance range: AC-US007-01 through AC-US007-05

### Zephyr-style test case

- Key: TC-API-AUTHZ-001
- Objective: prove a member cannot update another member's task
- Requirement link: FR-AUTHZ-001
- Acceptance link: AC-US007-02
- Automation: `tests/api/test_workboard_api.py::test_member_cannot_mutate_another_members_task`
- Cycle: CYCLE-PH6-API-20260810
- Final result: Pass

### Defect and retest

PH3-20260810-033 failed TC-ACCESS-003 and created DEF-P3-001. The component colors were corrected, PH3-20260810-034 passed the same case, the full Brave regression passed, and the defect moved to Closed.

## Regression execution

CYCLE-PH5-REGRESSION-20260810 executed six selected critical UI checks. All six passed, so the gate permitted broader testing to continue. A failed Critical regression or authorization check would instead stop progression until triage and retest.

## Source-of-truth rules

- Markdown explains intent, decisions, and readable summaries.
- CSV files are the machine-readable source for cases, cycles, executions, and traceability.
- XLSX registers are formatted review views generated from the same CSV data.
- Test source and retained reports are execution evidence; management records link to them and do not replace them.
- A planned cycle cannot be reported as executed, and a failed attempt is never deleted after a retest passes.
