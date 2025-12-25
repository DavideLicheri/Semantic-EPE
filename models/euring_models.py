"""
Core data models for EURING Code Recognition System
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class TransformationType(str, Enum):
    DIRECT = "direct"
    CALCULATED = "calculated"
    CONDITIONAL = "conditional"
    SPLIT = "split"
    MERGE = "merge"


class CompatibilityLevel(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    LIMITED = "limited"
    NONE = "none"


class PaymentStatus(str, Enum):
    FREE = "free"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class SemanticDomain(str, Enum):
    IDENTIFICATION_MARKING = "identification_marking"
    SPECIES = "species"
    DEMOGRAPHICS = "demographics"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    BIOMETRICS = "biometrics"
    METHODOLOGY = "methodology"


class DomainCompatibilityLevel(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    LOSSY = "lossy"
    INCOMPATIBLE = "incompatible"


class DomainChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    RENAMED = "renamed"


class FieldDefinition(BaseModel):
    position: int
    name: str
    data_type: str
    length: int
    valid_values: Optional[List[str]] = None
    description: str
    semantic_domain: Optional[SemanticDomain] = None
    semantic_meaning: Optional[str] = None
    evolution_notes: Optional[List[str]] = None


class ValidationRule(BaseModel):
    field_name: str
    rule_type: str
    rule_expression: str
    error_message: str


class FormatSpec(BaseModel):
    total_length: int
    field_separator: Optional[str] = None
    encoding: str = "utf-8"
    validation_pattern: Optional[str] = None


class EuringVersion(BaseModel):
    id: str
    name: str
    year: int
    description: str
    field_definitions: List[FieldDefinition]
    validation_rules: List[ValidationRule]
    format_specification: FormatSpec


class TransformationRule(BaseModel):
    rule_id: str
    source_field: Optional[str] = None
    target_field: str
    transformation_type: TransformationType
    transformation_expression: str
    conditions: Optional[Dict[str, Any]] = None


class FieldMapping(BaseModel):
    source_field: str
    target_field: str
    transformation_type: TransformationType
    transformation_function: Optional[str] = None
    semantic_domain: Optional[SemanticDomain] = None
    conversion_accuracy: Optional[float] = None


class DomainConversionMapping(BaseModel):
    domain: SemanticDomain
    compatibility: DomainCompatibilityLevel
    field_mappings: List[FieldMapping]
    transformation_rules: List[TransformationRule]
    lossy_conversion: bool
    conversion_notes: List[str]


class ConversionMapping(BaseModel):
    from_version: str
    to_version: str
    field_mappings: List[FieldMapping]
    transformation_rules: List[TransformationRule]
    compatibility_level: CompatibilityLevel
    domain_mappings: Optional[List[DomainConversionMapping]] = None


class VersionRelationship(BaseModel):
    from_version: str
    to_version: str
    relationship_type: str
    description: str


class DomainChange(BaseModel):
    change_type: DomainChangeType
    field_name: str
    previous_value: Optional[Any] = None
    new_value: Optional[Any] = None
    semantic_impact: str
    compatibility_impact: DomainCompatibilityLevel


class DomainEvolutionEntry(BaseModel):
    version: str
    year: int
    changes: List[DomainChange]
    field_mappings: List[FieldMapping]
    semantic_notes: List[str]
    fields_added: Optional[List[str]] = None
    fields_removed: Optional[List[str]] = None
    fields_modified: Optional[List[str]] = None
    format_changes: Optional[List[str]] = None
    semantic_improvements: Optional[List[str]] = None
    compatibility_notes: Optional[List[str]] = None


class DomainCompatibilityMatrix(BaseModel):
    """Matrix storing compatibility levels between versions for a specific domain"""
    domain: SemanticDomain
    compatibility_map: Dict[Tuple[str, str], DomainCompatibilityLevel] = Field(default_factory=dict)
    
    class Config:
        # Allow tuple keys in dict by using a custom serializer
        json_encoders = {
            tuple: lambda v: f"{v[0]}->{v[1]}"
        }
    
    def get_compatibility(self, from_version: str, to_version: str) -> DomainCompatibilityLevel:
        """Get compatibility level between two versions for this domain"""
        return self.compatibility_map.get((from_version, to_version), DomainCompatibilityLevel.INCOMPATIBLE)
    
    def set_compatibility(self, from_version: str, to_version: str, level: DomainCompatibilityLevel):
        """Set compatibility level between two versions for this domain"""
        self.compatibility_map[(from_version, to_version)] = level


class SemanticDomainDefinition(BaseModel):
    id: str
    name: str
    description: str
    fields: List[str]
    evolution_history: List[DomainEvolutionEntry]


class DomainEvolution(BaseModel):
    domain: SemanticDomain
    evolution_entries: List[DomainEvolutionEntry]
    compatibility_matrix: DomainCompatibilityMatrix
    field_evolution_map: Optional[Dict[str, Any]] = None  # Will store FieldEvolution objects


class SemanticDomainMapping(BaseModel):
    domain: SemanticDomain
    fields: List[str]
    domain_specific_rules: List[ValidationRule]
    evolution_from_previous: Optional[DomainEvolutionEntry] = None


class EuringVersion(BaseModel):
    id: str
    name: str
    year: int
    description: str
    field_definitions: List[FieldDefinition]
    validation_rules: List[ValidationRule]
    format_specification: FormatSpec
    semantic_domains: Optional[List[SemanticDomainMapping]] = None


class EuringVersionModel(BaseModel):
    versions: List[EuringVersion]
    relationships: List[VersionRelationship]
    conversion_mappings: List[ConversionMapping]
    semantic_domains: Optional[List[SemanticDomainDefinition]] = None
    domain_evolutions: Optional[List[DomainEvolution]] = None


class AnalysisMetadata(BaseModel):
    processing_time_ms: float
    algorithm_version: str
    confidence_factors: Dict[str, float]
    field_matches: Dict[str, bool]


class RecognitionResult(BaseModel):
    detected_version: EuringVersion
    confidence: float = Field(ge=0.0, le=1.0)
    alternative_versions: Optional[List[EuringVersion]] = None
    analysis_details: AnalysisMetadata


class BatchRecognitionResult(BaseModel):
    results: List[RecognitionResult]
    processing_summary: Dict[str, Any]
    same_version_detected: bool
    total_processed: int


class ConversionMetadata(BaseModel):
    conversion_timestamp: datetime
    processing_time_ms: float
    fields_converted: List[str]
    warnings: Optional[List[str]] = None


class BillingInfo(BaseModel):
    conversion_count: int
    free_conversions_used: int
    paid_conversions: int
    total_cost: float
    currency: str = "EUR"
    payment_required: bool


class ConversionResult(BaseModel):
    original_string: str
    converted_string: str
    from_version: str
    to_version: str
    conversion_metadata: ConversionMetadata
    billing_info: Optional[BillingInfo] = None


class ConversionRequest(BaseModel):
    input_string: str
    from_version: str
    to_version: str
    user_id: str


class BatchConversionResult(BaseModel):
    results: List[ConversionResult]
    total_processed: int
    successful_conversions: int
    failed_conversions: int
    total_billing_info: Optional[BillingInfo] = None


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class UserQuota(BaseModel):
    user_id: str
    free_conversions_used: int
    free_conversions_remaining: int
    total_conversions_this_month: int


class CostCalculation(BaseModel):
    free_conversions: int
    paid_conversions: int
    price_per_string: float
    total_cost: float
    currency: str = "EUR"


class QuotaCheckResult(BaseModel):
    quota_available: bool
    remaining_free: int
    cost_calculation: Optional[CostCalculation] = None
    payment_required: bool


class PaymentResult(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    amount_charged: float
    currency: str = "EUR"


class PricingConfiguration(BaseModel):
    free_conversion_limit: int = 19
    price_per_string_cents: int = 10  # 10 cents per string
    currency: str = "EUR"
    last_updated: datetime
    updated_by: str


class BillingHistory(BaseModel):
    id: str
    user_id: str
    timestamp: datetime
    conversion_count: int
    amount_charged: float
    currency: str
    payment_status: PaymentStatus
    transaction_id: Optional[str] = None


class UserSession(BaseModel):
    user_id: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    conversion_history: List['ConversionHistoryEntry']
    current_quota: UserQuota


class ExportedFile(BaseModel):
    filename: str
    format: str
    size_bytes: int
    created_at: datetime
    download_url: str


class ConversionHistoryEntry(BaseModel):
    timestamp: datetime
    original_strings: List[str]
    results: List[ConversionResult]
    exported_files: Optional[List[ExportedFile]] = None
    billing_info: Optional[BillingInfo] = None


# Update forward references
UserSession.model_rebuild()