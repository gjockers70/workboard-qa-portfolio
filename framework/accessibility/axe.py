from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AXE_SOURCE = PROJECT_ROOT / "app" / "frontend" / "node_modules" / "axe-core" / "axe.min.js"
WCAG_AA_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]


def run_axe(driver: WebDriver) -> dict[str, object]:
    if not AXE_SOURCE.is_file():
        raise FileNotFoundError("Install frontend development dependencies before running accessibility tests.")

    driver.execute_script(AXE_SOURCE.read_text(encoding="utf-8"))
    result = driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        axe.run(document, {runOnly: {type: 'tag', values: arguments[0]}})
          .then(results => done({ok: true, results}))
          .catch(error => done({ok: false, error: error.message}));
        """,
        WCAG_AA_TAGS,
    )
    if not result["ok"]:
        raise RuntimeError(f"axe execution failed: {result['error']}")
    return result["results"]


def violation_ids(results: dict[str, object]) -> set[str]:
    return {str(violation["id"]) for violation in results["violations"]}


def format_violations(results: dict[str, object]) -> str:
    entries = []
    for violation in results["violations"]:
        targets = [str(node["target"]) for node in violation["nodes"]]
        entries.append(f"{violation['id']}: {violation['help']} at {', '.join(targets)}")
    return "\n".join(entries) or "No violations"
