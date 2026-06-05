from __future__ import annotations

from datetime import datetime, timezone

from qual_lab.audit import build_audit_event
from qual_lab.models import (
    AnalysisWorkspace,
    ApprovedUse,
    AuditEvent,
    SensitivityLevel,
    StudyManifest,
    TeamCodingRound,
)


def _max_workspace_sensitivity(workspace: AnalysisWorkspace) -> SensitivityLevel:
    return max(
        (source.residual_sensitivity for source in workspace.source_artifacts),
        key=lambda sensitivity: sensitivity.rank,
    )


def initialize_team_coding_round(
    manifest: StudyManifest,
    workspace: AnalysisWorkspace,
    *,
    round_id: str,
    facilitator_role: str,
    coder_roles: list[str],
    adjudicator_role: str | None,
    linked_codebook_ids: list[str],
    linked_framework_matrix_ids: list[str] | None = None,
    linked_mixed_method_join_ids: list[str] | None = None,
    created_by_role: str,
) -> tuple[TeamCodingRound, AuditEvent]:
    blockers: list[str] = []

    role_map = {role.role_name: role for role in manifest.access_roles}
    declared_roles = {facilitator_role, created_by_role, *coder_roles}
    if adjudicator_role is not None:
        declared_roles.add(adjudicator_role)
    undeclared_roles = sorted(
        role_name for role_name in declared_roles if role_name not in role_map
    )
    if undeclared_roles:
        blockers.append(
            "team workflow roles must be declared in the study manifest: "
            + ", ".join(undeclared_roles)
        )

    if workspace.study_slug != manifest.study_slug:
        blockers.append("team workflow inputs must reference the same study_slug")
    if ApprovedUse.TEAM_CODING not in workspace.allowed_approved_uses:
        blockers.append("team workflows require analysis workspaces approved for team_coding")
    if len(coder_roles) < 2:
        blockers.append("team workflows require at least two coder_roles")
    if not linked_codebook_ids:
        blockers.append("team workflows require at least one linked_codebook_id")

    if blockers:
        raise ValueError("; ".join(blockers))

    round_record = TeamCodingRound(
        round_id=round_id,
        workspace_id=workspace.workspace_id,
        study_slug=manifest.study_slug,
        created_at=datetime.now(timezone.utc),
        created_by_role=created_by_role,
        facilitator_role=facilitator_role,
        coder_roles=coder_roles,
        adjudicator_role=adjudicator_role,
        linked_codebook_ids=linked_codebook_ids,
        linked_framework_matrix_ids=linked_framework_matrix_ids or [],
        linked_mixed_method_join_ids=linked_mixed_method_join_ids or [],
        assignments=[],
        notes=[
            "Initialized from an analysis workspace approved for team coding.",
            "Assignments may be added later without changing the workflow identity.",
        ],
    )
    audit_event = build_audit_event(
        actor_role=created_by_role,
        action="initialized_team_coding_round",
        target_type="team_coding_round",
        target_id=round_record.round_id,
        sensitivity=_max_workspace_sensitivity(workspace),
        details=(
            "Initialized a team-coding round from an approved analysis workspace "
            f"`{workspace.workspace_id}`."
        ),
    )
    return round_record, audit_event
