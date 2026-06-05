from __future__ import annotations

import pytest

from qual_lab.collaboration import initialize_team_coding_round
from qual_lab.models import ApprovedUse, default_analysis_workspace, default_study_manifest


def test_initialize_team_coding_round_succeeds() -> None:
    round_record, audit_event = initialize_team_coding_round(
        default_study_manifest(),
        default_analysis_workspace(),
        round_id="demo-sensitive-study-round-local",
        facilitator_role="senior_analyst",
        coder_roles=["analyst", "senior_analyst"],
        adjudicator_role="study_steward",
        linked_codebook_ids=["demo-sensitive-study-core"],
        linked_framework_matrix_ids=["demo-sensitive-study-framework-matrix"],
        linked_mixed_method_join_ids=["demo-sensitive-study-joint-display"],
        created_by_role="senior_analyst",
    )

    assert round_record.round_id == "demo-sensitive-study-round-local"
    assert round_record.assignments == []
    assert audit_event.action == "initialized_team_coding_round"


def test_initialize_team_coding_round_requires_team_coding_approval() -> None:
    workspace = default_analysis_workspace()
    workspace.allowed_approved_uses = [ApprovedUse.INTERNAL_ANALYSIS]

    with pytest.raises(ValueError, match="team_coding"):
        initialize_team_coding_round(
            default_study_manifest(),
            workspace,
            round_id="demo-sensitive-study-round-local",
            facilitator_role="senior_analyst",
            coder_roles=["analyst", "senior_analyst"],
            adjudicator_role="study_steward",
            linked_codebook_ids=["demo-sensitive-study-core"],
            created_by_role="senior_analyst",
        )
