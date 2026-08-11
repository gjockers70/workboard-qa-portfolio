from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


STAGE_FILES = {
    "unit_and_artifact": "unit-and-artifact.xml",
    "api": "api.xml",
    "database": "database.xml",
    "smoke": "smoke.xml",
    "regression": "regression.xml",
    "accessibility": "accessibility.xml",
}


@dataclass(frozen=True)
class StageResult:
    name: str
    tests: int
    passed: int
    failures: int
    errors: int
    skipped: int
    pass_rate_percent: float
    status: str


@dataclass(frozen=True)
class GateCheck:
    name: str
    status: str
    details: str


def _integer_attribute(element: ET.Element, name: str) -> int:
    return int(float(element.attrib.get(name, "0")))


def read_junit(path: Path, stage_name: str) -> StageResult:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    if not suites:
        raise ValueError(f"No test suite was found in {path}.")
    tests = sum(_integer_attribute(suite, "tests") for suite in suites)
    failures = sum(_integer_attribute(suite, "failures") for suite in suites)
    errors = sum(_integer_attribute(suite, "errors") for suite in suites)
    skipped = sum(_integer_attribute(suite, "skipped") for suite in suites)
    passed = tests - failures - errors - skipped
    pass_rate = (passed / tests * 100) if tests else 0.0
    status = "PASS" if tests > 0 and failures == errors == skipped == 0 else "BLOCK"
    return StageResult(
        name=stage_name,
        tests=tests,
        passed=passed,
        failures=failures,
        errors=errors,
        skipped=skipped,
        pass_rate_percent=round(pass_rate, 2),
        status=status,
    )


def open_critical_defects(defect_log: Path) -> list[str]:
    rows: list[list[str]] = []
    for line in defect_log.read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("| DEF-"):
            continue
        rows.append([part.strip() for part in line.strip().strip("|").split("|")])
    return sorted(row[0] for row in rows if row[4] == "Critical" and row[7] != "Closed")


def acceptance_coverage(project_root: Path) -> tuple[int, list[str]]:
    criteria_text = (project_root / "agile" / "ACCEPTANCE_CRITERIA.md").read_text(
        encoding="utf-8-sig"
    )
    required = set(re.findall(r"AC-US\d{3}-\d{2}", criteria_text))
    covered: set[str] = set()
    with (project_root / "test-management" / "TEST_CASES.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            covered.update(
                value.strip()
                for value in row["Acceptance Criteria IDs"].split(";")
                if value.strip()
            )
    return len(required), sorted(required - covered)


def evaluate_quality_gates(
    project_root: Path,
    results_dir: Path,
    minimum_regression_pass_rate: float = 100.0,
) -> dict[str, object]:
    stages: list[StageResult] = []
    checks: list[GateCheck] = []
    for stage_name, file_name in STAGE_FILES.items():
        path = results_dir / file_name
        if not path.is_file():
            checks.append(GateCheck(stage_name, "BLOCK", f"Missing result file: {file_name}"))
            continue
        stage = read_junit(path, stage_name)
        stages.append(stage)
        checks.append(
            GateCheck(
                stage_name,
                stage.status,
                f"{stage.passed}/{stage.tests} passed; {stage.skipped} skipped",
            )
        )

    stage_map = {stage.name: stage for stage in stages}
    regression = stage_map.get("regression")
    regression_passes = bool(
        regression and regression.pass_rate_percent >= minimum_regression_pass_rate
    )
    checks.append(
        GateCheck(
            "minimum_regression_pass_rate",
            "PASS" if regression_passes else "BLOCK",
            f"Required {minimum_regression_pass_rate:.2f}%",
        )
    )

    critical_defects = open_critical_defects(project_root / "DEFECT_LOG.md")
    checks.append(
        GateCheck(
            "open_critical_defects",
            "PASS" if not critical_defects else "BLOCK",
            "None" if not critical_defects else ", ".join(critical_defects),
        )
    )

    criterion_count, missing_criteria = acceptance_coverage(project_root)
    checks.append(
        GateCheck(
            "acceptance_criteria_coverage",
            "PASS" if not missing_criteria else "BLOCK",
            f"{criterion_count - len(missing_criteria)}/{criterion_count} covered",
        )
    )

    status = "PASS" if checks and all(check.status == "PASS" for check in checks) else "BLOCK"
    return {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "minimum_regression_pass_rate": minimum_regression_pass_rate,
        "stages": [asdict(stage) for stage in stages],
        "checks": [asdict(check) for check in checks],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the WorkBoard CI quality gates.")
    parser.add_argument("--results-dir", type=Path, default=Path("reports/ci"))
    parser.add_argument("--output", type=Path, default=Path("reports/ci/quality-gates.json"))
    parser.add_argument("--minimum-regression-pass-rate", type=float, default=100.0)
    options = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    result = evaluate_quality_gates(
        project_root=project_root,
        results_dir=options.results_dir,
        minimum_regression_pass_rate=options.minimum_regression_pass_rate,
    )
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Quality gate decision: {result['status']}")
    for check in result["checks"]:
        print(f"{check['status']}: {check['name']} - {check['details']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
