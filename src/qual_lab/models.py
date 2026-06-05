from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SensitivityLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    REGULATED = "regulated"

    @property
    def rank(self) -> int:
        return _SENSITIVITY_RANKS[self]


_SENSITIVITY_RANKS: dict[SensitivityLevel, int] = {
    SensitivityLevel.PUBLIC: 0,
    SensitivityLevel.INTERNAL: 1,
    SensitivityLevel.RESTRICTED: 2,
    SensitivityLevel.REGULATED: 3,
}


class AnalysisMode(str, Enum):
    CODEBOOK_THEMATIC = "codebook_thematic"
    FRAMEWORK = "framework_analysis"
    RAPID = "rapid_qualitative_summary"
    MIXED_METHODS = "mixed_methods"


class DataModality(str, Enum):
    TRANSCRIPT = "transcript"
    OBSERVER_NOTES = "observer_notes"
    QUESTIONNAIRE = "questionnaire"
    AUDIO = "audio"
    MEMO = "memo"
    CODED_EXCERPT = "coded_excerpt"


class DocumentCategory(str, Enum):
    PROTOCOL = "protocol"
    CONSENT = "consent"
    INSTRUMENT = "instrument"
    RUNBOOK = "runbook"
    DATA_USE_AGREEMENT = "data_use_agreement"


class DocumentStatus(str, Enum):
    CANONICAL = "canonical"
    DRAFT = "draft"
    ARCHIVED = "archived"


class StudyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ExternalModelAction(str, Enum):
    DISABLED = "disabled"
    DEIDENTIFIED_ONLY = "deidentified_only"
    APPROVED_EXCEPTION = "approved_exception"


class AuditResult(str, Enum):
    SUCCESS = "success"
    BLOCKED = "blocked"
    ERROR = "error"


class StorageScheme(str, Enum):
    SECURE_URI = "secure_uri"
    LOCAL_ENCRYPTED = "local_encrypted"
    EXTERNAL_OBJECT_STORE = "external_object_store"
    SYNTHETIC = "synthetic"


class DeidentificationState(str, Enum):
    NOT_STARTED = "not_started"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    CHANGES_REQUIRED = "changes_required"


class ReviewOutcome(str, Enum):
    APPROVED = "approved"
    CHANGES_REQUIRED = "changes_required"
    REJECTED = "rejected"


class ApprovedUse(str, Enum):
    INTERNAL_ANALYSIS = "internal_analysis"
    TEAM_CODING = "team_coding"
    DEIDENTIFIED_EXPORT = "deidentified_export"
    EXTERNAL_MODEL_PROCESSING = "external_model_processing"


class GateStatus(str, Enum):
    BLOCKED = "blocked"
    ACCEPTED_FOR_REVIEW = "accepted_for_review"
    READY_FOR_ANALYSIS = "ready_for_analysis"


class CodebookStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class AnalysisUnitKind(str, Enum):
    SEGMENT = "segment"
    EXCERPT = "excerpt"
    NOTE_SPAN = "note_span"
    RESPONSE_ITEM = "response_item"


class MemoKind(str, Enum):
    ANALYTIC = "analytic"
    REFLEXIVE = "reflexive"
    METHODOLOGICAL = "methodological"
    ADJUDICATION = "adjudication"


class IntegrationRelationship(str, Enum):
    CONVERGENCE = "convergence"
    COMPLEMENTARITY = "complementarity"
    DIVERGENCE = "divergence"
    EXPANSION = "expansion"


class TeamWorkflowStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    ARCHIVED = "archived"


class AdjudicationOutcome(str, Enum):
    CONFIRMED_PRIMARY = "confirmed_primary"
    CONFIRMED_SECONDARY = "confirmed_secondary"
    MERGED_RESOLUTION = "merged_resolution"
    ESCALATE_FOR_REVIEW = "escalate_for_review"
    NO_CONSENSUS = "no_consensus"


class AssistiveAlgorithmRuntime(str, Enum):
    LOCAL_RULE_BASED = "local_rule_based"
    LOCAL_STATISTICAL = "local_statistical"
    EXTERNAL_MODEL = "external_model"


class AssistivePolicyDecision(str, Enum):
    BLOCKED = "blocked"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    APPROVED = "approved"


class SynthesisExportKind(str, Enum):
    THEMATIC_SUMMARY = "thematic_summary"
    FRAMEWORK_MATRIX_REPORT = "framework_matrix_report"
    MIXED_METHOD_BRIEF = "mixed_method_brief"
    ADJUDICATION_SUMMARY = "adjudication_summary"


class CanonicalDocumentRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_id: str = Field(min_length=1)
    category: DocumentCategory
    version: str = Field(min_length=1)
    status: DocumentStatus = DocumentStatus.CANONICAL
    location: str = Field(min_length=1)
    checksum_sha256: str | None = None


class AccessRole(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_name: str = Field(min_length=1)
    privileges: list[str] = Field(min_length=1)
    may_access_identifiable: bool = False
    may_export_deidentified: bool = False


class RetentionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identifiable_data: str = Field(min_length=1)
    deidentified_data: str = Field(min_length=1)
    raw_media: str = Field(min_length=1)
    audit_log: str = Field(min_length=1)
    code_key: str = Field(min_length=1)


class ExternalModelPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_action: ExternalModelAction = ExternalModelAction.DISABLED
    requires_human_review: bool = True
    requires_deidentification: bool = True
    allowed_providers: list[str] = Field(default_factory=list)
    allowed_model_classes: list[str] = Field(default_factory=list)


class StudyManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest_version: str = "1.0"
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    display_name: str = Field(min_length=1)
    status: StudyStatus = StudyStatus.DRAFT
    data_sensitivity: SensitivityLevel
    modalities: list[DataModality] = Field(min_length=1)
    analysis_modes: list[AnalysisMode] = Field(min_length=1)
    canonical_documents: list[CanonicalDocumentRef] = Field(min_length=1)
    access_roles: list[AccessRole] = Field(min_length=1)
    retention: RetentionPolicy
    external_model_policy: ExternalModelPolicy = Field(default_factory=ExternalModelPolicy)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_sensitive_external_model_policy(self) -> StudyManifest:
        if self.data_sensitivity in {SensitivityLevel.RESTRICTED, SensitivityLevel.REGULATED}:
            if (
                self.external_model_policy.default_action == ExternalModelAction.APPROVED_EXCEPTION
                and not self.external_model_policy.requires_deidentification
            ):
                raise ValueError(
                    "restricted or regulated manifests must require de-identification "
                    "before approved external model use"
                )
        return self


class AuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_version: str = "1.0"
    timestamp: datetime
    actor_role: str = Field(min_length=1)
    action: str = Field(min_length=1)
    target_type: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    sensitivity: SensitivityLevel
    result: AuditResult
    details: str | None = None


class StorageLocator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    storage_scheme: StorageScheme
    locator: str = Field(min_length=1)
    checksum_sha256: str | None = None

    @model_validator(mode="after")
    def validate_locator_shape(self) -> StorageLocator:
        if self.storage_scheme in {
            StorageScheme.SECURE_URI,
            StorageScheme.EXTERNAL_OBJECT_STORE,
            StorageScheme.SYNTHETIC,
        } and "://" not in self.locator:
            raise ValueError(
                "non-local storage locators must use an explicit URI-like scheme such as "
                "`secure://`"
            )
        return self


class ProtectedIntakeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intake_version: str = "1.0"
    artifact_id: str = Field(min_length=1)
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    artifact_label: str = Field(min_length=1)
    received_at: datetime
    modality: DataModality
    sensitivity: SensitivityLevel
    submitted_by_role: str = Field(min_length=1)
    source: StorageLocator
    contains_direct_identifiers: bool = True
    contains_quasi_identifiers: bool = True
    contains_raw_media: bool = False
    code_key_linked: bool = False
    deidentification_state: DeidentificationState = DeidentificationState.NOT_STARTED
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_public_intake_fields(self) -> ProtectedIntakeRecord:
        if self.sensitivity == SensitivityLevel.PUBLIC and self.contains_direct_identifiers:
            raise ValueError("public intake records may not declare direct identifiers")
        if self.sensitivity == SensitivityLevel.PUBLIC and self.code_key_linked:
            raise ValueError("public intake records may not declare a linked code key")
        return self


class DeidentificationReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_version: str = "1.0"
    review_id: str = Field(min_length=1)
    artifact_id: str = Field(min_length=1)
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    reviewed_at: datetime
    reviewer_role: str = Field(min_length=1)
    outcome: ReviewOutcome
    direct_identifier_findings: list[str] = Field(default_factory=list)
    quasi_identifier_findings: list[str] = Field(default_factory=list)
    unresolved_risks: list[str] = Field(default_factory=list)
    transformations_applied: list[str] = Field(default_factory=list)
    approved_uses: list[ApprovedUse] = Field(default_factory=list)
    deidentified_locator: StorageLocator | None = None
    residual_sensitivity: SensitivityLevel = SensitivityLevel.RESTRICTED
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_review_outcome(self) -> DeidentificationReview:
        if self.outcome == ReviewOutcome.APPROVED:
            if self.deidentified_locator is None:
                raise ValueError("approved reviews must provide a deidentified locator")
            if not self.approved_uses:
                raise ValueError("approved reviews must declare at least one approved use")
            if self.unresolved_risks:
                raise ValueError("approved reviews may not carry unresolved risks")
            if not self.transformations_applied:
                raise ValueError("approved reviews must list the applied transformations")
            if self.residual_sensitivity == SensitivityLevel.REGULATED:
                raise ValueError(
                    "approved de-identified artifacts may not keep a regulated sensitivity level"
                )
        else:
            if self.approved_uses:
                raise ValueError("only approved reviews may declare approved uses")
            if self.deidentified_locator is not None:
                raise ValueError("only approved reviews may declare a deidentified locator")
        return self


class IntakeGateReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_version: str = "1.0"
    assessed_at: datetime
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    artifact_id: str = Field(min_length=1)
    modality: DataModality
    status: GateStatus
    analysis_ready: bool = False
    review_id: str | None = None
    approved_uses: list[ApprovedUse] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    recommended_audit_action: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_gate_consistency(self) -> IntakeGateReport:
        if self.analysis_ready and self.status != GateStatus.READY_FOR_ANALYSIS:
            raise ValueError("analysis-ready reports must use the ready_for_analysis status")
        if self.status == GateStatus.READY_FOR_ANALYSIS and not self.analysis_ready:
            raise ValueError("ready_for_analysis reports must set analysis_ready=true")
        if self.status != GateStatus.READY_FOR_ANALYSIS and self.approved_uses:
            raise ValueError("approved uses may only be emitted for ready_for_analysis reports")
        if self.analysis_ready and self.blockers:
            raise ValueError("analysis-ready reports may not carry blockers")
        return self


class WorkspaceSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    review_id: str = Field(min_length=1)
    modality: DataModality
    gate_status: GateStatus = GateStatus.READY_FOR_ANALYSIS
    approved_uses: list[ApprovedUse] = Field(min_length=1)
    source_locator: StorageLocator
    residual_sensitivity: SensitivityLevel

    @model_validator(mode="after")
    def validate_workspace_source(self) -> WorkspaceSource:
        if self.gate_status != GateStatus.READY_FOR_ANALYSIS:
            raise ValueError(
                "workspace sources must originate from ready_for_analysis gate reports"
            )
        if not any(
            approved_use in self.approved_uses
            for approved_use in {ApprovedUse.INTERNAL_ANALYSIS, ApprovedUse.TEAM_CODING}
        ):
            raise ValueError(
                "workspace sources must allow internal analysis or team coding before use"
            )
        return self


class AnalysisWorkspace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_version: str = "1.0"
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    created_at: datetime
    created_by_role: str = Field(min_length=1)
    workspace_locator: StorageLocator
    allowed_analysis_modes: list[AnalysisMode] = Field(min_length=1)
    allowed_approved_uses: list[ApprovedUse] = Field(min_length=1)
    source_artifacts: list[WorkspaceSource] = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_workspace_context(self) -> AnalysisWorkspace:
        source_ids = [source.artifact_id for source in self.source_artifacts]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("workspace source artifacts must be unique")
        if not any(
            approved_use in self.allowed_approved_uses
            for approved_use in {ApprovedUse.INTERNAL_ANALYSIS, ApprovedUse.TEAM_CODING}
        ):
            raise ValueError(
                "analysis workspaces must allow internal analysis or team coding"
            )
        return self


class AnalysisUnit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unit_version: str = "1.0"
    unit_id: str = Field(min_length=1)
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    source_artifact_id: str = Field(min_length=1)
    modality: DataModality
    unit_kind: AnalysisUnitKind
    content: str = Field(min_length=1)
    speaker_label: str | None = None
    start_offset: int | None = Field(default=None, ge=0)
    end_offset: int | None = Field(default=None, ge=0)
    tags: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_offsets(self) -> AnalysisUnit:
        if self.end_offset is not None and self.start_offset is None:
            raise ValueError("end_offset requires start_offset")
        if (
            self.start_offset is not None
            and self.end_offset is not None
            and self.end_offset <= self.start_offset
        ):
            raise ValueError("end_offset must be greater than start_offset")
        return self


class CodeDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    definition: str = Field(min_length=1)
    parent_code_id: str | None = None
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    exemplar_unit_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_parent_reference(self) -> CodeDefinition:
        if self.parent_code_id == self.code_id:
            raise ValueError("a code may not be its own parent")
        return self


class CodebookVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codebook_version: str = "1.0"
    codebook_id: str = Field(min_length=1)
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    version_label: str = Field(min_length=1)
    created_at: datetime
    created_by_role: str = Field(min_length=1)
    status: CodebookStatus = CodebookStatus.DRAFT
    codes: list[CodeDefinition] = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_codes(self) -> CodebookVersion:
        code_ids = [code.code_id for code in self.codes]
        if len(code_ids) != len(set(code_ids)):
            raise ValueError("code definitions must use unique code_id values")
        code_id_set = set(code_ids)
        for code in self.codes:
            if code.parent_code_id is not None and code.parent_code_id not in code_id_set:
                raise ValueError("parent_code_id must reference another code in the same version")
        return self


class CodeApplication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    application_version: str = "1.0"
    application_id: str = Field(min_length=1)
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    unit_id: str = Field(min_length=1)
    codebook_id: str = Field(min_length=1)
    code_id: str = Field(min_length=1)
    coder_role: str = Field(min_length=1)
    applied_at: datetime
    notes: list[str] = Field(default_factory=list)


class MemoRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memo_version: str = "1.0"
    memo_id: str = Field(min_length=1)
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    memo_kind: MemoKind
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    author_role: str = Field(min_length=1)
    created_at: datetime
    linked_unit_ids: list[str] = Field(default_factory=list)
    linked_code_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_linked_ids(self) -> MemoRecord:
        if len(self.linked_unit_ids) != len(set(self.linked_unit_ids)):
            raise ValueError("linked_unit_ids must be unique")
        if len(self.linked_code_ids) != len(set(self.linked_code_ids)):
            raise ValueError("linked_code_ids must be unique")
        return self


class QualitativeEvidenceAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    linked_unit_ids: list[str] = Field(default_factory=list)
    linked_code_ids: list[str] = Field(default_factory=list)
    linked_memo_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_anchor_links(self) -> QualitativeEvidenceAnchor:
        if not any((self.linked_unit_ids, self.linked_code_ids, self.linked_memo_ids)):
            raise ValueError(
                "qualitative evidence anchors must reference at least one unit, code, or memo"
            )
        if len(self.linked_unit_ids) != len(set(self.linked_unit_ids)):
            raise ValueError("linked_unit_ids must be unique")
        if len(self.linked_code_ids) != len(set(self.linked_code_ids)):
            raise ValueError("linked_code_ids must be unique")
        if len(self.linked_memo_ids) != len(set(self.linked_memo_ids)):
            raise ValueError("linked_memo_ids must be unique")
        return self


class FrameworkMatrixDimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    label: str = Field(min_length=1)
    definition: str = Field(min_length=1)
    prompts: list[str] = Field(default_factory=list)


class FrameworkMatrixCell(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    summary: str = Field(min_length=1)
    evidence: QualitativeEvidenceAnchor
    notes: list[str] = Field(default_factory=list)


class FrameworkMatrixRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    row_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    row_label: str = Field(min_length=1)
    cells: list[FrameworkMatrixCell] = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_cells(self) -> FrameworkMatrixRow:
        dimension_ids = [cell.dimension_id for cell in self.cells]
        if len(dimension_ids) != len(set(dimension_ids)):
            raise ValueError("framework matrix rows must use unique dimension_id values")
        return self


class FrameworkMatrix(BaseModel):
    model_config = ConfigDict(extra="forbid")

    matrix_version: str = "1.0"
    matrix_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    framework_label: str = Field(min_length=1)
    row_basis: str = Field(min_length=1)
    created_at: datetime
    created_by_role: str = Field(min_length=1)
    dimensions: list[FrameworkMatrixDimension] = Field(min_length=1)
    rows: list[FrameworkMatrixRow] = Field(min_length=1)
    linked_codebook_ids: list[str] = Field(default_factory=list)
    linked_memo_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_matrix(self) -> FrameworkMatrix:
        dimension_ids = [dimension.dimension_id for dimension in self.dimensions]
        if len(dimension_ids) != len(set(dimension_ids)):
            raise ValueError("framework matrices must use unique dimension_id values")

        row_ids = [row.row_id for row in self.rows]
        if len(row_ids) != len(set(row_ids)):
            raise ValueError("framework matrices must use unique row_id values")

        if len(self.linked_codebook_ids) != len(set(self.linked_codebook_ids)):
            raise ValueError("linked_codebook_ids must be unique")
        if len(self.linked_memo_ids) != len(set(self.linked_memo_ids)):
            raise ValueError("linked_memo_ids must be unique")

        dimension_id_set = set(dimension_ids)
        for row in self.rows:
            for cell in row.cells:
                if cell.dimension_id not in dimension_id_set:
                    raise ValueError(
                        "framework matrix cells must reference declared dimensions"
                    )
        return self


class QuantitativeFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    source_label: str = Field(min_length=1)
    measure_label: str = Field(min_length=1)
    subgroup_label: str | None = Field(default=None, min_length=1)
    numeric_value: float | None = None
    text_value: str | None = Field(default=None, min_length=1)
    unit: str | None = Field(default=None, min_length=1)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_value(self) -> QuantitativeFinding:
        if self.numeric_value is None and self.text_value is None:
            raise ValueError(
                "quantitative findings must provide either numeric_value or text_value"
            )
        return self


class MixedMethodJoinRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    row_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    row_label: str = Field(min_length=1)
    qualitative_summary: str = Field(min_length=1)
    qualitative_evidence: QualitativeEvidenceAnchor
    quantitative_finding_ids: list[str] = Field(min_length=1)
    relationship: IntegrationRelationship
    integrated_interpretation: str = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_quantitative_finding_ids(self) -> MixedMethodJoinRow:
        if len(self.quantitative_finding_ids) != len(set(self.quantitative_finding_ids)):
            raise ValueError("quantitative_finding_ids must be unique")
        return self


class MixedMethodJoin(BaseModel):
    model_config = ConfigDict(extra="forbid")

    join_version: str = "1.0"
    join_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    title: str = Field(min_length=1)
    join_strategy: str = Field(min_length=1)
    created_at: datetime
    created_by_role: str = Field(min_length=1)
    framework_matrix_ids: list[str] = Field(default_factory=list)
    codebook_ids: list[str] = Field(default_factory=list)
    quantitative_findings: list[QuantitativeFinding] = Field(min_length=1)
    rows: list[MixedMethodJoinRow] = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_join(self) -> MixedMethodJoin:
        if len(self.framework_matrix_ids) != len(set(self.framework_matrix_ids)):
            raise ValueError("framework_matrix_ids must be unique")
        if len(self.codebook_ids) != len(set(self.codebook_ids)):
            raise ValueError("codebook_ids must be unique")

        finding_ids = [finding.finding_id for finding in self.quantitative_findings]
        if len(finding_ids) != len(set(finding_ids)):
            raise ValueError("mixed-method joins must use unique finding_id values")

        row_ids = [row.row_id for row in self.rows]
        if len(row_ids) != len(set(row_ids)):
            raise ValueError("mixed-method joins must use unique row_id values")

        finding_id_set = set(finding_ids)
        for row in self.rows:
            for finding_id in row.quantitative_finding_ids:
                if finding_id not in finding_id_set:
                    raise ValueError(
                        "mixed-method join rows must reference declared quantitative findings"
                    )
        return self


class TeamCodingAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assignment_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    unit_id: str = Field(min_length=1)
    primary_coder_role: str = Field(min_length=1)
    secondary_coder_role: str | None = Field(default=None, min_length=1)
    focus_code_ids: list[str] = Field(default_factory=list)
    linked_memo_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_assignment(self) -> TeamCodingAssignment:
        if (
            self.secondary_coder_role is not None
            and self.secondary_coder_role == self.primary_coder_role
        ):
            raise ValueError("secondary_coder_role must differ from primary_coder_role")
        if len(self.focus_code_ids) != len(set(self.focus_code_ids)):
            raise ValueError("focus_code_ids must be unique")
        if len(self.linked_memo_ids) != len(set(self.linked_memo_ids)):
            raise ValueError("linked_memo_ids must be unique")
        return self


class TeamCodingRound(BaseModel):
    model_config = ConfigDict(extra="forbid")

    round_version: str = "1.0"
    round_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    created_at: datetime
    created_by_role: str = Field(min_length=1)
    facilitator_role: str = Field(min_length=1)
    coder_roles: list[str] = Field(min_length=2)
    adjudicator_role: str | None = Field(default=None, min_length=1)
    status: TeamWorkflowStatus = TeamWorkflowStatus.PLANNED
    linked_codebook_ids: list[str] = Field(min_length=1)
    linked_framework_matrix_ids: list[str] = Field(default_factory=list)
    linked_mixed_method_join_ids: list[str] = Field(default_factory=list)
    assignments: list[TeamCodingAssignment] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_round(self) -> TeamCodingRound:
        if len(self.coder_roles) != len(set(self.coder_roles)):
            raise ValueError("coder_roles must be unique")
        if len(self.linked_codebook_ids) != len(set(self.linked_codebook_ids)):
            raise ValueError("linked_codebook_ids must be unique")
        if len(self.linked_framework_matrix_ids) != len(set(self.linked_framework_matrix_ids)):
            raise ValueError("linked_framework_matrix_ids must be unique")
        if len(self.linked_mixed_method_join_ids) != len(
            set(self.linked_mixed_method_join_ids)
        ):
            raise ValueError("linked_mixed_method_join_ids must be unique")

        assignment_ids = [assignment.assignment_id for assignment in self.assignments]
        if len(assignment_ids) != len(set(assignment_ids)):
            raise ValueError("team coding rounds must use unique assignment_id values")

        unit_ids = [assignment.unit_id for assignment in self.assignments]
        if len(unit_ids) != len(set(unit_ids)):
            raise ValueError("team coding rounds may not assign the same unit twice")

        coder_role_set = set(self.coder_roles)
        requires_adjudicator = False
        for assignment in self.assignments:
            if assignment.primary_coder_role not in coder_role_set:
                raise ValueError(
                    "team coding assignments must use primary_coder_role values "
                    "declared in coder_roles"
                )
            if (
                assignment.secondary_coder_role is not None
                and assignment.secondary_coder_role not in coder_role_set
            ):
                raise ValueError(
                    "team coding assignments must use secondary_coder_role values "
                    "declared in coder_roles"
                )
            if assignment.secondary_coder_role is not None:
                requires_adjudicator = True

        if requires_adjudicator and self.adjudicator_role is None:
            raise ValueError(
                "team coding rounds with secondary_coder_role assignments must declare "
                "an adjudicator_role"
            )
        return self


class AdjudicationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adjudication_version: str = "1.0"
    decision_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    round_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    decided_at: datetime
    adjudicator_role: str = Field(min_length=1)
    unit_id: str = Field(min_length=1)
    compared_application_ids: list[str] = Field(min_length=2)
    outcome: AdjudicationOutcome
    selected_application_id: str | None = None
    retained_code_ids: list[str] = Field(default_factory=list)
    linked_memo_ids: list[str] = Field(default_factory=list)
    linked_framework_matrix_ids: list[str] = Field(default_factory=list)
    linked_mixed_method_join_ids: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    follow_up_actions: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_decision(self) -> AdjudicationDecision:
        if len(self.compared_application_ids) != len(set(self.compared_application_ids)):
            raise ValueError("compared_application_ids must be unique")
        if len(self.retained_code_ids) != len(set(self.retained_code_ids)):
            raise ValueError("retained_code_ids must be unique")
        if len(self.linked_memo_ids) != len(set(self.linked_memo_ids)):
            raise ValueError("linked_memo_ids must be unique")
        if len(self.linked_framework_matrix_ids) != len(set(self.linked_framework_matrix_ids)):
            raise ValueError("linked_framework_matrix_ids must be unique")
        if len(self.linked_mixed_method_join_ids) != len(
            set(self.linked_mixed_method_join_ids)
        ):
            raise ValueError("linked_mixed_method_join_ids must be unique")
        if len(self.follow_up_actions) != len(set(self.follow_up_actions)):
            raise ValueError("follow_up_actions must be unique")

        if self.outcome in {
            AdjudicationOutcome.CONFIRMED_PRIMARY,
            AdjudicationOutcome.CONFIRMED_SECONDARY,
        }:
            if self.selected_application_id is None:
                raise ValueError(
                    "confirmed adjudication outcomes must declare a selected_application_id"
                )
            if self.selected_application_id not in self.compared_application_ids:
                raise ValueError(
                    "selected_application_id must reference one of the compared applications"
                )

        if self.outcome == AdjudicationOutcome.MERGED_RESOLUTION:
            if self.selected_application_id is not None:
                raise ValueError(
                    "merged adjudication outcomes may not declare a selected_application_id"
                )
            if not self.retained_code_ids:
                raise ValueError(
                    "merged adjudication outcomes must declare retained_code_ids"
                )

        if self.outcome in {
            AdjudicationOutcome.ESCALATE_FOR_REVIEW,
            AdjudicationOutcome.NO_CONSENSUS,
        }:
            if self.selected_application_id is not None:
                raise ValueError(
                    "non-final adjudication outcomes may not declare a selected_application_id"
                )
            if not self.follow_up_actions:
                raise ValueError(
                    "non-final adjudication outcomes must declare follow_up_actions"
                )

        return self


class AssistiveAlgorithmPolicyGate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate_version: str = "1.0"
    gate_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    requested_at: datetime
    requested_by_role: str = Field(min_length=1)
    algorithm_label: str = Field(min_length=1)
    algorithm_runtime: AssistiveAlgorithmRuntime
    purpose: str = Field(min_length=1)
    proposed_uses: list[ApprovedUse] = Field(min_length=1)
    input_locator: StorageLocator
    output_locator: StorageLocator | None = None
    requires_human_review: bool = True
    requires_deidentification: bool = True
    decision: AssistivePolicyDecision
    decision_rationale: str = Field(min_length=1)
    decision_by_role: str | None = Field(default=None, min_length=1)
    decided_at: datetime | None = None
    required_controls: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_gate(self) -> AssistiveAlgorithmPolicyGate:
        if len(self.proposed_uses) != len(set(self.proposed_uses)):
            raise ValueError("proposed_uses must be unique")
        if len(self.required_controls) != len(set(self.required_controls)):
            raise ValueError("required_controls must be unique")

        uses_external_model = ApprovedUse.EXTERNAL_MODEL_PROCESSING in self.proposed_uses
        if (
            self.algorithm_runtime == AssistiveAlgorithmRuntime.EXTERNAL_MODEL
            and not uses_external_model
        ):
            raise ValueError(
                "algorithm_runtime=external_model requires external_model_processing "
                "in proposed_uses"
            )
        if (
            uses_external_model
            and self.algorithm_runtime != AssistiveAlgorithmRuntime.EXTERNAL_MODEL
        ):
            raise ValueError(
                "external model processing proposed_uses require algorithm_runtime=external_model"
            )
        if uses_external_model and not self.requires_deidentification:
            raise ValueError(
                "assistive gates with external model processing must require de-identification"
            )

        if self.requires_human_review and (
            self.decision_by_role is None or self.decided_at is None
        ):
            raise ValueError(
                "assistive gates requiring human review must declare "
                "decision_by_role and decided_at"
            )
        if (self.decision_by_role is None) != (self.decided_at is None):
            raise ValueError("decision_by_role and decided_at must be set together")

        if self.decision == AssistivePolicyDecision.BLOCKED:
            if self.output_locator is not None:
                raise ValueError("blocked assistive gates may not declare output_locator")
        elif self.output_locator is None:
            raise ValueError("approved assistive gates must declare output_locator")
        return self


class SynthesisExportRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_version: str = "1.0"
    export_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    workspace_id: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    study_slug: str = Field(pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
    created_at: datetime
    created_by_role: str = Field(min_length=1)
    export_kind: SynthesisExportKind
    source_codebook_ids: list[str] = Field(default_factory=list)
    source_framework_matrix_ids: list[str] = Field(default_factory=list)
    source_mixed_method_join_ids: list[str] = Field(default_factory=list)
    source_team_coding_round_ids: list[str] = Field(default_factory=list)
    source_adjudication_decision_ids: list[str] = Field(default_factory=list)
    source_memo_ids: list[str] = Field(default_factory=list)
    included_approved_uses: list[ApprovedUse] = Field(min_length=1)
    sensitivity: SensitivityLevel
    export_locator: StorageLocator
    assistive_algorithm_gate_id: str | None = None
    assistive_algorithms_applied: list[str] = Field(default_factory=list)
    audit_event_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_export(self) -> SynthesisExportRecord:
        source_lists = (
            self.source_codebook_ids,
            self.source_framework_matrix_ids,
            self.source_mixed_method_join_ids,
            self.source_team_coding_round_ids,
            self.source_adjudication_decision_ids,
            self.source_memo_ids,
        )
        if not any(source_lists):
            raise ValueError("synthesis exports must reference at least one source artifact")
        for source_list_name, source_list in (
            ("source_codebook_ids", self.source_codebook_ids),
            ("source_framework_matrix_ids", self.source_framework_matrix_ids),
            ("source_mixed_method_join_ids", self.source_mixed_method_join_ids),
            ("source_team_coding_round_ids", self.source_team_coding_round_ids),
            ("source_adjudication_decision_ids", self.source_adjudication_decision_ids),
            ("source_memo_ids", self.source_memo_ids),
        ):
            if len(source_list) != len(set(source_list)):
                raise ValueError(f"{source_list_name} must be unique")

        if len(self.included_approved_uses) != len(set(self.included_approved_uses)):
            raise ValueError("included_approved_uses must be unique")
        if len(self.assistive_algorithms_applied) != len(set(self.assistive_algorithms_applied)):
            raise ValueError("assistive_algorithms_applied must be unique")
        if len(self.audit_event_ids) != len(set(self.audit_event_ids)):
            raise ValueError("audit_event_ids must be unique")

        if self.assistive_algorithms_applied and self.assistive_algorithm_gate_id is None:
            raise ValueError(
                "assistive_algorithms_applied requires an explicit assistive_algorithm_gate_id"
            )
        if (
            self.assistive_algorithm_gate_id is not None
            and not self.assistive_algorithms_applied
        ):
            raise ValueError(
                "assistive_algorithm_gate_id requires at least one assistive algorithm label"
            )
        if (
            ApprovedUse.EXTERNAL_MODEL_PROCESSING in self.included_approved_uses
            and self.assistive_algorithm_gate_id is None
        ):
            raise ValueError(
                "external model synthesis exports require an explicit assistive policy gate"
            )
        if (
            self.sensitivity == SensitivityLevel.REGULATED
            and ApprovedUse.DEIDENTIFIED_EXPORT in self.included_approved_uses
        ):
            raise ValueError(
                "de-identified synthesis exports may not keep a regulated sensitivity level"
            )
        return self


def default_study_manifest() -> StudyManifest:
    return StudyManifest(
        study_slug="demo-sensitive-study",
        display_name="Demo Sensitive Study",
        status=StudyStatus.ACTIVE,
        data_sensitivity=SensitivityLevel.REGULATED,
        modalities=[
            DataModality.TRANSCRIPT,
            DataModality.OBSERVER_NOTES,
            DataModality.QUESTIONNAIRE,
            DataModality.MEMO,
        ],
        analysis_modes=[
            AnalysisMode.CODEBOOK_THEMATIC,
            AnalysisMode.FRAMEWORK,
            AnalysisMode.MIXED_METHODS,
        ],
        canonical_documents=[
            CanonicalDocumentRef(
                doc_id="protocol-v1",
                category=DocumentCategory.PROTOCOL,
                version="1.0",
                location="secure://docs/protocol-v1.pdf",
            ),
            CanonicalDocumentRef(
                doc_id="consent-v1",
                category=DocumentCategory.CONSENT,
                version="1.0",
                location="secure://docs/consent-v1.pdf",
            ),
        ],
        access_roles=[
            AccessRole(
                role_name="study_steward",
                privileges=[
                    "manage_manifest",
                    "review_exports",
                    "approve_policy_exceptions",
                ],
                may_access_identifiable=True,
                may_export_deidentified=True,
            ),
            AccessRole(
                role_name="analyst",
                privileges=[
                    "initialize_workspace",
                    "code_deidentified_excerpt",
                    "write_memo",
                    "build_framework_matrix",
                    "build_joint_display",
                    "participate_team_coding",
                ],
                may_export_deidentified=True,
            ),
            AccessRole(
                role_name="senior_analyst",
                privileges=[
                    "initialize_workspace",
                    "code_deidentified_excerpt",
                    "write_memo",
                    "build_framework_matrix",
                    "build_joint_display",
                    "coordinate_team_coding",
                    "adjudicate_coding_conflicts",
                ],
                may_export_deidentified=True,
            ),
        ],
        retention=RetentionPolicy(
            identifiable_data="Retain outside the repository per study governance.",
            deidentified_data=(
                "Retain according to study policy and downstream publication posture."
            ),
            raw_media="Keep outside the repository and destroy per study policy.",
            audit_log="Retain with generated exports and governance records.",
            code_key="Store separately from analysis artifacts and remove when policy allows.",
        ),
        external_model_policy=ExternalModelPolicy(),
        notes=[
            "Synthetic fixture only.",
            (
                "Replace secure document references with real canonical locations "
                "outside the repository."
            ),
        ],
    )


def default_audit_event() -> AuditEvent:
    return AuditEvent(
        timestamp=datetime.fromisoformat("2026-03-24T10:00:00+00:00"),
        actor_role="study_steward",
        action="validated_study_manifest",
        target_type="study_manifest",
        target_id="demo-sensitive-study",
        sensitivity=SensitivityLevel.REGULATED,
        result=AuditResult.SUCCESS,
        details="Synthetic audit event used to validate the baseline contract.",
    )


def default_protected_intake_record() -> ProtectedIntakeRecord:
    return ProtectedIntakeRecord(
        artifact_id="session-001-transcript",
        study_slug="demo-sensitive-study",
        artifact_label="Synthetic Session 001 Transcript",
        received_at=datetime.fromisoformat("2026-03-24T10:15:00+00:00"),
        modality=DataModality.TRANSCRIPT,
        sensitivity=SensitivityLevel.REGULATED,
        submitted_by_role="study_steward",
        source=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://intake/session-001/transcript.json",
        ),
        contains_direct_identifiers=True,
        contains_quasi_identifiers=True,
        contains_raw_media=False,
        code_key_linked=False,
        deidentification_state=DeidentificationState.IN_REVIEW,
        notes=[
            "Synthetic fixture only.",
            "Represents an intake artifact staged outside the repository boundary.",
        ],
    )


def default_deidentification_review() -> DeidentificationReview:
    return DeidentificationReview(
        review_id="review-session-001-transcript-v1",
        artifact_id="session-001-transcript",
        study_slug="demo-sensitive-study",
        reviewed_at=datetime.fromisoformat("2026-03-24T11:00:00+00:00"),
        reviewer_role="study_steward",
        outcome=ReviewOutcome.APPROVED,
        direct_identifier_findings=[
            "Personal names replaced with participant labels.",
        ],
        quasi_identifier_findings=[
            "Rare contextual details generalized for downstream coding.",
        ],
        unresolved_risks=[],
        transformations_applied=[
            "Removed direct identifiers from utterance text.",
            "Generalized rare contextual references.",
        ],
        approved_uses=[
            ApprovedUse.INTERNAL_ANALYSIS,
            ApprovedUse.TEAM_CODING,
        ],
        deidentified_locator=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://deidentified/session-001/transcript.json",
        ),
        residual_sensitivity=SensitivityLevel.RESTRICTED,
        notes=[
            "Synthetic fixture only.",
            "Approved for downstream de-identified coding work.",
        ],
    )


def default_intake_gate_report() -> IntakeGateReport:
    return IntakeGateReport(
        assessed_at=datetime.fromisoformat("2026-03-24T11:05:00+00:00"),
        study_slug="demo-sensitive-study",
        artifact_id="session-001-transcript",
        modality=DataModality.TRANSCRIPT,
        status=GateStatus.READY_FOR_ANALYSIS,
        analysis_ready=True,
        review_id="review-session-001-transcript-v1",
        approved_uses=[
            ApprovedUse.INTERNAL_ANALYSIS,
            ApprovedUse.TEAM_CODING,
        ],
        blockers=[],
        warnings=[],
        required_actions=[],
        recommended_audit_action="record_deidentification_approval",
    )


def default_analysis_workspace() -> AnalysisWorkspace:
    return AnalysisWorkspace(
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        created_at=datetime.fromisoformat("2026-03-24T11:15:00+00:00"),
        created_by_role="analyst",
        workspace_locator=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://workspace/demo-sensitive-study/coding",
        ),
        allowed_analysis_modes=[
            AnalysisMode.CODEBOOK_THEMATIC,
            AnalysisMode.FRAMEWORK,
            AnalysisMode.MIXED_METHODS,
        ],
        allowed_approved_uses=[
            ApprovedUse.INTERNAL_ANALYSIS,
            ApprovedUse.TEAM_CODING,
        ],
        source_artifacts=[
            WorkspaceSource(
                artifact_id="session-001-transcript",
                review_id="review-session-001-transcript-v1",
                modality=DataModality.TRANSCRIPT,
                approved_uses=[
                    ApprovedUse.INTERNAL_ANALYSIS,
                    ApprovedUse.TEAM_CODING,
                ],
                source_locator=StorageLocator(
                    storage_scheme=StorageScheme.SECURE_URI,
                    locator="secure://deidentified/session-001/transcript.json",
                ),
                residual_sensitivity=SensitivityLevel.RESTRICTED,
            ),
        ],
        notes=[
            "Synthetic fixture only.",
            "Represents a workspace opened from approved de-identified materials.",
            "Supports framework matrixing and mixed-method joins.",
        ],
    )


def default_analysis_unit() -> AnalysisUnit:
    return AnalysisUnit(
        unit_id="unit-session-001-001",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        source_artifact_id="session-001-transcript",
        modality=DataModality.TRANSCRIPT,
        unit_kind=AnalysisUnitKind.EXCERPT,
        content="Participant describes switching strategies after a confusing prompt.",
        speaker_label="participant",
        start_offset=0,
        end_offset=67,
        tags=["scenario-a", "interaction-breakdown"],
        notes=["Synthetic fixture only."],
    )


def default_codebook_version() -> CodebookVersion:
    return CodebookVersion(
        codebook_id="demo-sensitive-study-core",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        version_label="v1",
        created_at=datetime.fromisoformat("2026-03-24T11:20:00+00:00"),
        created_by_role="analyst",
        status=CodebookStatus.ACTIVE,
        codes=[
            CodeDefinition(
                code_id="usability_breakdown",
                label="Usability Breakdown",
                definition=(
                    "The participant reports confusion, friction, or failure in "
                    "the interaction."
                ),
                inclusion_criteria=[
                    "Mentions unclear prompts or navigation friction.",
                ],
                exclusion_criteria=[
                    "Pure preference statements without a breakdown.",
                ],
                exemplar_unit_ids=["unit-session-001-001"],
            ),
            CodeDefinition(
                code_id="strategy_shift",
                label="Strategy Shift",
                definition=(
                    "The participant changes approach in response to a difficulty "
                    "or adaptation need."
                ),
                inclusion_criteria=[
                    "Describes switching tactics or compensatory behavior.",
                ],
                exclusion_criteria=[
                    "Minor wording changes with no change in approach.",
                ],
                exemplar_unit_ids=["unit-session-001-001"],
            ),
        ],
        notes=[
            "Synthetic fixture only.",
            "Represents a small starter codebook for manual coding.",
        ],
    )


def default_code_application() -> CodeApplication:
    return CodeApplication(
        application_id="app-session-001-001-usability-breakdown",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        unit_id="unit-session-001-001",
        codebook_id="demo-sensitive-study-core",
        code_id="usability_breakdown",
        coder_role="analyst",
        applied_at=datetime.fromisoformat("2026-03-24T11:25:00+00:00"),
        notes=[
            "Synthetic fixture only.",
            "Applied during an initial manual coding pass.",
        ],
    )


def default_memo_record() -> MemoRecord:
    return MemoRecord(
        memo_id="memo-session-001-001",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        memo_kind=MemoKind.ANALYTIC,
        title="Breakdown prompts adaptive strategy use",
        body=(
            "The excerpt suggests that interaction breakdowns trigger compensatory strategy "
            "shifts rather than immediate abandonment."
        ),
        author_role="analyst",
        created_at=datetime.fromisoformat("2026-03-24T11:30:00+00:00"),
        linked_unit_ids=["unit-session-001-001"],
        linked_code_ids=["usability_breakdown", "strategy_shift"],
        notes=[
            "Synthetic fixture only.",
            "Links the initial excerpt to a higher-level analytic interpretation.",
        ],
    )


def default_framework_matrix() -> FrameworkMatrix:
    return FrameworkMatrix(
        matrix_id="demo-sensitive-study-framework-matrix",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        framework_label="Interaction Adaptation Matrix",
        row_basis="participant_case",
        created_at=datetime.fromisoformat("2026-03-24T11:40:00+00:00"),
        created_by_role="analyst",
        dimensions=[
            FrameworkMatrixDimension(
                dimension_id="interaction_breakdown",
                label="Interaction Breakdown",
                definition="How breakdowns, friction, or confusion appear in the case.",
                prompts=[
                    "What form does the breakdown take?",
                    "What makes the breakdown visible in the excerpt set?",
                ],
            ),
            FrameworkMatrixDimension(
                dimension_id="adaptation_response",
                label="Adaptation Response",
                definition="How the participant responds or compensates after friction appears.",
                prompts=[
                    "What recovery or adaptation strategy follows the breakdown?",
                    "How does the strategy affect continued task progress?",
                ],
            ),
        ],
        rows=[
            FrameworkMatrixRow(
                row_id="participant_01",
                row_label="Participant 01",
                cells=[
                    FrameworkMatrixCell(
                        dimension_id="interaction_breakdown",
                        summary=(
                            "The participant describes a confusing prompt sequence that "
                            "interrupts progress and forces a pause."
                        ),
                        evidence=QualitativeEvidenceAnchor(
                            linked_unit_ids=["unit-session-001-001"],
                            linked_code_ids=["usability_breakdown"],
                            linked_memo_ids=["memo-session-001-001"],
                        ),
                        notes=["Synthetic fixture only."],
                    ),
                    FrameworkMatrixCell(
                        dimension_id="adaptation_response",
                        summary=(
                            "Rather than abandon the task, the participant slows down, "
                            "seeks clarification, and switches tactics."
                        ),
                        evidence=QualitativeEvidenceAnchor(
                            linked_unit_ids=["unit-session-001-001"],
                            linked_code_ids=["strategy_shift"],
                            linked_memo_ids=["memo-session-001-001"],
                        ),
                        notes=["Synthetic fixture only."],
                    ),
                ],
                notes=["Synthetic fixture only."],
            )
        ],
        linked_codebook_ids=["demo-sensitive-study-core"],
        linked_memo_ids=["memo-session-001-001"],
        notes=[
            "Synthetic fixture only.",
            "Represents a bounded framework matrix grounded in coded excerpts and memos.",
        ],
    )


def default_mixed_method_join() -> MixedMethodJoin:
    return MixedMethodJoin(
        join_id="demo-sensitive-study-joint-display",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        title="Interaction breakdowns and task outcomes",
        join_strategy="convergent joint display",
        created_at=datetime.fromisoformat("2026-03-24T11:50:00+00:00"),
        created_by_role="analyst",
        framework_matrix_ids=["demo-sensitive-study-framework-matrix"],
        codebook_ids=["demo-sensitive-study-core"],
        quantitative_findings=[
            QuantitativeFinding(
                finding_id="completion_rate_scenario_a",
                source_label="Synthetic scenario A summary table",
                measure_label="Task completion rate",
                subgroup_label="scenario_a",
                numeric_value=0.62,
                unit="proportion",
                notes=["Synthetic fixture only."],
            ),
            QuantitativeFinding(
                finding_id="help_requests_scenario_a",
                source_label="Synthetic scenario A summary table",
                measure_label="Mean help requests per task",
                subgroup_label="scenario_a",
                numeric_value=1.8,
                unit="count",
                notes=["Synthetic fixture only."],
            ),
        ],
        rows=[
            MixedMethodJoinRow(
                row_id="scenario_a_breakdown_adaptation",
                row_label="Scenario A: breakdown with adaptive recovery",
                qualitative_summary=(
                    "Participants framed breakdowns as recoverable when they could pause, "
                    "reinterpret the prompt, and switch strategies."
                ),
                qualitative_evidence=QualitativeEvidenceAnchor(
                    linked_unit_ids=["unit-session-001-001"],
                    linked_code_ids=["usability_breakdown", "strategy_shift"],
                    linked_memo_ids=["memo-session-001-001"],
                ),
                quantitative_finding_ids=[
                    "completion_rate_scenario_a",
                    "help_requests_scenario_a",
                ],
                relationship=IntegrationRelationship.COMPLEMENTARITY,
                integrated_interpretation=(
                    "Moderate completion alongside elevated help requests suggests that "
                    "participants often recovered through adaptive strategy shifts rather "
                    "than friction-free interaction."
                ),
                notes=["Synthetic fixture only."],
            )
        ],
        notes=[
            "Synthetic fixture only.",
            (
                "Represents a bounded mixed-method join grounded in a framework matrix "
                "plus aggregate quantitative indicators."
            ),
        ],
    )


def default_team_coding_round() -> TeamCodingRound:
    return TeamCodingRound(
        round_id="demo-sensitive-study-round-001",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        created_at=datetime.fromisoformat("2026-03-24T12:00:00+00:00"),
        created_by_role="senior_analyst",
        facilitator_role="senior_analyst",
        coder_roles=["analyst", "senior_analyst"],
        adjudicator_role="study_steward",
        linked_codebook_ids=["demo-sensitive-study-core"],
        linked_framework_matrix_ids=["demo-sensitive-study-framework-matrix"],
        linked_mixed_method_join_ids=["demo-sensitive-study-joint-display"],
        assignments=[
            TeamCodingAssignment(
                assignment_id="assignment-unit-session-001-001",
                unit_id="unit-session-001-001",
                primary_coder_role="analyst",
                secondary_coder_role="senior_analyst",
                focus_code_ids=["usability_breakdown", "strategy_shift"],
                linked_memo_ids=["memo-session-001-001"],
                notes=[
                    "Synthetic fixture only.",
                    "Represents a double-coded assignment queued for later adjudication.",
                ],
            )
        ],
        notes=[
            "Synthetic fixture only.",
            "Represents a bounded team-coding round linked to the synthesis layer.",
        ],
    )


def default_adjudication_decision() -> AdjudicationDecision:
    return AdjudicationDecision(
        decision_id="adjudication-unit-session-001-001",
        round_id="demo-sensitive-study-round-001",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        decided_at=datetime.fromisoformat("2026-03-24T12:20:00+00:00"),
        adjudicator_role="study_steward",
        unit_id="unit-session-001-001",
        compared_application_ids=[
            "app-session-001-001-usability-breakdown",
            "app-session-001-001-strategy-shift",
        ],
        outcome=AdjudicationOutcome.MERGED_RESOLUTION,
        retained_code_ids=["usability_breakdown", "strategy_shift"],
        linked_memo_ids=["memo-session-001-001"],
        linked_framework_matrix_ids=["demo-sensitive-study-framework-matrix"],
        linked_mixed_method_join_ids=["demo-sensitive-study-joint-display"],
        rationale=(
            "Both coders captured a valid part of the excerpt, so the adjudicated "
            "resolution retains the breakdown and adaptation codes together."
        ),
        follow_up_actions=[
            "Update the framework matrix row to reflect the combined interpretation."
        ],
        notes=[
            "Synthetic fixture only.",
            "Represents a merged adjudication outcome grounded in coding and synthesis artifacts.",
        ],
    )


def default_assistive_algorithm_policy_gate() -> AssistiveAlgorithmPolicyGate:
    return AssistiveAlgorithmPolicyGate(
        gate_id="demo-sensitive-study-assistive-gate-001",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        requested_at=datetime.fromisoformat("2026-03-24T12:30:00+00:00"),
        requested_by_role="senior_analyst",
        algorithm_label="bounded_theme_suggester_v1",
        algorithm_runtime=AssistiveAlgorithmRuntime.LOCAL_STATISTICAL,
        purpose=(
            "Generate candidate synthesis themes from adjudicated coding artifacts "
            "for analyst review."
        ),
        proposed_uses=[ApprovedUse.INTERNAL_ANALYSIS],
        input_locator=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://workspace/demo-sensitive-study/coding/synthesis-input.json",
        ),
        output_locator=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://workspace/demo-sensitive-study/coding/assistive-themes.json",
        ),
        requires_human_review=True,
        requires_deidentification=True,
        decision=AssistivePolicyDecision.APPROVED_WITH_CONDITIONS,
        decision_rationale=(
            "Approved for internal synthesis support only after de-identification checks "
            "and manual analyst review of all suggested themes."
        ),
        decision_by_role="study_steward",
        decided_at=datetime.fromisoformat("2026-03-24T12:35:00+00:00"),
        required_controls=[
            "Record model and prompt parameters in audit events before export.",
            "Require manual analyst confirmation before any synthesis export is released.",
        ],
        notes=[
            "Synthetic fixture only.",
            "Represents a bounded assistive-policy gate tied to one workspace.",
        ],
    )


def default_synthesis_export_record() -> SynthesisExportRecord:
    return SynthesisExportRecord(
        export_id="demo-sensitive-study-synthesis-export-001",
        workspace_id="demo-sensitive-study-coding",
        study_slug="demo-sensitive-study",
        created_at=datetime.fromisoformat("2026-03-24T12:45:00+00:00"),
        created_by_role="senior_analyst",
        export_kind=SynthesisExportKind.MIXED_METHOD_BRIEF,
        source_codebook_ids=["demo-sensitive-study-core"],
        source_framework_matrix_ids=["demo-sensitive-study-framework-matrix"],
        source_mixed_method_join_ids=["demo-sensitive-study-joint-display"],
        source_team_coding_round_ids=["demo-sensitive-study-round-001"],
        source_adjudication_decision_ids=["adjudication-unit-session-001-001"],
        source_memo_ids=["memo-session-001-001"],
        included_approved_uses=[
            ApprovedUse.INTERNAL_ANALYSIS,
            ApprovedUse.DEIDENTIFIED_EXPORT,
        ],
        sensitivity=SensitivityLevel.RESTRICTED,
        export_locator=StorageLocator(
            storage_scheme=StorageScheme.SECURE_URI,
            locator="secure://exports/demo-sensitive-study/synthesis-export-001.json",
        ),
        assistive_algorithm_gate_id="demo-sensitive-study-assistive-gate-001",
        assistive_algorithms_applied=["bounded_theme_suggester_v1"],
        audit_event_ids=["event-demo-sensitive-study-synthesis-export-001"],
        notes=[
            "Synthetic fixture only.",
            "Represents a bounded synthesis export grounded in collaboration-layer artifacts.",
        ],
    )
