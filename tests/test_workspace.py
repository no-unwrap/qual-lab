from __future__ import annotations

from pathlib import Path

import pytest

from qual_lab.models import (
    GateStatus,
    StorageLocator,
    StorageScheme,
    default_deidentification_review,
    default_intake_gate_report,
    default_study_manifest,
)
from qual_lab.workspace import initialize_analysis_workspace


def test_initialize_analysis_workspace_succeeds_outside_repo(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    workspace_root = tmp_path / "workspace"

    workspace, audit_event = initialize_analysis_workspace(
        default_study_manifest(),
        default_intake_gate_report(),
        default_deidentification_review(),
        workspace_id="demo-sensitive-study-coding-local",
        workspace_locator=StorageLocator(
            storage_scheme=StorageScheme.LOCAL_ENCRYPTED,
            locator=str(workspace_root.resolve()),
        ),
        created_by_role="analyst",
        repo_root=repo_root,
    )

    assert workspace.workspace_id == "demo-sensitive-study-coding-local"
    assert workspace.source_artifacts[0].artifact_id == "session-001-transcript"
    assert audit_event.action == "initialized_analysis_workspace"


def test_initialize_analysis_workspace_blocks_repo_local_workspace_root(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    with pytest.raises(ValueError, match="outside the repository root"):
        initialize_analysis_workspace(
            default_study_manifest(),
            default_intake_gate_report(),
            default_deidentification_review(),
            workspace_id="demo-sensitive-study-coding-local",
            workspace_locator=StorageLocator(
                storage_scheme=StorageScheme.LOCAL_ENCRYPTED,
                locator=str((repo_root / "workspace").resolve()),
            ),
            created_by_role="analyst",
            repo_root=repo_root,
        )


def test_initialize_analysis_workspace_blocks_repo_local_deidentified_locator(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    review = default_deidentification_review()
    review.deidentified_locator = StorageLocator(
        storage_scheme=StorageScheme.LOCAL_ENCRYPTED,
        locator=str((repo_root / "deidentified" / "session-001.json").resolve()),
    )

    with pytest.raises(ValueError, match="outside the repository root"):
        initialize_analysis_workspace(
            default_study_manifest(),
            default_intake_gate_report(),
            review,
            workspace_id="demo-sensitive-study-coding-local",
            workspace_locator=StorageLocator(
                storage_scheme=StorageScheme.LOCAL_ENCRYPTED,
                locator=str((tmp_path / "workspace").resolve()),
            ),
            created_by_role="analyst",
            repo_root=repo_root,
        )


def test_initialize_analysis_workspace_requires_ready_gate(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    gate_report = default_intake_gate_report()
    gate_report.status = GateStatus.BLOCKED
    gate_report.analysis_ready = False

    with pytest.raises(ValueError, match="ready_for_analysis"):
        initialize_analysis_workspace(
            default_study_manifest(),
            gate_report,
            default_deidentification_review(),
            workspace_id="demo-sensitive-study-coding-local",
            workspace_locator=StorageLocator(
                storage_scheme=StorageScheme.LOCAL_ENCRYPTED,
                locator=str((tmp_path / "workspace").resolve()),
            ),
            created_by_role="analyst",
            repo_root=repo_root,
        )
