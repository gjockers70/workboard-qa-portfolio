from pathlib import Path

import pytest
import yaml


pytestmark = pytest.mark.ci

ROOT = Path(__file__).resolve().parents[2]
FAST_WORKFLOW = ROOT / ".github" / "workflows" / "quality-gates.yml"
PERFORMANCE_WORKFLOW = ROOT / ".github" / "workflows" / "performance-baseline.yml"


def workflow_triggers(workflow: dict[object, object]) -> dict[str, object]:
    return workflow.get("on") or workflow[True]


def test_required_phase13_files_exist() -> None:
    required = (
        FAST_WORKFLOW,
        PERFORMANCE_WORKFLOW,
        ROOT / "scripts" / "evaluate_quality_gates.py",
        ROOT / "docs" / "CI_CD.md",
        ROOT / "ci" / "PHASE_13_VALIDATION.md",
    )
    assert all(path.is_file() for path in required)


def test_fast_workflow_uses_expected_triggers_and_least_privilege() -> None:
    workflow = yaml.safe_load(FAST_WORKFLOW.read_text(encoding="utf-8"))
    triggers = workflow_triggers(workflow)
    assert set(triggers) == {"pull_request", "push", "workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["quality-gates"]["timeout-minutes"] == 25


def test_fast_workflow_contains_every_required_gate_and_artifact_upload() -> None:
    text = FAST_WORKFLOW.read_text(encoding="utf-8")
    for required in (
        "tests/ci",
        "tests/api",
        "tests/database",
        "tests/reporting",
        "tests/accessibility",
        "test_registered_user_can_sign_in",
        "test_search_and_status_filter_apply_together",
        "scripts/evaluate_quality_gates.py",
        "actions/upload-artifact@v7",
        'echo "WORKBOARD_ADMIN_PASSWORD=$test_password" >> "$GITHUB_ENV"',
        'echo "WORKBOARD_DATABASE_URL=sqlite:///$RUNNER_TEMP/workboard-ci.db" >> "$GITHUB_ENV"',
        "if: always()",
    ):
        assert required in text
    assert text.index("- name: Start local application") < text.index("- name: Run API tests")
    assert "ci-local-synthetic-password" not in text
    assert "runner.temp" not in text
    assert "scripts/run_performance_baseline.py" not in text


def test_manual_performance_workflow_cannot_run_on_push_or_pull_request() -> None:
    workflow = yaml.safe_load(PERFORMANCE_WORKFLOW.read_text(encoding="utf-8"))
    assert set(workflow_triggers(workflow)) == {"workflow_dispatch"}
    assert "scripts/run_performance_baseline.py" in PERFORMANCE_WORKFLOW.read_text(encoding="utf-8")
