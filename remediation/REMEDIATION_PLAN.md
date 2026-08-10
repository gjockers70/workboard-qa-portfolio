# Phase 12 Remediation and Retest Plan

## Objective

Confirm that every genuine defect recorded in the portfolio has a complete failure-to-closure chain, independently revalidate the corrected behaviors, and run risk-based regression before the Phase 12 checkpoint.

## Scope decision

Four confirmed defects are in scope: DEF-P3-001, DEF-P3-002, DEF-P8-001, and DEF-P8-002. All four were corrected and closed in their source cycles. Phase 12 preserves those historical records and performs an additional assurance cycle against the corrected baseline.

Phase 11 produced no product defect. UAT-OBS-001 is a clarified requirement misunderstanding and UAT-ENH-001 is linked to deferred backlog item ENH-002. Neither item authorizes a product change or corrective retest.

## Entry criteria

- Original failed execution or finding evidence is retained.
- A documented correction and passing source-cycle retest exist for each confirmed defect.
- The normal application configuration uses corrected behavior.
- Brave, the local application, and synthetic test data are available.
- No Critical or Major defect is open at cycle start.

## Execution sequence

1. Reconcile each defect with its source case, correction, and original retest.
2. Execute four managed defect confirmations using the approved case versions.
3. Run the six-case critical UI regression selection.
4. Reconcile managed results with the automated check count; one responsive case has three viewport parameters.
5. Run artifact-integrity checks, the complete project suite, and the frontend production build.
6. Keep a defect Closed only when the Phase 12 confirmation and adjacent regression pass.
7. Reopen a failed item instead of overwriting its historical evidence.

## Exit criteria

- 10 of 10 managed executions have a final Pass result.
- The focused browser commands report 12 passing checks: six defect-oriented checks and six critical regression checks.
- All four confirmed defects remain Closed with Phase 12 evidence.
- No open Critical or Major defect remains.
- UAT classifications remain truthful and no deferred enhancement is represented as a correction.
- The complete project suite and frontend production build pass.

## Environment and evidence

- Windows 11
- Brave 151.1.93.134 in verified headless mode
- corrected local application baseline
- disposable SQLite data and synthetic identities
- `remediation/DEFECT_RETEST_MATRIX.csv`
- `test-management/TEST_EXECUTIONS.csv`
- `test-management/PHASE_12_RETEST_REGISTER.xlsx`
- generated HTML and JUnit reports under the ignored `reports/` directory

## Failure handling

If a confirmation or regression check fails, record a new attempt, move the linked defect to Reopened or create a new defect after triage, correct only the approved scope, and rerun the failed case plus its impact-based regression selection. Do not replace the original failure or retest record.
