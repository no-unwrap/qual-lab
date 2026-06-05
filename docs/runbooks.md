# Runbooks

## Setup

```bash
just setup
```

## Validation

```bash
just lint
just typecheck
just test
just audit-public
```

## CLI Reference

Print the current version:

```bash
.venv/bin/python -m qual_lab.main --version
```

Show the repository-wide default policy:

```bash
.venv/bin/python -m qual_lab.main show-policy
```

Inspect the expected repository layout:

```bash
.venv/bin/python -m qual_lab.main doctor
```

Validate a study manifest:

```bash
.venv/bin/python -m qual_lab.main validate-study-manifest --manifest examples/demo_study_manifest.json
```

Validate an audit event:

```bash
.venv/bin/python -m qual_lab.main validate-audit-event --event examples/demo_audit_event.json
```

Validate a protected intake:

```bash
.venv/bin/python -m qual_lab.main validate-protected-intake --intake examples/demo_protected_intake.json
```

Validate a de-identification review:

```bash
.venv/bin/python -m qual_lab.main validate-deidentification-review --review examples/demo_deidentification_review.json
```

Validate the analysis workspace and coding-layer contracts:

```bash
.venv/bin/python -m qual_lab.main validate-analysis-workspace --workspace examples/demo_analysis_workspace.json
.venv/bin/python -m qual_lab.main validate-analysis-unit --unit examples/demo_analysis_unit.json
.venv/bin/python -m qual_lab.main validate-codebook-version --codebook examples/demo_codebook_version.json
.venv/bin/python -m qual_lab.main validate-code-application --application examples/demo_code_application.json
.venv/bin/python -m qual_lab.main validate-memo-record --memo examples/demo_memo_record.json
.venv/bin/python -m qual_lab.main validate-framework-matrix --matrix examples/demo_framework_matrix.json
.venv/bin/python -m qual_lab.main validate-mixed-method-join --join examples/demo_mixed_method_join.json
.venv/bin/python -m qual_lab.main validate-team-coding-round --round examples/demo_team_coding_round.json
.venv/bin/python -m qual_lab.main validate-adjudication-decision --decision examples/demo_adjudication_decision.json
.venv/bin/python -m qual_lab.main validate-assistive-algorithm-policy-gate --gate examples/demo_assistive_algorithm_policy_gate.json
.venv/bin/python -m qual_lab.main validate-synthesis-export-record --export examples/demo_synthesis_export_record.json
```

Assess whether an intake artifact is blocked, accepted for review, or ready for analysis:

```bash
.venv/bin/python -m qual_lab.main assess-intake --manifest examples/demo_study_manifest.json --intake examples/demo_protected_intake.json
.venv/bin/python -m qual_lab.main assess-intake --manifest examples/demo_study_manifest.json --intake examples/demo_protected_intake.json --review examples/demo_deidentification_review.json
```

Initialize an analysis workspace from an approved intake path:

```bash
.venv/bin/python -m qual_lab.main init-analysis-workspace --manifest examples/demo_study_manifest.json --gate-report examples/demo_intake_gate_report.json --review examples/demo_deidentification_review.json --workspace-id demo-sensitive-study-coding-cli --workspace-root secure://workspace/demo-sensitive-study/coding-cli --workspace-scheme secure_uri --created-by-role analyst
```

Initialize a team coding round from a workspace already approved for team coding:

```bash
.venv/bin/python -m qual_lab.main init-team-coding-round --manifest examples/demo_study_manifest.json --workspace examples/demo_analysis_workspace.json --round-id demo-sensitive-study-round-cli --created-by-role senior_analyst --facilitator-role senior_analyst --coder-role analyst --coder-role senior_analyst --adjudicator-role study_steward --codebook-id demo-sensitive-study-core --framework-matrix-id demo-sensitive-study-framework-matrix --mixed-method-join-id demo-sensitive-study-joint-display
```

Capture a bounded assistive review and emit the policy gate plus audit event:

```bash
.venv/bin/python -m qual_lab.main capture-assistive-review --manifest examples/demo_study_manifest.json --workspace examples/demo_analysis_workspace.json --gate-id demo-sensitive-study-assistive-gate-cli --requested-by-role senior_analyst --decision-by-role study_steward --algorithm-label bounded_theme_suggester_cli --algorithm-runtime local_statistical --purpose "Generate bounded candidate themes for analyst review." --proposed-use internal_analysis --input-locator secure://workspace/demo-sensitive-study/coding/synthesis-input-cli.json --decision approved_with_conditions --decision-rationale "Approved for local-first review only." --output-locator secure://workspace/demo-sensitive-study/coding/assistive-output-cli.json --required-control "Require manual analyst confirmation before release."
```

Initialize a synthesis export record from bounded collaboration artifacts:

```bash
.venv/bin/python -m qual_lab.main init-synthesis-export-record --manifest examples/demo_study_manifest.json --workspace examples/demo_analysis_workspace.json --export-id demo-sensitive-study-synthesis-export-cli --created-by-role senior_analyst --export-kind mixed_method_brief --approved-use internal_analysis --sensitivity restricted --export-locator secure://exports/demo-sensitive-study/synthesis-export-cli.json --source-codebook-id demo-sensitive-study-core --source-framework-matrix-id demo-sensitive-study-framework-matrix --source-mixed-method-join-id demo-sensitive-study-joint-display --source-team-coding-round-id demo-sensitive-study-round-001 --source-adjudication-decision-id adjudication-unit-session-001-001 --source-memo-id memo-session-001-001 --assistive-gate examples/demo_assistive_algorithm_policy_gate.json --assistive-algorithm bounded_theme_suggester_v1 --audit-event-id event-demo-sensitive-study-export-cli
```

Build a validated audit event:

```bash
.venv/bin/python -m qual_lab.main build-audit-event --actor-role analyst --action coded_analysis_unit --target-type code_application --target-id app-session-001-001-usability-breakdown --sensitivity restricted
```

Emit example templates:

```bash
.venv/bin/python -m qual_lab.main emit-study-manifest-template
.venv/bin/python -m qual_lab.main emit-audit-event-template
.venv/bin/python -m qual_lab.main emit-protected-intake-template
.venv/bin/python -m qual_lab.main emit-deidentification-review-template
.venv/bin/python -m qual_lab.main emit-intake-gate-report-template
.venv/bin/python -m qual_lab.main emit-analysis-workspace-template
.venv/bin/python -m qual_lab.main emit-analysis-unit-template
.venv/bin/python -m qual_lab.main emit-codebook-version-template
.venv/bin/python -m qual_lab.main emit-code-application-template
.venv/bin/python -m qual_lab.main emit-memo-record-template
.venv/bin/python -m qual_lab.main emit-framework-matrix-template
.venv/bin/python -m qual_lab.main emit-mixed-method-join-template
.venv/bin/python -m qual_lab.main emit-team-coding-round-template
.venv/bin/python -m qual_lab.main emit-adjudication-decision-template
.venv/bin/python -m qual_lab.main emit-assistive-algorithm-policy-gate-template
.venv/bin/python -m qual_lab.main emit-synthesis-export-record-template
```

Emit a JSON schema:

```bash
.venv/bin/python -m qual_lab.main emit-contract-schema --kind study-manifest
.venv/bin/python -m qual_lab.main emit-contract-schema --kind audit-event
.venv/bin/python -m qual_lab.main emit-contract-schema --kind protected-intake
.venv/bin/python -m qual_lab.main emit-contract-schema --kind deidentification-review
.venv/bin/python -m qual_lab.main emit-contract-schema --kind intake-gate-report
.venv/bin/python -m qual_lab.main emit-contract-schema --kind analysis-workspace
.venv/bin/python -m qual_lab.main emit-contract-schema --kind analysis-unit
.venv/bin/python -m qual_lab.main emit-contract-schema --kind codebook-version
.venv/bin/python -m qual_lab.main emit-contract-schema --kind code-application
.venv/bin/python -m qual_lab.main emit-contract-schema --kind memo-record
.venv/bin/python -m qual_lab.main emit-contract-schema --kind framework-matrix
.venv/bin/python -m qual_lab.main emit-contract-schema --kind mixed-method-join
.venv/bin/python -m qual_lab.main emit-contract-schema --kind team-coding-round
.venv/bin/python -m qual_lab.main emit-contract-schema --kind adjudication-decision
.venv/bin/python -m qual_lab.main emit-contract-schema --kind assistive-algorithm-policy-gate
.venv/bin/python -m qual_lab.main emit-contract-schema --kind synthesis-export-record
```

## Operator Notes

- keep raw identifiable materials outside the repository
- use synthetic fixtures for tests, docs, and examples
- treat generated exports as review artifacts, not source inputs
- treat protected intake as a staged boundary, not implicit local notebook state
- keep de-identified workspace roots and source locators outside the repository
- keep study-specific forbidden terms in an untracked local patterns file when
  you need stricter release gating than the repo-default audit
