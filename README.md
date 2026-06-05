# qual-lab

Local-first qualitative and mixed-methods analysis framework for sensitive
study workflows.

A framework-oriented repository for turning study manifests, protected intake
contracts, analysis workspace context, coding structures, and synthesis outputs
into an auditable analysis runtime that stays useful across multiple studies.

## Design Intent

`qual-lab` is designed as a research instrument, not a notebook pile or
one-study script bundle.

It is meant to support:

- study manifests that pin canonical governance and access expectations
- local-first handling of sensitive materials
- explicit de-identification and export boundaries
- reusable workspace, coding, memo, and synthesis seams
- mixed-methods analysis that stays grounded in auditable artifacts

Key principle:

- governance, intake, analysis, and export contracts should be explicit before
  automation broadens

## Repo Map

- `src/qual_lab/`: active Python runtime for manifests, policies, doctor
  checks, protected intake, de-identification review, workspace initialization,
  coding contracts, synthesis/export helpers, audit helpers, and CLI entrypoints
- `tests/`: runtime and CLI validation surface
- `tools/`: repo-local operational scripts
- `contracts/`: generated contract schemas and notes about machine-readable
  boundaries
- `examples/`: synthetic examples only
- `artifacts/`: generated analysis outputs and review exports
- `docs/README.md`: docs index
- `docs/architecture.md`: runtime map and contract posture
- `docs/runbooks.md`: setup, validation, and operator reference

## 60-Second Setup

1. Use a Python environment that already contains the repo dependencies.
On declaratively managed workstations, no repo-local `.venv` is required.

```bash
just setup
```

2. Inspect the public CLI surface.

```bash
PYTHONPATH=src python -m qual_lab.main --version
PYTHONPATH=src python -m qual_lab.main show-policy
PYTHONPATH=src python -m qual_lab.main doctor
```

3. Validate the shipped example contracts.

```bash
PYTHONPATH=src python -m qual_lab.main validate-study-manifest --manifest examples/demo_study_manifest.json
PYTHONPATH=src python -m qual_lab.main validate-audit-event --event examples/demo_audit_event.json
PYTHONPATH=src python -m qual_lab.main validate-protected-intake --intake examples/demo_protected_intake.json
PYTHONPATH=src python -m qual_lab.main validate-deidentification-review --review examples/demo_deidentification_review.json
PYTHONPATH=src python -m qual_lab.main validate-analysis-workspace --workspace examples/demo_analysis_workspace.json
PYTHONPATH=src python -m qual_lab.main validate-codebook-version --codebook examples/demo_codebook_version.json
PYTHONPATH=src python -m qual_lab.main validate-framework-matrix --matrix examples/demo_framework_matrix.json
PYTHONPATH=src python -m qual_lab.main validate-mixed-method-join --join examples/demo_mixed_method_join.json
PYTHONPATH=src python -m qual_lab.main validate-team-coding-round --round examples/demo_team_coding_round.json
PYTHONPATH=src python -m qual_lab.main validate-adjudication-decision --decision examples/demo_adjudication_decision.json
PYTHONPATH=src python -m qual_lab.main validate-assistive-algorithm-policy-gate --gate examples/demo_assistive_algorithm_policy_gate.json
PYTHONPATH=src python -m qual_lab.main validate-synthesis-export-record --export examples/demo_synthesis_export_record.json
PYTHONPATH=src python -m qual_lab.main assess-intake --manifest examples/demo_study_manifest.json --intake examples/demo_protected_intake.json --review examples/demo_deidentification_review.json
```

4. Run the baseline validation passes.

```bash
just lint
just typecheck
just test
just audit-public
```

## How It Works

```text
Study Manifest
    -> Protected Intake
    -> De-identification Review
    -> Intake Gate
    -> Analysis Workspace
    -> Coding / Memos
    -> Framework Matrix
    -> Mixed-Method Join
    -> Team Coding / Adjudication
    -> Synthesis Export
```

- study manifests pin allowed modalities, roles, retention, and external-model
  posture
- intake surfaces should fail closed when sensitivity, approval state, or
  storage boundary is ambiguous
- de-identification review happens before broader downstream analysis surfaces
- analysis workspaces should be initialized from explicit `ready_for_analysis`
  gate outputs and off-repo de-identified sources
- coding and synthesis outputs are expected to stay artifact-backed and auditable

## Current Runtime Surfaces

- a typed study-manifest contract
- a typed audit-event contract
- a typed protected-intake contract
- a typed de-identification review contract
- a typed intake gate report generated from the manifest plus intake state
- a typed analysis workspace contract with source provenance
- a typed analysis unit contract for manual coding spans and excerpts
- a typed codebook version contract and code application contract
- a typed memo record contract
- a typed framework matrix contract for structured cross-case or cross-phase synthesis
- a typed mixed-method join contract for bounded joint displays grounded in qualitative evidence and quantitative findings
- a typed team coding round contract for collaborative coding plans and assignments
- a typed adjudication decision contract for resolving coding disagreements against explicit evidence
- a typed assistive algorithm policy gate contract for bounded assistive processing approvals
- a typed synthesis export record contract for governed analysis outputs
- a local-first repository policy surface
- a `doctor` command that verifies the expected repo layout
- a `build-audit-event` command for validated workflow audit records
- a `init-analysis-workspace` command that opens a workspace from a
  `ready_for_analysis` gate report and emits the corresponding audit event
- a `init-team-coding-round` command that opens a collaboration round from a
  workspace already approved for team coding and emits the corresponding audit event
- a `capture-assistive-review` command that records a bounded assistive review
  into the existing policy-gate contract and emits the corresponding audit event
- a `init-synthesis-export-record` command that initializes a synthesis export
  record from bounded collaboration artifacts and emits the corresponding audit event
- CLI commands for emitting, validating, and assessing runtime contracts

## Current Focus

- keep the governance, intake, and analysis workspace spine stable
- keep synthesis exports and assistive processing explicitly policy-gated and
  grounded in collaboration-layer artifacts
- keep automation behind explicit study-policy gates

## Safety Posture

- keep raw identifiable study data out of the repository
- keep examples synthetic and code-facing only
- disable external model calls by default
- require explicit assistive-policy approval before any synthesis export widens
  into an external-model path
- require human review for de-identification-sensitive flows
- keep de-identified workspace roots and source locators outside the repository
- keep public-facing docs focused on runtime and contracts, not study rationale

## Docs Map

- `docs/README.md`: docs index
- `docs/architecture.md`: architecture and runtime contract map
- `docs/runbooks.md`: bootstrap, validation, and CLI reference
- `contracts/README.md`: contract-file guidance
- `artifacts/README.md`: artifact-output guidance

## License

This project is licensed under the MIT License. See `LICENSE` for the full
text.
