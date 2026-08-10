# Defect Triage

## Workflow

`New → Triaged → Assigned → In Progress → Ready for Retest → Retested → Closed`

## Triage meeting checklist

1. Confirm the observed result is reproducible on the recorded baseline.
2. Link the failed execution, test case, acceptance criterion, and evidence.
3. Separate product defects from test-data, environment, duplicate, or enhancement outcomes.
4. Assign severity from user impact and priority from release urgency.
5. Identify the owner role and the regression scope before correction begins.
6. Move to Ready for Retest only when a focused correction is available.
7. Close only after the failed case passes and the selected regression cycle remains green.

## Classification

| Outcome | Handling |
|---|---|
| Reproducible requirement failure | Create or update a defect |
| Test script or data problem | Correct the test asset; do not count as a product defect |
| Expected behavior not represented in requirements | Raise a requirement question |
| New capability request | Return an enhancement to the backlog |
| Environment-only interruption | Record a blocked execution and environment evidence |

## Phase 9 triage status

All four confirmed findings in the defect log are Closed. DEF-P3-001 and DEF-P3-002 each have an initial failed execution and a passing retest. The two Phase 8 tool-assisted findings have documented corrections and successful focused retests. There are no open Critical or Major defects in the executed Phase 3–8 scope.
