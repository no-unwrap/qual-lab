from __future__ import annotations

from pathlib import Path

from qual_lab.intake import assess_intake
from qual_lab.models import (
    ApprovedUse,
    GateStatus,
    ReviewOutcome,
    StorageScheme,
    default_deidentification_review,
    default_protected_intake_record,
    default_study_manifest,
)


def test_assess_intake_accepts_for_review_without_review_record(tmp_path: Path) -> None:
    report = assess_intake(
        default_study_manifest(),
        default_protected_intake_record(),
        repo_root=tmp_path,
    )
    assert report.status == GateStatus.ACCEPTED_FOR_REVIEW
    assert report.analysis_ready is False
    assert "complete_deidentification_review" in report.required_actions


def test_assess_intake_blocks_repo_local_source(tmp_path: Path) -> None:
    intake = default_protected_intake_record()
    intake.source.storage_scheme = StorageScheme.LOCAL_ENCRYPTED
    intake.source.locator = str(tmp_path / "imports" / "session-001.json")

    report = assess_intake(
        default_study_manifest(),
        intake,
        repo_root=tmp_path,
    )
    assert report.status == GateStatus.BLOCKED
    assert any("outside the repository" in blocker for blocker in report.blockers)


def test_assess_intake_blocks_external_model_when_manifest_disables_it(tmp_path: Path) -> None:
    review = default_deidentification_review()
    review.approved_uses.append(ApprovedUse.EXTERNAL_MODEL_PROCESSING)

    report = assess_intake(
        default_study_manifest(),
        default_protected_intake_record(),
        review=review,
        repo_root=tmp_path,
    )
    assert report.status == GateStatus.BLOCKED
    assert any("forbids external model processing" in blocker for blocker in report.blockers)


def test_assess_intake_ready_for_analysis_after_approved_review(tmp_path: Path) -> None:
    report = assess_intake(
        default_study_manifest(),
        default_protected_intake_record(),
        review=default_deidentification_review(),
        repo_root=tmp_path,
    )
    assert report.status == GateStatus.READY_FOR_ANALYSIS
    assert report.analysis_ready is True


def test_assess_intake_blocks_review_changes_required(tmp_path: Path) -> None:
    review = default_deidentification_review()
    review.outcome = ReviewOutcome.CHANGES_REQUIRED
    review.approved_uses = []
    review.deidentified_locator = None

    report = assess_intake(
        default_study_manifest(),
        default_protected_intake_record(),
        review=review,
        repo_root=tmp_path,
    )
    assert report.status == GateStatus.BLOCKED
    assert "apply_requested_transformations" in report.required_actions


def test_assess_intake_blocks_review_export_without_export_role(tmp_path: Path) -> None:
    manifest = default_study_manifest()
    for role in manifest.access_roles:
        role.may_export_deidentified = False

    review = default_deidentification_review()
    review.approved_uses.append(ApprovedUse.DEIDENTIFIED_EXPORT)

    report = assess_intake(
        manifest,
        default_protected_intake_record(),
        review=review,
        repo_root=tmp_path,
    )
    assert report.status == GateStatus.BLOCKED
    assert any("allowed to export" in blocker for blocker in report.blockers)
