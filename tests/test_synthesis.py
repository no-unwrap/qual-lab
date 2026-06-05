from __future__ import annotations

import pytest

from qual_lab.models import (
    ApprovedUse,
    AssistiveAlgorithmRuntime,
    AssistivePolicyDecision,
    ExternalModelAction,
    ExternalModelPolicy,
    SensitivityLevel,
    StorageLocator,
    StorageScheme,
    SynthesisExportKind,
    default_analysis_workspace,
    default_assistive_algorithm_policy_gate,
    default_study_manifest,
)
from qual_lab.synthesis import capture_assistive_review, initialize_synthesis_export_record


def test_capture_assistive_review_succeeds() -> None:
    gate, audit_event = capture_assistive_review(
        default_study_manifest(),
        default_analysis_workspace(),
        gate_id="demo-sensitive-study-assistive-gate-local",
        requested_by_role="senior_analyst",
        decision_by_role="study_steward",
        algorithm_label="bounded_theme_suggester_v2",
        algorithm_runtime=AssistiveAlgorithmRuntime.LOCAL_STATISTICAL,
        purpose="Generate bounded candidate themes for analyst review.",
        proposed_uses=[ApprovedUse.INTERNAL_ANALYSIS],
        input_locator=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://workspace/demo-sensitive-study/coding/synthesis-input-v2.json",
        ),
        output_locator=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://workspace/demo-sensitive-study/coding/assistive-themes-v2.json",
        ),
        decision=AssistivePolicyDecision.APPROVED_WITH_CONDITIONS,
        decision_rationale="Approved for local-first internal synthesis support only.",
        required_controls=["Record manual analyst confirmation before release."],
    )

    assert gate.gate_id == "demo-sensitive-study-assistive-gate-local"
    assert gate.requires_human_review is True
    assert audit_event.action == "captured_assistive_review"


def test_capture_assistive_review_rejects_external_runtime_when_disabled() -> None:
    workspace = default_analysis_workspace()

    with pytest.raises(ValueError, match="disabled by the study manifest policy"):
        capture_assistive_review(
            default_study_manifest(),
            workspace,
            gate_id="demo-sensitive-study-assistive-gate-external",
            requested_by_role="senior_analyst",
            decision_by_role="study_steward",
            algorithm_label="external-theme-suggester",
            algorithm_runtime=AssistiveAlgorithmRuntime.EXTERNAL_MODEL,
            purpose="Attempt external synthesis support without policy approval.",
            proposed_uses=[ApprovedUse.INTERNAL_ANALYSIS, ApprovedUse.EXTERNAL_MODEL_PROCESSING],
            input_locator=StorageLocator(
                storage_scheme=StorageScheme.SECURE_URI,
                locator="secure://workspace/demo-sensitive-study/coding/synthesis-input.json",
            ),
            output_locator=StorageLocator(
                storage_scheme=StorageScheme.SECURE_URI,
                locator="secure://workspace/demo-sensitive-study/coding/assistive-output.json",
            ),
            decision=AssistivePolicyDecision.APPROVED_WITH_CONDITIONS,
            decision_rationale="Should fail closed.",
            required_controls=["Manual review required."],
        )


def test_capture_assistive_review_allows_explicit_external_exception() -> None:
    manifest = default_study_manifest()
    manifest.external_model_policy = ExternalModelPolicy(
        default_action=ExternalModelAction.APPROVED_EXCEPTION,
        requires_human_review=True,
        requires_deidentification=True,
        allowed_providers=["approved-provider"],
        allowed_model_classes=["theme-summarizer"],
    )

    gate, audit_event = capture_assistive_review(
        manifest,
        default_analysis_workspace(),
        gate_id="demo-sensitive-study-assistive-gate-approved-external",
        requested_by_role="senior_analyst",
        decision_by_role="study_steward",
        algorithm_label="approved-external-theme-suggester",
        algorithm_runtime=AssistiveAlgorithmRuntime.EXTERNAL_MODEL,
        purpose="Use one approved external exception after de-identification.",
        proposed_uses=[ApprovedUse.INTERNAL_ANALYSIS, ApprovedUse.EXTERNAL_MODEL_PROCESSING],
        input_locator=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://workspace/demo-sensitive-study/coding/synthesis-input.json",
        ),
        output_locator=StorageLocator(
            storage_scheme=StorageScheme.EXTERNAL_OBJECT_STORE,
            locator="s3://approved-exception/demo-sensitive-study/assistive-output.json",
        ),
        decision=AssistivePolicyDecision.APPROVED_WITH_CONDITIONS,
        decision_rationale="Explicit manifest exception documented for this study.",
        required_controls=["Log provider and model class before export."],
    )

    assert gate.algorithm_runtime == AssistiveAlgorithmRuntime.EXTERNAL_MODEL
    assert audit_event.target_id == gate.gate_id


def test_initialize_synthesis_export_record_succeeds() -> None:
    record, audit_event = initialize_synthesis_export_record(
        default_study_manifest(),
        default_analysis_workspace(),
        export_id="demo-sensitive-study-synthesis-export-local",
        created_by_role="senior_analyst",
        export_kind=SynthesisExportKind.MIXED_METHOD_BRIEF,
        included_approved_uses=[ApprovedUse.INTERNAL_ANALYSIS],
        sensitivity=SensitivityLevel.RESTRICTED,
        export_locator=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://exports/demo-sensitive-study/synthesis-export-local.json",
        ),
        source_codebook_ids=["demo-sensitive-study-core"],
        source_framework_matrix_ids=["demo-sensitive-study-framework-matrix"],
        source_mixed_method_join_ids=["demo-sensitive-study-joint-display"],
        source_team_coding_round_ids=["demo-sensitive-study-round-001"],
        source_adjudication_decision_ids=["adjudication-unit-session-001-001"],
        source_memo_ids=["memo-session-001-001"],
        assistive_gate=default_assistive_algorithm_policy_gate(),
        assistive_algorithms_applied=["bounded_theme_suggester_v1"],
        audit_event_ids=["event-demo-sensitive-study-export-local"],
    )

    assert record.export_id == "demo-sensitive-study-synthesis-export-local"
    assert record.assistive_algorithm_gate_id == "demo-sensitive-study-assistive-gate-001"
    assert audit_event.action == "initialized_synthesis_export_record"


def test_initialize_synthesis_export_record_rejects_sensitivity_increase() -> None:
    with pytest.raises(ValueError, match="may not exceed the highest workspace source sensitivity"):
        initialize_synthesis_export_record(
            default_study_manifest(),
            default_analysis_workspace(),
            export_id="demo-sensitive-study-synthesis-export-regulated",
            created_by_role="senior_analyst",
            export_kind=SynthesisExportKind.THEMATIC_SUMMARY,
            included_approved_uses=[ApprovedUse.INTERNAL_ANALYSIS],
            sensitivity=SensitivityLevel.REGULATED,
            export_locator=StorageLocator(
                storage_scheme=StorageScheme.SECURE_URI,
                locator="secure://exports/demo-sensitive-study/synthesis-export-regulated.json",
            ),
            source_memo_ids=["memo-session-001-001"],
        )
