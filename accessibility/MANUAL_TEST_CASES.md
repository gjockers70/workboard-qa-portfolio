# Phase 8 Manual and Tool-Assisted Test Cases

Execution date: August 10, 2026
Primary browser: Brave 151.1.93.134

| ID | Check | Procedure | Expected result | Final result |
|---|---|---|---|---|
| A11Y-M01 | Sign-in structure | Review landmarks, heading, labels, control names, and document language. | One descriptive level-one heading, a main landmark, English document language, and named controls. | Pass |
| A11Y-M02 | Registration structure | Open registration and review the added display-name field and heading. | The view retains logical structure and every field has an explicit label. | Pass |
| A11Y-M03 | Workspace structure | Sign in, create a task, and inspect headings and regions. | A single page heading is followed by level-two section and task headings without skipped levels. | Pass |
| A11Y-M04 | Keyboard workflow | Use Tab, Shift+Tab, Enter, typing, select, and dialog keys through creation, profile, filtering, completion, deletion, and sign-out. | All functions are reachable and operable without pointer input; focus order follows the visual workflow. | Pass |
| A11Y-M05 | Focus indicator | Inspect focused inputs, text areas, selects, and buttons on light and dark surfaces. | A persistent two-color focus indicator is visible and is not obscured. | Pass |
| A11Y-M06 | Delete dialog | Open the delete confirmation from the keyboard, dismiss it, and inspect focus. | The dialog names the task, supports keyboard dismissal, preserves data, and restores focus to Delete. | Pass |
| A11Y-M07 | Reflow | Set the browser viewport to 320 by 900 pixels and inspect core controls. | No horizontal page scrolling is required and core controls remain in the viewport. | Pass |
| A11Y-M08 | Contrast | Run axe-core, WAVE contrast review, and computed text/component checks. | Corrected controls and content have no detected WCAG A/AA contrast violation. | Pass |
| A11Y-M09 | Success announcement | With NVDA active, create a task in headed Brave. | NVDA announces “Task created” without moving focus. | Pass after remediation |
| A11Y-M10 | Error announcement | Submit an invalid task value with NVDA active. | NVDA announces “Check the submitted values” as an alert. | Pass |
| A11Y-M11 | WAVE sign-in review | Activate WAVE on the rendered sign-in page and inspect the Details and Structure views. | No WAVE errors, contrast errors, or alerts; labels and structure are exposed. | Pass: 0 errors, 0 contrast errors, 0 alerts |
| A11Y-M12 | WAVE workspace review | Activate WAVE on a populated authenticated workspace and disposition each result. | No unresolved error, contrast error, or alert remains. | Pass after remediation: 0 errors, 0 contrast errors, 0 alerts |
| A11Y-M13 | Controlled baseline | Open local development with `?accessibility-defects=true` and repeat naming, structure, contrast, focus, and feedback checks. | The known defects reproduce only in controlled mode and are detected by the assigned checks. | Pass |

The detailed automated coverage is in `tests/accessibility/test_accessibility.py`. Final execution: 10 passed, 0 failed.
