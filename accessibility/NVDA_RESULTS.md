# NVDA Results

## Configuration

- NVDA portable 2026.1.1
- Brave 151.1.93.134
- local corrected WorkBoard application
- add-ons disabled
- synthetic member and task data

The raw diagnostic speech log remains in the ignored local report directory. This file records only sanitized application evidence.

## Initial observation

The headed browser checks passed at the DOM level, and NVDA announced the error text “Check the submitted values.” The success text was not consistently announced. The feedback region was being inserted only after it already contained the new message, which made polite status delivery timing-dependent.

Finding: `A11Y-004` in [FINDINGS.md](FINDINGS.md).

## Remediation

The application now mounts an empty `role="status"` region before any update and keeps the same node available for later text changes. It uses `aria-atomic="true"`; error content switches the region to `role="alert"`. The controlled defect mode intentionally omits those semantics.

## Retest

The focused headed-Brave test passed. The NVDA speech log captured both application messages:

- `Task created`
- `Check the submitted values`

The complete Phase 8 browser suite then passed 10 of 10 tests.

## Result boundary

This result verifies the tested WorkBoard workflows and messages in the listed local environment. It does not establish behavior for every screen reader, browser, operating system, user setting, or application state.
