# Phase 8 Accessibility Findings

| ID | Source | Severity | Finding | WCAG 2.2 relevance | Final disposition |
|---|---|---|---|---|---|
| A11Y-001 | Controlled baseline, axe-core, semantic checks | High | Search labeling, Delete accessible name, and search text contrast are deliberately degraded when controlled defect mode is active. | 1.3.1, 1.4.3, 2.4.6, 4.1.2 | Reproduced as designed; corrected mode passes axe and naming checks. |
| A11Y-002 | Controlled baseline, keyboard check | High | Controlled defect mode removes the visible keyboard focus indicator. | 2.4.7, 1.4.11 | Reproduced as designed; corrected mode exposes a two-color focus indicator. |
| A11Y-003 | Controlled baseline, structure and feedback checks | Medium | Controlled defect mode skips task-heading level and omits status/error roles. | 1.3.1, 2.4.6, 4.1.3 | Reproduced as designed; corrected mode has ordered headings and status/alert semantics. |
| A11Y-004 | NVDA | High | Success feedback was not consistently announced because the live region was inserted only after it contained the message. | 4.1.3 | Corrected with a persistent atomic live region; NVDA announced success and error text on retest. |
| A11Y-005 | WAVE | Low | WAVE raised two association alerts for implicit `<textarea>` and `<select>` labels. | 1.3.1, 3.3.2 | Hardened with explicit `for`/`id` associations; workspace retest has 0 alerts. |

## Final open-findings status

There are no unresolved confirmed findings in the corrected Phase 8 scope. The controlled baseline remains intentionally available only for local development evidence and is disabled by default.

Automated and tool-assisted results do not replace broader user research, testing with additional assistive technologies, or a formal conformance assessment.
