from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RepositoryPolicy:
    local_first_runtime: bool = True
    raw_identifiable_data_in_repo: bool = False
    synthetic_examples_only: bool = True
    external_model_calls_default: str = "disabled"
    protected_intake_required: bool = True
    repo_tracked_intake_sources_allowed: bool = False
    deidentification_review_required: bool = True
    deidentified_analysis_requires_review_approval: bool = True
    analysis_workspace_required_for_coding: bool = True
    workspace_storage_outside_repo_required: bool = True
    manual_coding_contracts_enabled: bool = True
    public_docs_scope: str = "codebase_only"
    study_manifest_required: bool = True
    audit_events_required_for_sensitive_transforms: bool = True
    mixed_methods_supported: bool = True
    team_coding_supported: bool = True
    adjudication_supported: bool = True
    synthesis_exports_supported: bool = True
    assistive_algorithm_policy_gates_required: bool = True
    external_assistive_processing_requires_explicit_gate: bool = True

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def default_policy() -> RepositoryPolicy:
    return RepositoryPolicy()
