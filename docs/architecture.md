# Architecture

`qual-lab` is a local-first analysis framework for qualitative and mixed-methods
workflows that need explicit governance, auditability, and safe boundaries
before heavier automation enters the stack.

## Runtime Shape

```text
Study Manifest
    -> Intake Policy
    -> Protected Intake Record
    -> De-identification Review
    -> Intake Gate Report
    -> Audit Events
    -> Analysis Workspace
    -> Analysis Units / Codebook / Code Applications / Memos
    -> Framework Matrix
    -> Mixed-Method Join
    -> Team Coding Round / Adjudication
    -> Export Surface
```

The current implementation now hardens the governance, intake, and analysis
workspace spine:

- study-manifest contract
- audit-event contract
- protected intake contract
- de-identification review contract
- intake gate report
- analysis workspace contract
- analysis unit contract
- codebook version contract
- code application contract
- memo record contract
- framework matrix contract
- mixed-method join contract
- team coding round contract
- adjudication decision contract
- assistive algorithm policy gate contract
- synthesis export record contract
- repository policy
- audit-event builder
- analysis workspace initializer
- team coding round initializer
- assistive review capture helper
- synthesis export initializer
- repository doctor and CLI surface

## Core Entities

### Study Manifest

Pins the operational expectations for one study or analysis track:

- sensitivity level
- allowed modalities
- analysis modes
- canonical documents
- access roles
- retention policy
- external-model policy

### Audit Event

Captures one relevant analysis event in a machine-readable form:

- who acted
- what changed
- what artifact was touched
- sensitivity level
- result
- optional detail note

### Protected Intake Record

Captures one artifact staged for review outside the repository:

- artifact identity and study slug
- modality and sensitivity
- submitter role
- source locator and storage scheme
- direct-identifier / quasi-identifier flags
- code-key linkage and de-identification state

### De-identification Review

Captures the human review required before downstream analysis widens:

- review identity and reviewer role
- review outcome
- identifier findings and unresolved risks
- transformations applied
- approved downstream uses
- de-identified locator and residual sensitivity

### Intake Gate Report

Summarizes the combined manifest, intake, and review decision:

- blocked vs accepted-for-review vs ready-for-analysis
- blockers and warnings
- required actions
- approved uses
- recommended audit action

### Analysis Workspace

Defines the off-repo context for manual qualitative work after the intake gate:

- workspace identity and creator role
- off-repo workspace locator
- allowed analysis modes and approved uses
- source provenance back to review-approved artifacts

### Analysis Unit

Defines one de-identified span, excerpt, or response item available for coding:

- workspace and study binding
- source artifact and modality
- normalized text content
- optional speaker label and offsets

### Codebook Version

Defines one explicit coding surface for a workspace:

- version label and creator
- code definitions
- parent-child code relationships
- inclusion / exclusion criteria

### Code Application

Captures one manual coding action:

- target analysis unit
- codebook version and code id
- coder role and timestamp
- optional notes

### Memo Record

Captures one analytic, reflexive, methodological, or adjudication memo:

- memo kind, title, and body
- author role and timestamp
- linked units and codes

### Framework Matrix

Captures one structured synthesis matrix grounded in coded units and memos:

- declared framework dimensions
- explicit row basis such as case, site, or phase
- per-cell summaries with evidence anchors back to units, codes, and memos
- linked codebooks and memos for auditability

### Mixed-Method Join

Captures one bounded mixed-method joint display or integration table:

- quantitative findings with typed provenance labels
- qualitative summaries with explicit evidence anchors
- row-level integration relationship such as convergence or complementarity
- integrated interpretations grounded in both qualitative and quantitative evidence

### Team Coding Round

Captures one bounded collaborative coding workflow:

- facilitator, coder, and optional adjudicator roles
- linked codebooks and optional matrix/join artifacts under review
- assignment records tied to explicit units, focus codes, and supporting memos
- workflow status that stays inside the protected analysis boundary

### Adjudication Decision

Captures one explicit resolution of coding disagreement:

- the round and unit under review
- compared code-application records
- outcome shape such as confirmed, merged, or escalated
- rationale, retained codes, and follow-up actions
- optional links back to memos, matrices, and mixed-method joins

### Assistive Algorithm Policy Gate

Captures one explicit approval or denial for bounded assistive processing:

- requested algorithm label, runtime class, and intended use
- declared input and output storage locators
- explicit review requirements, decision state, and decision actor
- required controls for any approved path
- fail-closed handling for external-model requests without explicit policy alignment

### Synthesis Export Record

Captures one export artifact grounded in collaboration and synthesis evidence:

- export kind and output locator
- linked source artifacts (codebooks, matrices, joins, team rounds, adjudications, memos)
- approved-use scope and resulting sensitivity label
- explicit assistive gate linkage when assistive algorithms contributed
- audit-event references for downstream governance traceability

### Repository Policy

Defines the default posture for the repository independent of any one study:

- local-first by default
- raw identifiable data does not belong in the repo
- synthetic fixtures only under `examples/`
- external model use disabled by default
- human review required for de-identification-sensitive paths

## Boundary Surfaces

- `src/qual_lab/`: typed contracts, policy helpers, doctor, and CLI
- `src/qual_lab/intake.py`: protected-intake gate evaluator
- `src/qual_lab/workspace.py`: analysis workspace initializer
- `src/qual_lab/synthesis.py`: assistive review capture and synthesis export helpers
- `src/qual_lab/audit.py`: validated audit-event builder
- `src/qual_lab/boundaries.py`: shared off-repo storage boundary checks
- `contracts/`: generated JSON schemas derived from the runtime contracts
- `examples/`: synthetic fixtures that validate the contract shape
- `artifacts/`: generated outputs and review bundles
- `tests/`: validation for the typed contracts and CLI

## Design Constraints

- fail closed when sensitivity, approval, or de-identification state is unclear
- fail closed when intake source boundaries are ambiguous or point into the repo
- fail closed when de-identified sources or workspace roots point into the repo
- keep study-specific rationale and unpublished findings outside repo docs
- prefer explicit contracts and audit events over hidden notebook state
- stage automation after the governance, intake, workspace, and coding seams are stable
