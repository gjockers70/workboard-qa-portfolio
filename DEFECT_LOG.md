# Defect Log

This register contains reproducible findings observed during executed test cycles. Controlled defect switches are test inputs and are not open defects by themselves.

| Defect ID | Summary | Source cycle | Case | Severity | Priority | Owner role | Status | Resolution | Retest evidence |
|---|---|---|---|---|---|---|---|---|---|
| DEF-P3-001 | Form borders and focus indicator did not meet the project component-contrast target | CYCLE-PH3-20260810 | TC-ACCESS-003 | Major | High | Frontend developer | Closed | Darkened component borders and added a two-color focus treatment | PH3-20260810-034 passed; full Brave regression passed |
| DEF-P3-002 | The page overflowed horizontally at the 320-pixel responsive target | CYCLE-PH3-20260810 | TC-COMPAT-001 | Major | High | Frontend developer | Closed | Removed the page minimum-width constraint and corrected the narrow header layout | PH3-20260810-036 passed at 320, 760, and 1,280 pixels; full Brave regression passed |
| DEF-P8-001 | Success feedback was not announced consistently by NVDA | CYCLE-PH8-ACCESSIBILITY-20260810 | TC-ACCESS-002 | Major | High | Frontend developer | Closed | Kept an atomic live region in the document before messages were populated | NVDA announced success and error feedback on retest; Phase 8 accessibility suite passed |
| DEF-P8-002 | WAVE reported two implicit label-association alerts | CYCLE-PH8-ACCESSIBILITY-20260810 | TC-ACCESS-002 | Minor | Low | Frontend developer | Closed | Added explicit label and control associations | WAVE workspace retest reported zero alerts; Phase 8 accessibility suite passed |

## Required fields and handling rules

Every defect records an identifier, concise summary, reproduction source, affected case, severity, priority, owner role, status, resolution, and retest evidence. Attachments and environment details remain in the linked execution evidence rather than being duplicated here.

- Severity describes product impact: Critical, Major, Minor, or Trivial.
- Priority describes correction urgency: Critical, High, Medium, or Low.
- A failed test becomes a defect only after reproduction and triage.
- Closure requires a passing retest plus regression evidence appropriate to the changed area.
- Reopened defects return to Assigned with the new failure evidence linked.
