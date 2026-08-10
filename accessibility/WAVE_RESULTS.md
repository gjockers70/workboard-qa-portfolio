# WAVE Results

Tool: official WAVE browser extension 3.3.1.0
Browser: Brave 151.1.93.134
Execution date: August 10, 2026

The extension ran in disposable local Brave profiles, allowing it to inspect the rendered local and authenticated application without sending the WorkBoard page to the public WAVE service.

## Sign-in page

| Category | Count |
|---|---:|
| Errors | 0 |
| Contrast errors | 0 |
| Alerts | 0 |
| Features | 3 |
| Structural elements | 2 |
| ARIA items | 1 |

The visible structure contained the English document language, a level-one heading, a main landmark, two form labels, and the empty status region.

## Authenticated workspace

Initial review:

| Category | Count |
|---|---:|
| Errors | 0 |
| Contrast errors | 0 |
| Alerts | 2 |
| Features | 6 |
| Structural elements | 7 |
| ARIA items | 1 |

Both alerts were “Orphaned form label” notices targeting the implicitly associated Description `<textarea>` and Status `<select>`. Browser semantics and axe-core exposed valid names, but explicit associations provide clearer cross-tool evidence. The labels and controls were changed to matching `for` and `id` values.

Workspace retest:

| Category | Count |
|---|---:|
| Errors | 0 |
| Contrast errors | 0 |
| Alerts | 0 |
| Features | 6 |
| Structural elements | 7 |
| ARIA items | 1 |

The WAVE details, structure, and rendered-page overlays were visually inspected. Feature, structural, and ARIA icons are informational and were verified rather than removed.

WAVE itself does not issue accessibility approval or certification. These counts are one input to the combined evaluation.
