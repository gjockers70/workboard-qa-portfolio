# Phase 11 user acceptance test plan

## Purpose

Evaluate whether WorkBoard's approved business workflows are understandable and acceptable from a business-user perspective. This phase uses a disclosed single-person simulation; no external client participated, and the results must not be presented as client delivery experience.

## Participant and roles

| Role | Responsibility |
|---|---|
| Simulated participant | Role-plays an operations coordinator who manages personal tasks and occasionally reviews team workload as an administrator. |
| Facilitator | Introduces business goals, observes without coaching through difficulty, answers scope questions after an attempt, and records outcomes. |
| Test engineer | Prepares the corrected local baseline and synthetic data, replays the accepted paths in Brave, and reconciles evidence. |

The same project exercise performs all three roles. The separation is procedural, not a claim that three people participated.

## Scope

Included:

- account registration and authenticated workspace entry;
- profile and personal task maintenance;
- task search and status filtering;
- refresh and session continuity;
- administrator team oversight and its read-only boundary;
- sign-out and return to the sign-in page;
- classification of questions as defect, requirement misunderstanding, or enhancement request.

Excluded:

- production data, hosting, email delivery, password recovery, and multi-factor authentication;
- destructive testing, production-scale load, and security penetration testing;
- accessibility certification or legal-compliance claims;
- final release recommendation, which remains assigned to a later phase.

## Entry criteria

- Requirements and acceptance criteria through Phase 10 are approved.
- The corrected local application is available in Brave.
- Synthetic member and administrator identities are available.
- The complete regression and Phase 10 performance gate pass.
- No Critical or Major defect remains open in the tested baseline.

## Session method

1. Explain the participant persona, scope, and freedom to stop or ask a question.
2. Present one business goal at a time without prescribing control-by-control steps.
3. Let the simulated participant attempt the goal before answering workflow questions.
4. Record the attempt, expected result, actual result, hesitation, question, and outcome.
5. Compare unexpected behavior with the approved requirement before classifying it.
6. Record defects separately from misunderstandings and enhancement requests.
7. Replay the accepted paths in headless Brave as corroborating technical evidence.
8. Summarize acceptance, exceptions, and any required retest.

## Outcome rules

| Outcome | Meaning |
|---|---|
| Pass | The business goal is completed and the result matches the approved acceptance criterion. |
| Fail | The product prevents completion or produces behavior that contradicts an approved requirement. |
| Blocked | The scenario cannot be attempted because required environment or data is unavailable. |
| Not run | The scenario was planned but not attempted. |

## Issue classification

| Classification | Decision rule | Treatment |
|---|---|---|
| Defect | Observed product behavior contradicts an approved requirement. | Assign severity and priority, link the failed scenario, correct in an approved remediation phase, and retest. |
| Requirement misunderstanding | Product behavior matches the baseline, but the participant expected different behavior. | Clarify the approved scope and improve supporting wording only if confusion is likely to recur. |
| Enhancement request | The participant asks for useful behavior not required by the baseline. | Return the request to the backlog for product prioritization; do not count it as a failed test. |

Severity is used only for confirmed defects: Critical prevents all meaningful use or creates severe exposure; Major blocks a core goal without a practical workaround; Minor affects a secondary goal; Trivial is cosmetic with no task impact.

## Exit criteria

- Six planned scenarios have a final Pass, Fail, or Blocked result.
- Every observation has a classification and disposition.
- Any failed scenario has a linked defect and retest requirement.
- The session summary clearly states that the exercise was simulated.
- The sign-off record identifies outstanding exceptions without claiming a real client decision.

## Evidence

- `uat/UAT_SCENARIOS.md`
- `uat/SESSION_RESULTS.csv`
- `uat/UAT_SESSION_NOTES.md`
- `uat/UAT_DEFECT_LOG.md`
- `uat/UAT_SUMMARY.md`
- `tests/uat/test_uat_browser_replay.py`
- `tests/uat/test_uat_artifacts.py`
