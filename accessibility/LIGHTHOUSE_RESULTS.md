# Lighthouse Accessibility Results

Execution date: August 10, 2026
Target: corrected local sign-in page
Lighthouse: 13.4.1
Browser binary: Brave 151.1.93.134
Reported user agent engine: Chromium 151

## Result

| Category | Score | Scored audit failures |
|---|---:|---:|
| Accessibility | 100 | 0 |

The reproducible command is:

```powershell
cd app/frontend
$env:CHROME_PATH = "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
npm run audit:accessibility -- http://127.0.0.1:5173/
Remove-Item Env:CHROME_PATH
```

The project runner writes JSON and HTML reports to the ignored `reports/` directory and exits unsuccessfully if the accessibility score is below 100.

## Manual audit disposition

Lighthouse lists keyboard focusability, logical tab order, visual/DOM order, focus traps, managed focus, landmarks, hidden content, and custom-control semantics as manual topics. Those topics were evaluated separately through the Phase 8 Brave keyboard suite, DOM review, WAVE review, native-dialog check, and NVDA execution.

The score summarizes Lighthouse's scored automated audits. It is not evidence that every accessibility requirement is satisfied.
