from __future__ import annotations

import json
from pathlib import Path

import pytest

from qual_lab.main import main


def test_emit_study_manifest_template(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["emit-study-manifest-template"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["study_slug"] == "demo-sensitive-study"


def test_validate_study_manifest_example(capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = Path("examples/demo_study_manifest.json")
    assert main(["validate-study-manifest", "--manifest", str(manifest_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["data_sensitivity"] == "regulated"


def test_invalid_manifest_returns_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = tmp_path / "invalid.json"
    manifest_path.write_text('{"display_name": "Missing slug"}', encoding="utf-8")
    assert main(["validate-study-manifest", "--manifest", str(manifest_path)]) == 1
    assert "error:" in capsys.readouterr().err


def test_emit_audit_schema(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["emit-contract-schema", "--kind", "audit-event"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "AuditEvent"


def test_validate_protected_intake_example(capsys: pytest.CaptureFixture[str]) -> None:
    intake_path = Path("examples/demo_protected_intake.json")
    assert main(["validate-protected-intake", "--intake", str(intake_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["artifact_id"] == "session-001-transcript"


def test_assess_intake_with_review(capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = Path("examples/demo_study_manifest.json")
    intake_path = Path("examples/demo_protected_intake.json")
    review_path = Path("examples/demo_deidentification_review.json")
    assert (
        main(
            [
                "assess-intake",
                "--manifest",
                str(manifest_path),
                "--intake",
                str(intake_path),
                "--review",
                str(review_path),
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_analysis"
    assert payload["modality"] == "transcript"


def test_validate_analysis_workspace_example(capsys: pytest.CaptureFixture[str]) -> None:
    workspace_path = Path("examples/demo_analysis_workspace.json")
    assert main(["validate-analysis-workspace", "--workspace", str(workspace_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["workspace_id"] == "demo-sensitive-study-coding"


def test_validate_framework_matrix_example(capsys: pytest.CaptureFixture[str]) -> None:
    matrix_path = Path("examples/demo_framework_matrix.json")
    assert main(["validate-framework-matrix", "--matrix", str(matrix_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["matrix_id"] == "demo-sensitive-study-framework-matrix"


def test_validate_mixed_method_join_example(capsys: pytest.CaptureFixture[str]) -> None:
    join_path = Path("examples/demo_mixed_method_join.json")
    assert main(["validate-mixed-method-join", "--join", str(join_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["join_id"] == "demo-sensitive-study-joint-display"


def test_validate_team_coding_round_example(capsys: pytest.CaptureFixture[str]) -> None:
    round_path = Path("examples/demo_team_coding_round.json")
    assert main(["validate-team-coding-round", "--round", str(round_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["round_id"] == "demo-sensitive-study-round-001"


def test_validate_adjudication_decision_example(capsys: pytest.CaptureFixture[str]) -> None:
    decision_path = Path("examples/demo_adjudication_decision.json")
    assert main(["validate-adjudication-decision", "--decision", str(decision_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["decision_id"] == "adjudication-unit-session-001-001"


def test_validate_assistive_algorithm_policy_gate_example(
    capsys: pytest.CaptureFixture[str],
) -> None:
    gate_path = Path("examples/demo_assistive_algorithm_policy_gate.json")
    assert main(["validate-assistive-algorithm-policy-gate", "--gate", str(gate_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["gate_id"] == "demo-sensitive-study-assistive-gate-001"


def test_validate_synthesis_export_record_example(capsys: pytest.CaptureFixture[str]) -> None:
    export_path = Path("examples/demo_synthesis_export_record.json")
    assert main(["validate-synthesis-export-record", "--export", str(export_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["export_id"] == "demo-sensitive-study-synthesis-export-001"


def test_init_analysis_workspace(capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = Path("examples/demo_study_manifest.json")
    gate_report_path = Path("examples/demo_intake_gate_report.json")
    review_path = Path("examples/demo_deidentification_review.json")
    assert (
        main(
            [
                "init-analysis-workspace",
                "--manifest",
                str(manifest_path),
                "--gate-report",
                str(gate_report_path),
                "--review",
                str(review_path),
                "--workspace-id",
                "demo-sensitive-study-coding-cli",
                "--workspace-root",
                "secure://workspace/demo-sensitive-study/coding-cli",
                "--workspace-scheme",
                "secure_uri",
                "--created-by-role",
                "analyst",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["workspace"]["workspace_id"] == "demo-sensitive-study-coding-cli"
    assert payload["audit_event"]["action"] == "initialized_analysis_workspace"


def test_init_team_coding_round(capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = Path("examples/demo_study_manifest.json")
    workspace_path = Path("examples/demo_analysis_workspace.json")
    assert (
        main(
            [
                "init-team-coding-round",
                "--manifest",
                str(manifest_path),
                "--workspace",
                str(workspace_path),
                "--round-id",
                "demo-sensitive-study-round-cli",
                "--created-by-role",
                "senior_analyst",
                "--facilitator-role",
                "senior_analyst",
                "--coder-role",
                "analyst",
                "--coder-role",
                "senior_analyst",
                "--adjudicator-role",
                "study_steward",
                "--codebook-id",
                "demo-sensitive-study-core",
                "--framework-matrix-id",
                "demo-sensitive-study-framework-matrix",
                "--mixed-method-join-id",
                "demo-sensitive-study-joint-display",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["team_coding_round"]["round_id"] == "demo-sensitive-study-round-cli"
    assert payload["audit_event"]["action"] == "initialized_team_coding_round"


def test_capture_assistive_review(capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = Path("examples/demo_study_manifest.json")
    workspace_path = Path("examples/demo_analysis_workspace.json")
    assert (
        main(
            [
                "capture-assistive-review",
                "--manifest",
                str(manifest_path),
                "--workspace",
                str(workspace_path),
                "--gate-id",
                "demo-sensitive-study-assistive-gate-cli",
                "--requested-by-role",
                "senior_analyst",
                "--decision-by-role",
                "study_steward",
                "--algorithm-label",
                "bounded_theme_suggester_cli",
                "--algorithm-runtime",
                "local_statistical",
                "--purpose",
                "Generate bounded candidate themes for analyst review.",
                "--proposed-use",
                "internal_analysis",
                "--input-locator",
                "secure://workspace/demo-sensitive-study/coding/synthesis-input-cli.json",
                "--decision",
                "approved_with_conditions",
                "--decision-rationale",
                "Approved for local-first review only.",
                "--output-locator",
                "secure://workspace/demo-sensitive-study/coding/assistive-output-cli.json",
                "--required-control",
                "Require manual analyst confirmation before release.",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["assistive_algorithm_policy_gate"]["gate_id"] == (
        "demo-sensitive-study-assistive-gate-cli"
    )
    assert payload["audit_event"]["action"] == "captured_assistive_review"


def test_init_synthesis_export_record(capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = Path("examples/demo_study_manifest.json")
    workspace_path = Path("examples/demo_analysis_workspace.json")
    assistive_gate_path = Path("examples/demo_assistive_algorithm_policy_gate.json")
    assert (
        main(
            [
                "init-synthesis-export-record",
                "--manifest",
                str(manifest_path),
                "--workspace",
                str(workspace_path),
                "--export-id",
                "demo-sensitive-study-synthesis-export-cli",
                "--created-by-role",
                "senior_analyst",
                "--export-kind",
                "mixed_method_brief",
                "--approved-use",
                "internal_analysis",
                "--sensitivity",
                "restricted",
                "--export-locator",
                "secure://exports/demo-sensitive-study/synthesis-export-cli.json",
                "--source-codebook-id",
                "demo-sensitive-study-core",
                "--source-framework-matrix-id",
                "demo-sensitive-study-framework-matrix",
                "--source-mixed-method-join-id",
                "demo-sensitive-study-joint-display",
                "--source-team-coding-round-id",
                "demo-sensitive-study-round-001",
                "--source-adjudication-decision-id",
                "adjudication-unit-session-001-001",
                "--source-memo-id",
                "memo-session-001-001",
                "--assistive-gate",
                str(assistive_gate_path),
                "--assistive-algorithm",
                "bounded_theme_suggester_v1",
                "--audit-event-id",
                "event-demo-sensitive-study-export-cli",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["synthesis_export_record"]["export_id"] == (
        "demo-sensitive-study-synthesis-export-cli"
    )
    assert payload["audit_event"]["action"] == "initialized_synthesis_export_record"


def test_build_audit_event(capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        main(
            [
                "build-audit-event",
                "--actor-role",
                "analyst",
                "--action",
                "coded_analysis_unit",
                "--target-type",
                "code_application",
                "--target-id",
                "app-session-001-001-usability-breakdown",
                "--sensitivity",
                "restricted",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["result"] == "success"


def test_emit_mixed_method_join_schema(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["emit-contract-schema", "--kind", "mixed-method-join"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "MixedMethodJoin"


def test_emit_team_coding_round_schema(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["emit-contract-schema", "--kind", "team-coding-round"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "TeamCodingRound"


def test_emit_assistive_algorithm_policy_gate_schema(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["emit-contract-schema", "--kind", "assistive-algorithm-policy-gate"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "AssistiveAlgorithmPolicyGate"


def test_emit_synthesis_export_record_schema(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["emit-contract-schema", "--kind", "synthesis-export-record"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "SynthesisExportRecord"
