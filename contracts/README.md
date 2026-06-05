# Contracts

Machine-readable contract files for `qual-lab`.

Current contract families:

- `study_manifest.schema.json`
- `audit_event.schema.json`
- `protected_intake_record.schema.json`
- `deidentification_review.schema.json`
- `intake_gate_report.schema.json`
- `analysis_workspace.schema.json`
- `analysis_unit.schema.json`
- `codebook_version.schema.json`
- `code_application.schema.json`
- `memo_record.schema.json`
- `framework_matrix.schema.json`
- `mixed_method_join.schema.json`
- `team_coding_round.schema.json`
- `adjudication_decision.schema.json`
- `assistive_algorithm_policy_gate.schema.json`
- `synthesis_export_record.schema.json`

These files should be generated from the typed runtime contracts rather than
hand-edited when practical.

```bash
.venv/bin/python -m qual_lab.main emit-contract-schema --kind study-manifest > contracts/study_manifest.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind audit-event > contracts/audit_event.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind protected-intake > contracts/protected_intake_record.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind deidentification-review > contracts/deidentification_review.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind intake-gate-report > contracts/intake_gate_report.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind analysis-workspace > contracts/analysis_workspace.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind analysis-unit > contracts/analysis_unit.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind codebook-version > contracts/codebook_version.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind code-application > contracts/code_application.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind memo-record > contracts/memo_record.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind framework-matrix > contracts/framework_matrix.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind mixed-method-join > contracts/mixed_method_join.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind team-coding-round > contracts/team_coding_round.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind adjudication-decision > contracts/adjudication_decision.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind assistive-algorithm-policy-gate > contracts/assistive_algorithm_policy_gate.schema.json
.venv/bin/python -m qual_lab.main emit-contract-schema --kind synthesis-export-record > contracts/synthesis_export_record.schema.json
```

Contract rules:

- keep example fixtures synthetic
- keep contract names stable once external tooling depends on them
- do not encode study-specific unpublished details in shared contract files
