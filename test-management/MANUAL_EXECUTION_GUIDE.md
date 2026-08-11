# Manual Test Execution Guide

## Purpose

`TEST_CASES.csv` is the source register for manual cases. Each row represents one versioned test case and maps to a Zephyr-style case record. A new case remains `Draft` until reviewed, and case approval remains separate from the result of any execution attempt. The current registered cases are approved; historical attempts are retained in the execution register.

## Before execution

1. Record whether the corrected, functional-defect, or accessibility-defect baseline is active.
2. Start the backend and frontend and confirm the health endpoint responds.
3. Use new synthetic accounts or identify existing synthetic records reserved for the cycle.
4. Confirm that the case version, requirement links, and acceptance-criterion links are current.
5. Create an evidence location named for the cycle and execution date.

## Execution rules

- Follow the written steps in order unless performing an explicitly exploratory case.
- Record the actual result before assigning Pass, Fail, or Blocked.
- Use Pass only when every expected result is observed.
- Use Fail for a reproducible product mismatch.
- Use Blocked when the case cannot reach its assertion because of an environment or dependency issue.
- Do not mark a case Failed solely because a different case left contaminated data; correct the environment and rerun it.
- Capture screenshots only when they add useful evidence and avoid exposing credentials.

## Evidence naming

Use:

`<cycle-id>_<case-id>_<result>_<yyyy-mm-dd>_<short-description>`

Example:

`CYCLE-FUNC-001_TC-TASK-001_PASS_2026-08-10_task-created`

## Defect decision

A failed case becomes a defect candidate only after reproduction. Record the failed criterion, environment, exact data, expected result, actual result, and evidence. During triage, distinguish a product defect from an environment problem, requirement misunderstanding, duplicate, or enhancement.

## Zephyr-style field mapping

| Local field | Test-management meaning |
|---|---|
| Test Case ID | Stable case key |
| Title | Test case name |
| Objective | Purpose or scenario summary |
| Preconditions | Required starting state |
| Test Data | Synthetic inputs |
| Steps | Manual action sequence |
| Expected Result | Pass condition |
| Requirement IDs | Requirement links |
| Acceptance Criteria IDs | Story acceptance links |
| Labels | Suite or regression tags |
| Automation Candidate | Future automation disposition |
| Status | Draft or approved case state, not execution result |

Execution status, evidence, linked defects, and tester/date fields belong in separate execution records. The initial Phase 3 cycle is recorded in `TEST_EXECUTIONS.csv` and `PHASE_3_EXECUTION_REGISTER.xlsx`. Phase 9 extended the same structure with broader cycles and end-to-end traceability, as documented in the [Agile test-management guide](../docs/AGILE_TEST_MANAGEMENT.md).

## Phase 3 coverage boundary

At the Phase 3 checkpoint, the manual catalog contained 37 cases covering 22 requirements and 44 acceptance criteria. Twelve criteria were intentionally deferred to specialized API, database, CI, performance, and release-reporting phases. Those later phases completed the planned managed coverage; the [readable matrix](../TRACEABILITY_MATRIX.md) and [machine-readable register](REQUIREMENTS_TRACEABILITY.csv) record the final links.
