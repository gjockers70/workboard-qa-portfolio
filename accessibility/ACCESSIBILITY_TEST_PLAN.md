# Phase 8 Accessibility Test Plan

## Objective

Evaluate WorkBoard with automated, keyboard, visual, and screen-reader methods; document reproducible findings; remediate confirmed issues; and retest the corrected application.

This evaluation uses WCAG 2.2 Level A and AA success criteria as the primary technical reference and maps relevant results to the Revised Section 508 web-content requirements. It is project test evidence, not a certification or legal-compliance claim.

## Scope

Included application states:

- sign-in and registration views
- authenticated member workspace
- populated task list
- success and error feedback
- native edit and delete dialogs
- controlled accessibility-defect baseline

Included topics:

- accessible names, labels, roles, values, and relationships
- heading hierarchy and landmarks
- keyboard operation, tab order, focus visibility, and focus restoration
- text, component, and focus-indicator contrast
- status and error announcements
- desktop and 320-pixel reflow
- automated WCAG A/AA rules

Administrator authorization behavior, API contracts, and direct database checks remain covered by earlier phases except where they affect the rendered interface.

## References

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [WCAG 2.2 Understanding documents](https://www.w3.org/WAI/WCAG22/Understanding/)
- [Section 508 testing guidance](https://www.section508.gov/test/)
- [axe-core](https://github.com/dequelabs/axe-core)
- [Lighthouse accessibility audits](https://developer.chrome.com/docs/lighthouse/accessibility/)
- [WAVE help](https://wave.webaim.org/help)

## Environment

| Component | Version or configuration |
|---|---|
| Operating system | Windows 11 |
| Primary browser | Brave 151.1.93.134 |
| axe-core | 4.13.0 |
| Lighthouse | 13.4.1 |
| WAVE extension | 3.3.1.0 |
| NVDA portable | 2026.1.1 |
| Application | Local React, FastAPI, and SQLite stack |

All accounts and records use synthetic local test data. Generated raw reports, browser profiles, speech logs, and screenshots remain under the ignored `reports/` directory.

## Approach

1. Run axe-core against corrected sign-in, registration, empty-workspace, and populated-workspace states.
2. Run positive checks against the controlled defect baseline to prove missing names, low contrast, heading changes, missing labels, and absent focus indication are detectable.
3. Operate the corrected interface using the keyboard and verify focus visibility, order, dialogs, focus restoration, and 320-pixel reflow.
4. Run Lighthouse against the corrected sign-in state and separately complete its manual-audit topics.
5. Review sign-in and populated-workspace states with the official WAVE browser extension.
6. Run NVDA with headed Brave, capture success and error announcements, remediate failures, and retest.
7. Run the complete project regression suite and production build after accessibility remediation.

## Entry and exit criteria

Entry criteria:

- corrected application and controlled defect baseline are available locally
- backend and frontend health checks succeed
- test tools are installed from reproducible project dependencies or verified local copies

Exit criteria:

- every Phase 8 automated test passes
- no unresolved WAVE error or contrast-error result remains
- every WAVE alert has a documented disposition
- keyboard, dialog, reflow, and NVDA evidence has a passing final result
- every confirmed finding is corrected and passes focused and full regression testing
- documentation avoids claims that the tool results establish complete accessibility or legal compliance
