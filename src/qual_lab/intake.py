from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from qual_lab.boundaries import REPO_ROOT, storage_locator_outside_repo
from qual_lab.models import (
    ApprovedUse,
    DeidentificationReview,
    DeidentificationState,
    ExternalModelAction,
    GateStatus,
    IntakeGateReport,
    ProtectedIntakeRecord,
    ReviewOutcome,
    StudyManifest,
    StudyStatus,
)


def assess_intake(
    manifest: StudyManifest,
    intake: ProtectedIntakeRecord,
    review: DeidentificationReview | None = None,
    repo_root: str | Path | None = None,
) -> IntakeGateReport:
    root = Path(repo_root or REPO_ROOT).resolve()
    blockers: list[str] = []
    warnings: list[str] = []
    required_actions: list[str] = []

    role_map = {role.role_name: role for role in manifest.access_roles}
    submitting_role = role_map.get(intake.submitted_by_role)

    if manifest.status != StudyStatus.ACTIVE:
        blockers.append("study manifest must be active before protected intake can proceed")
    if intake.study_slug != manifest.study_slug:
        blockers.append("intake study_slug does not match the study manifest")
    if intake.modality not in manifest.modalities:
        blockers.append("intake modality is not allowed by the study manifest")
    if intake.sensitivity.rank > manifest.data_sensitivity.rank:
        blockers.append("intake sensitivity exceeds the manifest sensitivity ceiling")
    if submitting_role is None:
        blockers.append("submitted_by_role is not declared in the study manifest")
    elif intake.contains_direct_identifiers and not submitting_role.may_access_identifiable:
        blockers.append("submitted_by_role may not handle identifiable intake material")

    source_allowed, source_issue = storage_locator_outside_repo(intake.source, root)
    if not source_allowed and source_issue is not None:
        blockers.append(source_issue)

    if intake.code_key_linked:
        blockers.append("intake artifacts must not embed or link the code key")
    if intake.contains_raw_media and intake.modality.value != "audio":
        warnings.append("raw media was flagged on a non-audio modality; confirm modality labeling")

    if review is None:
        if intake.deidentification_state == DeidentificationState.APPROVED:
            blockers.append("de-identification approval requires an explicit review record")
        if blockers:
            required_actions.append("resolve_intake_policy_blockers")
            status = GateStatus.BLOCKED
            audit_action = "record_blocked_intake_attempt"
        else:
            required_actions.append("complete_deidentification_review")
            required_actions.append("stage_deidentified_artifact_outside_repo")
            status = GateStatus.ACCEPTED_FOR_REVIEW
            audit_action = "record_intake_receipt"

        return IntakeGateReport(
            assessed_at=datetime.now(timezone.utc),
            study_slug=intake.study_slug,
            artifact_id=intake.artifact_id,
            modality=intake.modality,
            status=status,
            analysis_ready=False,
            blockers=blockers,
            warnings=warnings,
            required_actions=required_actions,
            recommended_audit_action=audit_action,
        )

    review_role = role_map.get(review.reviewer_role)
    if review.study_slug != manifest.study_slug or review.study_slug != intake.study_slug:
        blockers.append("review study_slug does not match the study manifest and intake record")
    if review.artifact_id != intake.artifact_id:
        blockers.append("review artifact_id does not match the intake record")
    if review_role is None:
        blockers.append("reviewer_role is not declared in the study manifest")
    elif intake.contains_direct_identifiers and not review_role.may_access_identifiable:
        blockers.append("reviewer_role may not review identifiable source material")

    if review.deidentified_locator is not None:
        review_allowed, review_issue = storage_locator_outside_repo(
            review.deidentified_locator,
            root,
        )
        if not review_allowed and review_issue is not None:
            blockers.append(review_issue)

    if review.outcome != ReviewOutcome.APPROVED:
        blockers.append(f"de-identification review outcome is `{review.outcome.value}`")
        if review.outcome == ReviewOutcome.CHANGES_REQUIRED:
            required_actions.append("apply_requested_transformations")
            required_actions.append("rerun_deidentification_review")
        else:
            required_actions.append("stage_new_artifact_and_restart_review")
    else:
        if (
            ApprovedUse.EXTERNAL_MODEL_PROCESSING in review.approved_uses
            and manifest.external_model_policy.default_action == ExternalModelAction.DISABLED
        ):
            blockers.append("the study manifest forbids external model processing")
        if (
            ApprovedUse.DEIDENTIFIED_EXPORT in review.approved_uses
            and not any(role.may_export_deidentified for role in manifest.access_roles)
        ):
            blockers.append(
                "the study manifest declares no role allowed to export deidentified data"
            )
        if review.residual_sensitivity.rank > manifest.data_sensitivity.rank:
            blockers.append("review residual sensitivity exceeds the manifest sensitivity ceiling")

    if blockers:
        return IntakeGateReport(
            assessed_at=datetime.now(timezone.utc),
            study_slug=intake.study_slug,
            artifact_id=intake.artifact_id,
            modality=intake.modality,
            status=GateStatus.BLOCKED,
            analysis_ready=False,
            review_id=review.review_id,
            blockers=blockers,
            warnings=warnings,
            required_actions=required_actions or ["resolve_review_blockers"],
            recommended_audit_action="record_blocked_review_decision",
        )

    return IntakeGateReport(
        assessed_at=datetime.now(timezone.utc),
        study_slug=intake.study_slug,
        artifact_id=intake.artifact_id,
        modality=intake.modality,
        status=GateStatus.READY_FOR_ANALYSIS,
        analysis_ready=True,
        review_id=review.review_id,
        approved_uses=review.approved_uses,
        blockers=[],
        warnings=warnings,
        required_actions=[],
        recommended_audit_action="record_deidentification_approval",
    )
