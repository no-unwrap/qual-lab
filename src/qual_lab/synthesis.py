from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from qual_lab.audit import build_audit_event
from qual_lab.boundaries import REPO_ROOT, storage_locator_outside_repo
from qual_lab.models import (
    AnalysisWorkspace,
    ApprovedUse,
    AssistiveAlgorithmPolicyGate,
    AssistiveAlgorithmRuntime,
    AssistivePolicyDecision,
    AuditEvent,
    ExternalModelAction,
    SensitivityLevel,
    StorageLocator,
    StudyManifest,
    SynthesisExportKind,
    SynthesisExportRecord,
)


def _max_workspace_sensitivity(workspace: AnalysisWorkspace) -> SensitivityLevel:
    return max(
        (source.residual_sensitivity for source in workspace.source_artifacts),
        key=lambda sensitivity: sensitivity.rank,
    )


def _roles_declared(manifest: StudyManifest, *roles: str) -> list[str]:
    declared_roles = {role.role_name for role in manifest.access_roles}
    return sorted(role for role in roles if role not in declared_roles)


def _validate_locator(
    locator: StorageLocator,
    *,
    repo_root: Path,
    label: str,
    blockers: list[str],
) -> None:
    allowed, issue = storage_locator_outside_repo(locator, repo_root)
    if not allowed and issue is not None:
        blockers.append(f"{label} {issue}")


def capture_assistive_review(
    manifest: StudyManifest,
    workspace: AnalysisWorkspace,
    *,
    gate_id: str,
    requested_by_role: str,
    decision_by_role: str,
    algorithm_label: str,
    algorithm_runtime: AssistiveAlgorithmRuntime,
    purpose: str,
    proposed_uses: list[ApprovedUse],
    input_locator: StorageLocator,
    output_locator: StorageLocator | None,
    decision: AssistivePolicyDecision,
    decision_rationale: str,
    required_controls: list[str] | None = None,
    notes: list[str] | None = None,
    repo_root: str | Path | None = None,
) -> tuple[AssistiveAlgorithmPolicyGate, AuditEvent]:
    root = Path(repo_root or REPO_ROOT).resolve()
    blockers: list[str] = []

    undeclared_roles = _roles_declared(manifest, requested_by_role, decision_by_role)
    if undeclared_roles:
        blockers.append(
            "assistive review roles must be declared in the study manifest: "
            + ", ".join(undeclared_roles)
        )
    if workspace.study_slug != manifest.study_slug:
        blockers.append("assistive review inputs must reference the same study_slug")

    _validate_locator(input_locator, repo_root=root, label="input_locator", blockers=blockers)
    if output_locator is not None:
        _validate_locator(output_locator, repo_root=root, label="output_locator", blockers=blockers)

    if decision == AssistivePolicyDecision.BLOCKED and output_locator is not None:
        blockers.append("blocked assistive reviews may not declare an output_locator")
    if decision != AssistivePolicyDecision.BLOCKED and output_locator is None:
        blockers.append("approved assistive reviews must declare an output_locator")

    if (
        decision == AssistivePolicyDecision.APPROVED_WITH_CONDITIONS
        and not required_controls
    ):
        blockers.append(
            "approved_with_conditions assistive reviews must declare at least one required_control"
        )

    if algorithm_runtime == AssistiveAlgorithmRuntime.EXTERNAL_MODEL:
        policy = manifest.external_model_policy
        if policy.default_action == ExternalModelAction.DISABLED:
            blockers.append(
                "external-model assistive review capture is disabled by the study manifest policy"
            )
        if policy.requires_human_review is False:
            blockers.append(
                "external-model assistive review capture requires explicit human-review policy"
            )
        if policy.requires_deidentification is False:
            blockers.append(
                "external-model assistive review capture requires explicit de-identification policy"
            )
        if policy.default_action == ExternalModelAction.DEIDENTIFIED_ONLY and (
            ApprovedUse.EXTERNAL_MODEL_PROCESSING not in proposed_uses
        ):
            blockers.append(
                "deidentified_only external-model policy requires external_model_processing "
                "in proposed_uses"
            )

    if blockers:
        raise ValueError("; ".join(blockers))

    captured_at = datetime.now(timezone.utc)
    gate = AssistiveAlgorithmPolicyGate(
        gate_id=gate_id,
        workspace_id=workspace.workspace_id,
        study_slug=manifest.study_slug,
        requested_at=captured_at,
        requested_by_role=requested_by_role,
        algorithm_label=algorithm_label,
        algorithm_runtime=algorithm_runtime,
        purpose=purpose,
        proposed_uses=proposed_uses,
        input_locator=input_locator,
        output_locator=output_locator,
        requires_human_review=True,
        requires_deidentification=True,
        decision=decision,
        decision_rationale=decision_rationale,
        decision_by_role=decision_by_role,
        decided_at=captured_at,
        required_controls=required_controls or [],
        notes=[
            "Captured with the assistive review workflow helper.",
            *(notes or []),
        ],
    )
    audit_event = build_audit_event(
        actor_role=decision_by_role,
        action="captured_assistive_review",
        target_type="assistive_algorithm_policy_gate",
        target_id=gate.gate_id,
        sensitivity=_max_workspace_sensitivity(workspace),
        details=(
            "Captured an assistive review for "
            f"`{gate.algorithm_label}` on workspace `{workspace.workspace_id}`."
        ),
    )
    return gate, audit_event


def initialize_synthesis_export_record(
    manifest: StudyManifest,
    workspace: AnalysisWorkspace,
    *,
    export_id: str,
    created_by_role: str,
    export_kind: SynthesisExportKind,
    included_approved_uses: list[ApprovedUse],
    sensitivity: SensitivityLevel,
    export_locator: StorageLocator,
    source_codebook_ids: list[str] | None = None,
    source_framework_matrix_ids: list[str] | None = None,
    source_mixed_method_join_ids: list[str] | None = None,
    source_team_coding_round_ids: list[str] | None = None,
    source_adjudication_decision_ids: list[str] | None = None,
    source_memo_ids: list[str] | None = None,
    assistive_gate: AssistiveAlgorithmPolicyGate | None = None,
    assistive_algorithms_applied: list[str] | None = None,
    audit_event_ids: list[str] | None = None,
    notes: list[str] | None = None,
    repo_root: str | Path | None = None,
) -> tuple[SynthesisExportRecord, AuditEvent]:
    root = Path(repo_root or REPO_ROOT).resolve()
    blockers: list[str] = []

    undeclared_roles = _roles_declared(manifest, created_by_role)
    if undeclared_roles:
        blockers.append(
            "synthesis export roles must be declared in the study manifest: "
            + ", ".join(undeclared_roles)
        )
    if workspace.study_slug != manifest.study_slug:
        blockers.append("synthesis export inputs must reference the same study_slug")

    _validate_locator(export_locator, repo_root=root, label="export_locator", blockers=blockers)

    max_sensitivity = _max_workspace_sensitivity(workspace)
    if sensitivity.rank > max_sensitivity.rank:
        blockers.append(
            "synthesis export sensitivity may not exceed the highest workspace source sensitivity"
        )

    applied_algorithms = assistive_algorithms_applied or []
    if assistive_gate is None and applied_algorithms:
        blockers.append("assistive_algorithms_applied requires an explicit assistive gate")
    if assistive_gate is not None:
        if assistive_gate.study_slug != manifest.study_slug:
            blockers.append("assistive gates linked to synthesis exports must match study_slug")
        if assistive_gate.workspace_id != workspace.workspace_id:
            blockers.append("assistive gates linked to synthesis exports must match workspace_id")
        if assistive_gate.decision == AssistivePolicyDecision.BLOCKED:
            blockers.append("blocked assistive gates may not be linked to synthesis exports")
        if not applied_algorithms:
            blockers.append(
                "assistive gates linked to synthesis exports require at least one "
                "assistive algorithm label"
            )

    uses_external_model = ApprovedUse.EXTERNAL_MODEL_PROCESSING in included_approved_uses
    if uses_external_model:
        if manifest.external_model_policy.default_action == ExternalModelAction.DISABLED:
            blockers.append(
                "external-model synthesis exports are disabled by the study manifest policy"
            )
        if assistive_gate is None:
            blockers.append(
                "external-model synthesis exports require an explicit assistive policy gate"
            )
        elif assistive_gate.algorithm_runtime != AssistiveAlgorithmRuntime.EXTERNAL_MODEL:
            blockers.append(
                "external-model synthesis exports require an assistive gate with "
                "algorithm_runtime=external_model"
            )

    if blockers:
        raise ValueError("; ".join(blockers))

    record = SynthesisExportRecord(
        export_id=export_id,
        workspace_id=workspace.workspace_id,
        study_slug=manifest.study_slug,
        created_at=datetime.now(timezone.utc),
        created_by_role=created_by_role,
        export_kind=export_kind,
        source_codebook_ids=source_codebook_ids or [],
        source_framework_matrix_ids=source_framework_matrix_ids or [],
        source_mixed_method_join_ids=source_mixed_method_join_ids or [],
        source_team_coding_round_ids=source_team_coding_round_ids or [],
        source_adjudication_decision_ids=source_adjudication_decision_ids or [],
        source_memo_ids=source_memo_ids or [],
        included_approved_uses=included_approved_uses,
        sensitivity=sensitivity,
        export_locator=export_locator,
        assistive_algorithm_gate_id=assistive_gate.gate_id if assistive_gate else None,
        assistive_algorithms_applied=applied_algorithms,
        audit_event_ids=audit_event_ids or [],
        notes=[
            "Initialized with the synthesis export workflow helper.",
            *(notes or []),
        ],
    )
    audit_event = build_audit_event(
        actor_role=created_by_role,
        action="initialized_synthesis_export_record",
        target_type="synthesis_export_record",
        target_id=record.export_id,
        sensitivity=record.sensitivity,
        details=(
            "Initialized a synthesis export record for workspace "
            f"`{workspace.workspace_id}`."
        ),
    )
    return record, audit_event
