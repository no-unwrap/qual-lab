from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

from pydantic import BaseModel, ValidationError

from qual_lab import __version__
from qual_lab.audit import build_audit_event
from qual_lab.collaboration import initialize_team_coding_round
from qual_lab.doctor import run_doctor
from qual_lab.intake import assess_intake
from qual_lab.models import (
    AdjudicationDecision,
    AnalysisUnit,
    AnalysisWorkspace,
    ApprovedUse,
    AssistiveAlgorithmPolicyGate,
    AssistiveAlgorithmRuntime,
    AssistivePolicyDecision,
    AuditEvent,
    AuditResult,
    CodeApplication,
    CodebookVersion,
    DeidentificationReview,
    FrameworkMatrix,
    IntakeGateReport,
    MemoRecord,
    MixedMethodJoin,
    ProtectedIntakeRecord,
    SensitivityLevel,
    StorageLocator,
    StorageScheme,
    StudyManifest,
    SynthesisExportKind,
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
    default_intake_gate_report,
    default_memo_record,
    default_mixed_method_join,
    default_protected_intake_record,
    default_study_manifest,
    default_synthesis_export_record,
    default_team_coding_round,
)
from qual_lab.policies import default_policy
from qual_lab.synthesis import capture_assistive_review, initialize_synthesis_export_record
from qual_lab.workspace import initialize_analysis_workspace

# ---------------------------------------------------------------------------
# Contract registry: maps CLI kind names to (model, default_factory, arg_name)
# ---------------------------------------------------------------------------

_CONTRACT_REGISTRY: list[tuple[str, type[BaseModel], Callable[[], BaseModel], str]] = [
    ("study-manifest", StudyManifest, default_study_manifest, "manifest"),
    ("audit-event", AuditEvent, default_audit_event, "event"),
    ("protected-intake", ProtectedIntakeRecord, default_protected_intake_record, "intake"),
    (
        "deidentification-review",
        DeidentificationReview,
        default_deidentification_review,
        "review",
    ),
    ("intake-gate-report", IntakeGateReport, default_intake_gate_report, "report"),
    ("analysis-workspace", AnalysisWorkspace, default_analysis_workspace, "workspace"),
    ("analysis-unit", AnalysisUnit, default_analysis_unit, "unit"),
    ("codebook-version", CodebookVersion, default_codebook_version, "codebook"),
    ("code-application", CodeApplication, default_code_application, "application"),
    ("memo-record", MemoRecord, default_memo_record, "memo"),
    ("framework-matrix", FrameworkMatrix, default_framework_matrix, "matrix"),
    ("mixed-method-join", MixedMethodJoin, default_mixed_method_join, "join"),
    ("team-coding-round", TeamCodingRound, default_team_coding_round, "round"),
    (
        "adjudication-decision",
        AdjudicationDecision,
        default_adjudication_decision,
        "decision",
    ),
    (
        "assistive-algorithm-policy-gate",
        AssistiveAlgorithmPolicyGate,
        default_assistive_algorithm_policy_gate,
        "gate",
    ),
    (
        "synthesis-export-record",
        SynthesisExportRecord,
        default_synthesis_export_record,
        "export",
    ),
]

_VALIDATE_COMMANDS: dict[str, tuple[type[BaseModel], str]] = {
    f"validate-{kind}": (model, arg_name)
    for kind, model, _, arg_name in _CONTRACT_REGISTRY
}
_TEMPLATE_COMMANDS: dict[str, Callable[[], BaseModel]] = {
    f"emit-{kind}-template": factory for kind, _, factory, _ in _CONTRACT_REGISTRY
}
_SCHEMA_DISPATCH: dict[str, type[BaseModel]] = {
    kind: model for kind, model, _, _ in _CONTRACT_REGISTRY
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _make_storage_locator(*, scheme: str, locator: str) -> StorageLocator:
    return StorageLocator(
        storage_scheme=StorageScheme(scheme),
        locator=locator,
    )


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qual-lab",
        description="Local-first qualitative and mixed-methods analysis framework.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the qual-lab package version and exit.",
    )
    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser(
        "doctor",
        help="Inspect the expected repository layout and report the default policy posture.",
    )
    doctor.add_argument(
        "--repo-root",
        help="Optional repository root to inspect. Defaults to the current working directory.",
    )

    subparsers.add_parser(
        "show-policy",
        help="Print the repository-wide default policy.",
    )

    # --- validate-* and emit-*-template subcommands (registry-driven) ------
    for kind, _, _, arg_name in _CONTRACT_REGISTRY:
        label = kind.replace("-", " ")

        validate_parser = subparsers.add_parser(
            f"validate-{kind}",
            help=f"Validate one {label} JSON file and print the normalized payload.",
        )
        validate_parser.add_argument(
            f"--{arg_name}",
            required=True,
            help=f"Path to a {label} JSON file.",
        )

        subparsers.add_parser(
            f"emit-{kind}-template",
            help=f"Print a synthetic {label} template.",
        )

    # --- workflow commands --------------------------------------------------
    assess_intake_parser = subparsers.add_parser(
        "assess-intake",
        help="Evaluate whether an intake artifact is blocked, accepted for review, or ready.",
    )
    assess_intake_parser.add_argument(
        "--manifest", required=True, help="Path to a study manifest JSON file."
    )
    assess_intake_parser.add_argument(
        "--intake", required=True, help="Path to a protected intake JSON file."
    )
    assess_intake_parser.add_argument(
        "--review", help="Optional path to a de-identification review JSON file."
    )
    assess_intake_parser.add_argument(
        "--repo-root", help="Optional repository root used for boundary checks."
    )

    init_workspace = subparsers.add_parser(
        "init-analysis-workspace",
        help="Initialize an analysis workspace from a ready_for_analysis gate report.",
    )
    init_workspace.add_argument(
        "--manifest", required=True, help="Path to a study manifest JSON file."
    )
    init_workspace.add_argument(
        "--gate-report", required=True, help="Path to an intake gate report JSON file."
    )
    init_workspace.add_argument(
        "--review", required=True, help="Path to an approved de-identification review JSON file."
    )
    init_workspace.add_argument(
        "--workspace-id",
        required=True,
        help="Workspace identifier to assign to the initialized analysis workspace.",
    )
    init_workspace.add_argument(
        "--workspace-root",
        required=True,
        help="Locator or absolute path for the workspace storage root.",
    )
    init_workspace.add_argument(
        "--workspace-scheme",
        choices=[s.value for s in StorageScheme],
        default=StorageScheme.LOCAL_ENCRYPTED.value,
        help="Storage scheme for the workspace root.",
    )
    init_workspace.add_argument(
        "--created-by-role",
        required=True,
        help="Role responsible for initializing the analysis workspace.",
    )
    init_workspace.add_argument(
        "--repo-root", help="Optional repository root used for off-repo boundary checks."
    )

    init_round = subparsers.add_parser(
        "init-team-coding-round",
        help="Initialize a team coding round from an analysis workspace approved for team coding.",
    )
    init_round.add_argument(
        "--manifest", required=True, help="Path to a study manifest JSON file."
    )
    init_round.add_argument(
        "--workspace", required=True, help="Path to an analysis workspace JSON file."
    )
    init_round.add_argument(
        "--round-id",
        required=True,
        help="Team coding round identifier to assign to the initialized workflow.",
    )
    init_round.add_argument(
        "--created-by-role",
        required=True,
        help="Role responsible for initializing the team coding round.",
    )
    init_round.add_argument(
        "--facilitator-role",
        required=True,
        help="Role responsible for facilitating the team coding round.",
    )
    init_round.add_argument(
        "--coder-role",
        action="append",
        dest="coder_roles",
        required=True,
        help="Coder role participating in the round. Repeat for multiple coders.",
    )
    init_round.add_argument(
        "--adjudicator-role", help="Optional adjudicator role for the round."
    )
    init_round.add_argument(
        "--codebook-id",
        action="append",
        dest="codebook_ids",
        required=True,
        help="Linked codebook identifier. Repeat to link multiple codebooks.",
    )
    init_round.add_argument(
        "--framework-matrix-id",
        action="append",
        dest="framework_matrix_ids",
        help="Optional linked framework matrix identifier. Repeat if needed.",
    )
    init_round.add_argument(
        "--mixed-method-join-id",
        action="append",
        dest="mixed_method_join_ids",
        help="Optional linked mixed-method join identifier. Repeat if needed.",
    )

    capture_assistive = subparsers.add_parser(
        "capture-assistive-review",
        help="Capture a bounded assistive review and emit the resulting gate plus audit event.",
    )
    capture_assistive.add_argument(
        "--manifest", required=True, help="Path to a study manifest JSON file."
    )
    capture_assistive.add_argument(
        "--workspace", required=True, help="Path to an analysis workspace JSON file."
    )
    capture_assistive.add_argument(
        "--gate-id", required=True, help="Assistive policy gate identifier to assign."
    )
    capture_assistive.add_argument(
        "--requested-by-role", required=True, help="Role requesting the assistive review."
    )
    capture_assistive.add_argument(
        "--decision-by-role", required=True, help="Role recording the assistive review decision."
    )
    capture_assistive.add_argument(
        "--algorithm-label", required=True, help="Assistive algorithm label under review."
    )
    capture_assistive.add_argument(
        "--algorithm-runtime",
        choices=[runtime.value for runtime in AssistiveAlgorithmRuntime],
        required=True,
        help="Runtime class for the assistive algorithm.",
    )
    capture_assistive.add_argument(
        "--purpose", required=True, help="Purpose for the bounded assistive review."
    )
    capture_assistive.add_argument(
        "--proposed-use",
        action="append",
        dest="proposed_uses",
        choices=[approved_use.value for approved_use in ApprovedUse],
        required=True,
        help="Requested approved use. Repeat to record multiple uses.",
    )
    capture_assistive.add_argument(
        "--input-locator",
        required=True,
        help="Locator or absolute path for the assistive input artifact.",
    )
    capture_assistive.add_argument(
        "--input-scheme",
        choices=[scheme.value for scheme in StorageScheme],
        default=StorageScheme.SECURE_URI.value,
        help="Storage scheme for the assistive input locator.",
    )
    capture_assistive.add_argument(
        "--decision",
        choices=[decision.value for decision in AssistivePolicyDecision],
        required=True,
        help="Review decision for the assistive request.",
    )
    capture_assistive.add_argument(
        "--decision-rationale", required=True, help="Rationale for the assistive review decision."
    )
    capture_assistive.add_argument(
        "--output-locator",
        help="Locator or absolute path for assistive output. Required for approved decisions.",
    )
    capture_assistive.add_argument(
        "--output-scheme",
        choices=[scheme.value for scheme in StorageScheme],
        default=StorageScheme.SECURE_URI.value,
        help="Storage scheme for the assistive output locator.",
    )
    capture_assistive.add_argument(
        "--required-control",
        action="append",
        dest="required_controls",
        help="Required control to enforce for approved paths. Repeat as needed.",
    )
    capture_assistive.add_argument(
        "--note",
        action="append",
        dest="notes",
        help="Optional note to append to the captured gate.",
    )
    capture_assistive.add_argument(
        "--repo-root", help="Optional repository root used for off-repo boundary checks."
    )

    init_export = subparsers.add_parser(
        "init-synthesis-export-record",
        help="Initialize a synthesis export record from bounded collaboration artifacts.",
    )
    init_export.add_argument(
        "--manifest", required=True, help="Path to a study manifest JSON file."
    )
    init_export.add_argument(
        "--workspace", required=True, help="Path to an analysis workspace JSON file."
    )
    init_export.add_argument(
        "--export-id", required=True, help="Synthesis export identifier to assign."
    )
    init_export.add_argument(
        "--created-by-role", required=True, help="Role responsible for initializing the export."
    )
    init_export.add_argument(
        "--export-kind",
        choices=[kind.value for kind in SynthesisExportKind],
        required=True,
        help="Synthesis export kind to initialize.",
    )
    init_export.add_argument(
        "--approved-use",
        action="append",
        dest="approved_uses",
        choices=[approved_use.value for approved_use in ApprovedUse],
        required=True,
        help="Approved use captured by the export. Repeat as needed.",
    )
    init_export.add_argument(
        "--sensitivity",
        choices=[sensitivity.value for sensitivity in SensitivityLevel],
        required=True,
        help="Sensitivity label assigned to the export.",
    )
    init_export.add_argument(
        "--export-locator",
        required=True,
        help="Locator or absolute path for the export artifact.",
    )
    init_export.add_argument(
        "--export-scheme",
        choices=[scheme.value for scheme in StorageScheme],
        default=StorageScheme.SECURE_URI.value,
        help="Storage scheme for the export locator.",
    )
    init_export.add_argument(
        "--source-codebook-id",
        action="append",
        dest="source_codebook_ids",
        help="Source codebook identifier. Repeat to link multiple codebooks.",
    )
    init_export.add_argument(
        "--source-framework-matrix-id",
        action="append",
        dest="source_framework_matrix_ids",
        help="Source framework matrix identifier. Repeat as needed.",
    )
    init_export.add_argument(
        "--source-mixed-method-join-id",
        action="append",
        dest="source_mixed_method_join_ids",
        help="Source mixed-method join identifier. Repeat as needed.",
    )
    init_export.add_argument(
        "--source-team-coding-round-id",
        action="append",
        dest="source_team_coding_round_ids",
        help="Source team coding round identifier. Repeat as needed.",
    )
    init_export.add_argument(
        "--source-adjudication-decision-id",
        action="append",
        dest="source_adjudication_decision_ids",
        help="Source adjudication decision identifier. Repeat as needed.",
    )
    init_export.add_argument(
        "--source-memo-id",
        action="append",
        dest="source_memo_ids",
        help="Source memo identifier. Repeat as needed.",
    )
    init_export.add_argument(
        "--assistive-gate",
        help="Optional path to an assistive algorithm policy gate JSON file.",
    )
    init_export.add_argument(
        "--assistive-algorithm",
        action="append",
        dest="assistive_algorithms",
        help="Assistive algorithm label applied to the export. Repeat as needed.",
    )
    init_export.add_argument(
        "--audit-event-id",
        action="append",
        dest="audit_event_ids",
        help="Existing audit event identifier to reference. Repeat as needed.",
    )
    init_export.add_argument(
        "--note",
        action="append",
        dest="notes",
        help="Optional note to append to the export record.",
    )
    init_export.add_argument(
        "--repo-root", help="Optional repository root used for off-repo boundary checks."
    )

    build_event = subparsers.add_parser(
        "build-audit-event",
        help="Build a validated audit event for one repository workflow action.",
    )
    build_event.add_argument("--actor-role", required=True, help="Actor role.")
    build_event.add_argument("--action", required=True, help="Action name.")
    build_event.add_argument("--target-type", required=True, help="Target type.")
    build_event.add_argument("--target-id", required=True, help="Target identifier.")
    build_event.add_argument(
        "--sensitivity",
        choices=[s.value for s in SensitivityLevel],
        required=True,
        help="Sensitivity of the affected artifact or action.",
    )
    build_event.add_argument(
        "--result",
        choices=[r.value for r in AuditResult],
        default=AuditResult.SUCCESS.value,
        help="Audit result state.",
    )
    build_event.add_argument("--details", help="Optional free-text detail note.")

    emit_schema = subparsers.add_parser(
        "emit-contract-schema",
        help="Print the JSON schema for one supported contract kind.",
    )
    emit_schema.add_argument(
        "--kind",
        choices=list(_SCHEMA_DISPATCH),
        required=True,
        help="Contract kind to emit.",
    )

    return parser


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"qual-lab {__version__}")
        return 0

    try:
        if args.command == "doctor":
            _print_json(run_doctor(repo_root=args.repo_root).to_dict())
            return 0

        if args.command == "show-policy":
            _print_json(default_policy().to_dict())
            return 0

        # --- registry-driven validate-* commands --------------------------
        if args.command in _VALIDATE_COMMANDS:
            model_class, arg_name = _VALIDATE_COMMANDS[args.command]
            instance = model_class.model_validate(_load_json(getattr(args, arg_name)))
            _print_json(instance.model_dump(mode="json"))
            return 0

        # --- registry-driven emit-*-template commands ---------------------
        if args.command in _TEMPLATE_COMMANDS:
            factory = _TEMPLATE_COMMANDS[args.command]
            _print_json(factory().model_dump(mode="json"))
            return 0

        # --- registry-driven emit-contract-schema -------------------------
        if args.command == "emit-contract-schema":
            _print_json(_SCHEMA_DISPATCH[args.kind].model_json_schema())
            return 0

        # --- workflow commands --------------------------------------------
        if args.command == "assess-intake":
            manifest = StudyManifest.model_validate(_load_json(args.manifest))
            intake = ProtectedIntakeRecord.model_validate(_load_json(args.intake))
            review_record: DeidentificationReview | None = None
            if args.review:
                review_record = DeidentificationReview.model_validate(_load_json(args.review))
            report = assess_intake(
                manifest,
                intake,
                review=review_record,
                repo_root=args.repo_root,
            )
            _print_json(report.model_dump(mode="json"))
            return 0

        if args.command == "init-analysis-workspace":
            manifest = StudyManifest.model_validate(_load_json(args.manifest))
            gate_report = IntakeGateReport.model_validate(_load_json(args.gate_report))
            review = DeidentificationReview.model_validate(_load_json(args.review))
            workspace, audit_event = initialize_analysis_workspace(
                manifest,
                gate_report,
                review,
                workspace_id=args.workspace_id,
                workspace_locator=_make_storage_locator(
                    scheme=args.workspace_scheme,
                    locator=args.workspace_root,
                ),
                created_by_role=args.created_by_role,
                repo_root=args.repo_root,
            )
            _print_json(
                {
                    "workspace": workspace.model_dump(mode="json"),
                    "audit_event": audit_event.model_dump(mode="json"),
                }
            )
            return 0

        if args.command == "init-team-coding-round":
            manifest = StudyManifest.model_validate(_load_json(args.manifest))
            workspace = AnalysisWorkspace.model_validate(_load_json(args.workspace))
            team_coding_round, audit_event = initialize_team_coding_round(
                manifest,
                workspace,
                round_id=args.round_id,
                facilitator_role=args.facilitator_role,
                coder_roles=args.coder_roles,
                adjudicator_role=args.adjudicator_role,
                linked_codebook_ids=args.codebook_ids,
                linked_framework_matrix_ids=args.framework_matrix_ids,
                linked_mixed_method_join_ids=args.mixed_method_join_ids,
                created_by_role=args.created_by_role,
            )
            _print_json(
                {
                    "team_coding_round": team_coding_round.model_dump(mode="json"),
                    "audit_event": audit_event.model_dump(mode="json"),
                }
            )
            return 0

        if args.command == "capture-assistive-review":
            manifest = StudyManifest.model_validate(_load_json(args.manifest))
            workspace = AnalysisWorkspace.model_validate(_load_json(args.workspace))
            output_locator = None
            if args.output_locator:
                output_locator = _make_storage_locator(
                    scheme=args.output_scheme,
                    locator=args.output_locator,
                )
            gate, audit_event = capture_assistive_review(
                manifest,
                workspace,
                gate_id=args.gate_id,
                requested_by_role=args.requested_by_role,
                decision_by_role=args.decision_by_role,
                algorithm_label=args.algorithm_label,
                algorithm_runtime=AssistiveAlgorithmRuntime(args.algorithm_runtime),
                purpose=args.purpose,
                proposed_uses=[
                    ApprovedUse(approved_use) for approved_use in args.proposed_uses
                ],
                input_locator=_make_storage_locator(
                    scheme=args.input_scheme,
                    locator=args.input_locator,
                ),
                output_locator=output_locator,
                decision=AssistivePolicyDecision(args.decision),
                decision_rationale=args.decision_rationale,
                required_controls=list(args.required_controls or []),
                notes=list(args.notes or []),
                repo_root=args.repo_root,
            )
            _print_json(
                {
                    "assistive_algorithm_policy_gate": gate.model_dump(mode="json"),
                    "audit_event": audit_event.model_dump(mode="json"),
                }
            )
            return 0

        if args.command == "init-synthesis-export-record":
            manifest = StudyManifest.model_validate(_load_json(args.manifest))
            workspace = AnalysisWorkspace.model_validate(_load_json(args.workspace))
            assistive_gate: AssistiveAlgorithmPolicyGate | None = None
            if args.assistive_gate:
                assistive_gate = AssistiveAlgorithmPolicyGate.model_validate(
                    _load_json(args.assistive_gate)
                )
            synthesis_export_record, audit_event = initialize_synthesis_export_record(
                manifest,
                workspace,
                export_id=args.export_id,
                created_by_role=args.created_by_role,
                export_kind=SynthesisExportKind(args.export_kind),
                included_approved_uses=[
                    ApprovedUse(approved_use) for approved_use in args.approved_uses
                ],
                sensitivity=SensitivityLevel(args.sensitivity),
                export_locator=_make_storage_locator(
                    scheme=args.export_scheme,
                    locator=args.export_locator,
                ),
                source_codebook_ids=list(args.source_codebook_ids or []),
                source_framework_matrix_ids=list(args.source_framework_matrix_ids or []),
                source_mixed_method_join_ids=list(args.source_mixed_method_join_ids or []),
                source_team_coding_round_ids=list(args.source_team_coding_round_ids or []),
                source_adjudication_decision_ids=list(
                    args.source_adjudication_decision_ids or []
                ),
                source_memo_ids=list(args.source_memo_ids or []),
                assistive_gate=assistive_gate,
                assistive_algorithms_applied=list(args.assistive_algorithms or []),
                audit_event_ids=list(args.audit_event_ids or []),
                notes=list(args.notes or []),
                repo_root=args.repo_root,
            )
            _print_json(
                {
                    "synthesis_export_record": synthesis_export_record.model_dump(mode="json"),
                    "audit_event": audit_event.model_dump(mode="json"),
                }
            )
            return 0

        if args.command == "build-audit-event":
            event = build_audit_event(
                actor_role=args.actor_role,
                action=args.action,
                target_type=args.target_type,
                target_id=args.target_id,
                sensitivity=SensitivityLevel(args.sensitivity),
                result=AuditResult(args.result),
                details=args.details,
            )
            _print_json(event.model_dump(mode="json"))
            return 0

    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (ValidationError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
