from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from qual_lab.models import (
    AdjudicationDecision,
    AnalysisUnit,
    AnalysisWorkspace,
    AssistiveAlgorithmPolicyGate,
    AssistiveAlgorithmRuntime,
    AuditEvent,
    CodeApplication,
    CodebookVersion,
    DeidentificationReview,
    ExternalModelAction,
    ExternalModelPolicy,
    FrameworkMatrix,
    GateStatus,
    IntakeGateReport,
    MemoRecord,
    MixedMethodJoin,
    ProtectedIntakeRecord,
    SensitivityLevel,
    StudyManifest,
    SynthesisExportRecord,
    TeamCodingRound,
    default_adjudication_decision,
    default_analysis_unit,
    default_analysis_workspace,
    default_assistive_algorithm_policy_gate,
    default_audit_event,
    default_code_application,
    default_codebook_version,
    default_deidentification_review,
    default_framework_matrix,
    default_memo_record,
    default_mixed_method_join,
    default_protected_intake_record,
    default_study_manifest,
    default_synthesis_export_record,
    default_team_coding_round,
)


def test_default_examples_validate() -> None:
    assert default_study_manifest().study_slug == "demo-sensitive-study"
    assert default_audit_event().result.value == "success"
    assert default_protected_intake_record().artifact_id == "session-001-transcript"
    assert default_deidentification_review().outcome.value == "approved"
    assert default_analysis_workspace().workspace_id == "demo-sensitive-study-coding"
    assert default_analysis_unit().unit_id == "unit-session-001-001"
    assert default_codebook_version().codebook_id == "demo-sensitive-study-core"
    assert default_code_application().application_id.startswith("app-session-001")
    assert default_memo_record().memo_id == "memo-session-001-001"
    assert default_framework_matrix().matrix_id == "demo-sensitive-study-framework-matrix"
    assert default_mixed_method_join().join_id == "demo-sensitive-study-joint-display"
    assert default_team_coding_round().round_id == "demo-sensitive-study-round-001"
    assert default_adjudication_decision().decision_id == "adjudication-unit-session-001-001"
    assert (
        default_assistive_algorithm_policy_gate().gate_id
        == "demo-sensitive-study-assistive-gate-001"
    )
    assert (
        default_synthesis_export_record().export_id
        == "demo-sensitive-study-synthesis-export-001"
    )


def test_demo_json_examples_validate() -> None:
    study_payload = json.loads(
        Path("examples/demo_study_manifest.json").read_text(encoding="utf-8")
    )
    event_payload = json.loads(
        Path("examples/demo_audit_event.json").read_text(encoding="utf-8")
    )
    intake_payload = json.loads(
        Path("examples/demo_protected_intake.json").read_text(encoding="utf-8")
    )
    review_payload = json.loads(
        Path("examples/demo_deidentification_review.json").read_text(encoding="utf-8")
    )
    gate_payload = json.loads(
        Path("examples/demo_intake_gate_report.json").read_text(encoding="utf-8")
    )
    workspace_payload = json.loads(
        Path("examples/demo_analysis_workspace.json").read_text(encoding="utf-8")
    )
    unit_payload = json.loads(
        Path("examples/demo_analysis_unit.json").read_text(encoding="utf-8")
    )
    codebook_payload = json.loads(
        Path("examples/demo_codebook_version.json").read_text(encoding="utf-8")
    )
    application_payload = json.loads(
        Path("examples/demo_code_application.json").read_text(encoding="utf-8")
    )
    memo_payload = json.loads(
        Path("examples/demo_memo_record.json").read_text(encoding="utf-8")
    )
    framework_matrix_payload = json.loads(
        Path("examples/demo_framework_matrix.json").read_text(encoding="utf-8")
    )
    mixed_method_join_payload = json.loads(
        Path("examples/demo_mixed_method_join.json").read_text(encoding="utf-8")
    )
    team_coding_round_payload = json.loads(
        Path("examples/demo_team_coding_round.json").read_text(encoding="utf-8")
    )
    adjudication_decision_payload = json.loads(
        Path("examples/demo_adjudication_decision.json").read_text(encoding="utf-8")
    )
    assistive_gate_payload = json.loads(
        Path("examples/demo_assistive_algorithm_policy_gate.json").read_text(encoding="utf-8")
    )
    synthesis_export_payload = json.loads(
        Path("examples/demo_synthesis_export_record.json").read_text(encoding="utf-8")
    )

    assert StudyManifest.model_validate(study_payload).status.value == "active"
    assert AuditEvent.model_validate(event_payload).result.value == "success"
    assert ProtectedIntakeRecord.model_validate(intake_payload).modality.value == "transcript"
    assert DeidentificationReview.model_validate(review_payload).outcome.value == "approved"
    assert IntakeGateReport.model_validate(gate_payload).status == GateStatus.READY_FOR_ANALYSIS
    assert AnalysisWorkspace.model_validate(workspace_payload).workspace_id.endswith("coding")
    assert AnalysisUnit.model_validate(unit_payload).unit_kind.value == "excerpt"
    assert CodebookVersion.model_validate(codebook_payload).status.value == "active"
    assert CodeApplication.model_validate(application_payload).coder_role == "analyst"
    assert MemoRecord.model_validate(memo_payload).memo_kind.value == "analytic"
    assert FrameworkMatrix.model_validate(framework_matrix_payload).matrix_id.endswith("matrix")
    assert MixedMethodJoin.model_validate(mixed_method_join_payload).join_strategy.endswith(
        "joint display"
    )
    assert TeamCodingRound.model_validate(team_coding_round_payload).round_id.endswith("001")
    assert (
        AdjudicationDecision.model_validate(adjudication_decision_payload).outcome.value
        == "merged_resolution"
    )
    assert (
        AssistiveAlgorithmPolicyGate.model_validate(assistive_gate_payload).decision.value
        == "approved_with_conditions"
    )
    assert (
        SynthesisExportRecord.model_validate(synthesis_export_payload).export_kind.value
        == "mixed_method_brief"
    )


def test_sensitive_manifest_requires_deidentification_for_exceptions() -> None:
    payload = default_study_manifest().model_dump(mode="json")
    payload["external_model_policy"] = ExternalModelPolicy(
        default_action=ExternalModelAction.APPROVED_EXCEPTION,
        requires_human_review=True,
        requires_deidentification=False,
    ).model_dump(mode="json")
    payload["data_sensitivity"] = SensitivityLevel.REGULATED.value
    with pytest.raises(ValidationError):
        StudyManifest.model_validate(payload)


def test_public_intake_cannot_carry_direct_identifiers() -> None:
    payload = default_protected_intake_record().model_dump(mode="json")
    payload["sensitivity"] = SensitivityLevel.PUBLIC.value
    with pytest.raises(ValidationError):
        ProtectedIntakeRecord.model_validate(payload)


def test_approved_review_requires_locator_and_transformations() -> None:
    payload = default_deidentification_review().model_dump(mode="json")
    payload["deidentified_locator"] = None
    with pytest.raises(ValidationError):
        DeidentificationReview.model_validate(payload)


def test_codebook_requires_unique_code_ids() -> None:
    payload = default_codebook_version().model_dump(mode="json")
    payload["codes"][1]["code_id"] = payload["codes"][0]["code_id"]
    with pytest.raises(ValidationError):
        CodebookVersion.model_validate(payload)


def test_workspace_requires_analysis_use() -> None:
    payload = default_analysis_workspace().model_dump(mode="json")
    payload["allowed_approved_uses"] = ["deidentified_export"]
    with pytest.raises(ValidationError):
        AnalysisWorkspace.model_validate(payload)


def test_framework_matrix_requires_declared_dimensions() -> None:
    payload = default_framework_matrix().model_dump(mode="json")
    payload["rows"][0]["cells"][0]["dimension_id"] = "not_in_dimensions"
    with pytest.raises(ValidationError):
        FrameworkMatrix.model_validate(payload)


def test_mixed_method_join_requires_declared_quantitative_finding_ids() -> None:
    payload = default_mixed_method_join().model_dump(mode="json")
    payload["rows"][0]["quantitative_finding_ids"].append("unknown_finding")
    with pytest.raises(ValidationError):
        MixedMethodJoin.model_validate(payload)


def test_team_coding_round_requires_adjudicator_for_double_coding() -> None:
    payload = default_team_coding_round().model_dump(mode="json")
    payload["adjudicator_role"] = None
    with pytest.raises(ValidationError):
        TeamCodingRound.model_validate(payload)


def test_adjudication_decision_requires_selected_application_for_confirmed_outcome() -> None:
    payload = default_adjudication_decision().model_dump(mode="json")
    payload["outcome"] = "confirmed_primary"
    payload["selected_application_id"] = None
    with pytest.raises(ValidationError):
        AdjudicationDecision.model_validate(payload)


def test_assistive_gate_external_runtime_requires_external_processing_use() -> None:
    payload = default_assistive_algorithm_policy_gate().model_dump(mode="json")
    payload["algorithm_runtime"] = AssistiveAlgorithmRuntime.EXTERNAL_MODEL.value
    payload["proposed_uses"] = ["internal_analysis"]
    with pytest.raises(ValidationError):
        AssistiveAlgorithmPolicyGate.model_validate(payload)


def test_synthesis_export_with_assistive_algorithms_requires_gate_id() -> None:
    payload = default_synthesis_export_record().model_dump(mode="json")
    payload["assistive_algorithm_gate_id"] = None
    with pytest.raises(ValidationError):
        SynthesisExportRecord.model_validate(payload)


def test_synthesis_export_requires_source_artifacts() -> None:
    payload = default_synthesis_export_record().model_dump(mode="json")
    payload["source_codebook_ids"] = []
    payload["source_framework_matrix_ids"] = []
    payload["source_mixed_method_join_ids"] = []
    payload["source_team_coding_round_ids"] = []
    payload["source_adjudication_decision_ids"] = []
    payload["source_memo_ids"] = []
    with pytest.raises(ValidationError):
        SynthesisExportRecord.model_validate(payload)
