from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from qual_lab.audit import build_audit_event
from qual_lab.boundaries import REPO_ROOT, storage_locator_outside_repo
from qual_lab.models import (
    AnalysisWorkspace,
    AuditEvent,
    DeidentificationReview,
    GateStatus,
    IntakeGateReport,
    ReviewOutcome,
    StorageLocator,
    StudyManifest,
    WorkspaceSource,
)


def initialize_analysis_workspace(
    manifest: StudyManifest,
    gate_report: IntakeGateReport,
    review: DeidentificationReview,
    *,
    workspace_id: str,
    workspace_locator: StorageLocator,
    created_by_role: str,
    repo_root: str | Path | None = None,
) -> tuple[AnalysisWorkspace, AuditEvent]:
    root = Path(repo_root or REPO_ROOT).resolve()
    blockers: list[str] = []

    role_map = {role.role_name: role for role in manifest.access_roles}
    if created_by_role not in role_map:
        blockers.append("created_by_role is not declared in the study manifest")
    if gate_report.study_slug != manifest.study_slug or review.study_slug != manifest.study_slug:
        blockers.append("workspace inputs must all reference the same study_slug")
    if gate_report.artifact_id != review.artifact_id:
        blockers.append("gate report artifact_id does not match the review artifact_id")
    if gate_report.review_id is not None and gate_report.review_id != review.review_id:
        blockers.append("gate report review_id does not match the review record")
    if gate_report.status != GateStatus.READY_FOR_ANALYSIS or not gate_report.analysis_ready:
        blockers.append(
            "analysis workspaces may only be created from ready_for_analysis gate reports"
        )
    if review.outcome != ReviewOutcome.APPROVED:
        blockers.append("analysis workspaces require an approved de-identification review")
    if review.deidentified_locator is None:
        blockers.append("approved de-identification reviews must provide a deidentified locator")

    workspace_allowed, workspace_issue = storage_locator_outside_repo(workspace_locator, root)
    if not workspace_allowed and workspace_issue is not None:
        blockers.append(workspace_issue)

    if review.deidentified_locator is not None:
        source_allowed, source_issue = storage_locator_outside_repo(
            review.deidentified_locator,
            root,
        )
        if not source_allowed and source_issue is not None:
            blockers.append(source_issue)

    if blockers:
        raise ValueError("; ".join(blockers))

    assert review.deidentified_locator is not None
    source = WorkspaceSource(
        artifact_id=review.artifact_id,
        review_id=review.review_id,
        modality=gate_report.modality,
        gate_status=gate_report.status,
        approved_uses=gate_report.approved_uses,
        source_locator=review.deidentified_locator,
        residual_sensitivity=review.residual_sensitivity,
    )
    workspace = AnalysisWorkspace(
        workspace_id=workspace_id,
        study_slug=manifest.study_slug,
        created_at=datetime.now(timezone.utc),
        created_by_role=created_by_role,
        workspace_locator=workspace_locator,
        allowed_analysis_modes=manifest.analysis_modes,
        allowed_approved_uses=gate_report.approved_uses,
        source_artifacts=[source],
        notes=[
            "Initialized from a ready_for_analysis gate report.",
            "Synthetic fixtures should remain the only repo-tracked workspace examples.",
        ],
    )
    audit_event = build_audit_event(
        actor_role=created_by_role,
        action="initialized_analysis_workspace",
        target_type="analysis_workspace",
        target_id=workspace.workspace_id,
        sensitivity=review.residual_sensitivity,
        details=(
            "Initialized analysis workspace from approved de-identified artifact "
            f"`{review.artifact_id}`."
        ),
    )
    return workspace, audit_event
