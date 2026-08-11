# Sprint Review Notes

## Sprint 1 — Requirements and functional baseline

- Demonstrated approved stories, acceptance criteria, 37 manual cases, and a completed functional cycle.
- Final result: 37 of 37 cases passed after two corrected findings passed retest.
- Improvement carried forward: record every attempt, including the original failure, instead of overwriting results.

## Sprint 2 — Automation and backend validation

- Demonstrated reusable browser, API, and database layers with selected smoke and regression suites.
- Evidence: six regression checks, 24 API tests, and 16 database tests passed.
- Improvement carried forward: use stable case and cycle identifiers so one automated check can be traced without copying test logic into management documents.

## Sprint 3 — Accessibility, reliability, and remediation

- Demonstrated keyboard, automated rules, Lighthouse, WAVE, and NVDA evidence with correction and retest records.
- Evidence: ten dedicated accessibility tests passed; confirmed findings were corrected and closed.
- Improvement carried forward: keep automated results and manual assistive-technology observations distinct in the evidence.

## Release-readiness decision at this checkpoint

The completed regression cycle supported continuing to Phase 10 because all six selected regression checks passed and no Critical or Major defect remained open. Performance, simulated UAT, pipeline gates, and final reporting now have completed later-cycle records. Phase 14 recommends release for the tested portfolio scope.

## Sprint 4 — Performance, simulated UAT, and retest assurance

- Demonstrated the bounded local load baseline and a disclosed single-person business acceptance exercise.
- Reconciled all four genuine defects through original failure, approved correction, source-cycle retest, Phase 12 independent confirmation, and adjacent regression.
- Evidence: 10 of 10 managed Phase 12 executions passed and the corresponding focused browser commands produced 12 passing automated checks.
- Improvement carried forward: classification comes before correction; requirement misunderstandings and deferred enhancements must not be relabeled as defects to manufacture remediation work.

## Sprint 4 — Continuous integration and blocking gates

- Added one fast validation workflow and one manual-only performance workflow.
- Separated build, unit/artifact, API, database, smoke, regression, and accessibility evidence so a failed stage is diagnosable.
- Applied release blockers for any failure or skip, regression below 100%, an open Critical defect, or missing acceptance-criteria coverage.
- Recorded a successful hosted run covering the build, all six test groups, gate evaluation, cleanup, and artifact retention.
- Improvement carried forward: a locally validated workflow is not described as hosted evidence until the approved push produces a completed remote run.

## Sprint 4 - Final test summary and release decision

- Reconciled 55 approved managed cases, 125 final checks across 11 completed cycles, and 77 execution rows without overwriting the two historical failures.
- Confirmed all four recorded defects are closed, all 56 acceptance criteria have managed case coverage, and the complete Phase 14 regression passed.
- Separated accepted limitations from release blockers and produced both technical and stakeholder-facing summaries.
- Recommendation: Release the corrected WorkBoard baseline for the tested portfolio scope; production deployment, certification, capacity, and real-client claims remain outside the decision.
