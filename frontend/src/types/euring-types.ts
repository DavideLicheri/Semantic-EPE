/**
 * TypeScript interfaces for EURING Code Recognition System Frontend
 */

export enum TransformationType {
  DIRECT = "direct",
  CALCULATED = "calculated",
  CONDITIONAL = "conditional",
  SPLIT = "split",
  MERGE = "merge"
}

export enum CompatibilityLevel {
  FULL = "full",
  PARTIAL = "partial",
  LIMITED = "limited",
  NONE = "none"
}

export enum PaymentStatus {
  FREE = "free",
  PENDING = "pending",
  COMPLETED = "completed",
  FAILED = "failed"
}

export interface FieldDefinition {
  position: number;
  name: string;
  dataType: string;
  length: number;
  validValues?: string[];
  description: string;
}

export interface ValidationRule {
  fieldName: string;
  ruleType: string;
  ruleExpression: string;
  errorMessage: string;
}

export interface FormatSpec {
  totalLength: number;
  fieldSeparator?: string;
  encoding: string;
  validationPattern?: string;
}

export interface EuringVersion {
  id: string;
  name: string;
  year: number;
  description: string;
  fieldDefinitions: FieldDefinition[];
  validationRules: ValidationRule[];
  formatSpecification: FormatSpec;
}

export interface AnalysisMetadata {
  processingTimeMs: number;
  algorithmVersion: string;
  confidenceFactors: Record<string, number>;
  fieldMatches: Record<string, boolean>;
}

export interface RecognitionResult {
  detectedVersion: EuringVersion;
  confidence: number;
  alternativeVersions?: EuringVersion[];
  analysisDetails: AnalysisMetadata;
}

export interface BatchRecognitionResult {
  results: RecognitionResult[];
  processingSummary: Record<string, any>;
  sameVersionDetected: boolean;
  totalProcessed: number;
}

export interface ConversionMetadata {
  conversionTimestamp: string;
  processingTimeMs: number;
  fieldsConverted: string[];
  warnings?: string[];
}

export interface BillingInfo {
  conversionCount: number;
  freeConversionsUsed: number;
  paidConversions: number;
  totalCost: number;
  currency: string;
  paymentRequired: boolean;
}

export interface ConversionResult {
  originalString: string;
  convertedString: string;
  fromVersion: string;
  toVersion: string;
  conversionMetadata: ConversionMetadata;
  billingInfo?: BillingInfo;
}

export interface ConversionRequest {
  inputString: string;
  fromVersion: string;
  toVersion: string;
  userId: string;
}

export interface BatchConversionResult {
  results: ConversionResult[];
  totalProcessed: number;
  successfulConversions: number;
  failedConversions: number;
  totalBillingInfo?: BillingInfo;
}

export interface UserQuota {
  userId: string;
  freeConversionsUsed: number;
  freeConversionsRemaining: number;
  totalConversionsThisMonth: number;
}

export interface CostCalculation {
  freeConversions: number;
  paidConversions: number;
  pricePerString: number;
  totalCost: number;
  currency: string;
}

export interface QuotaCheckResult {
  quotaAvailable: boolean;
  remainingFree: number;
  costCalculation?: CostCalculation;
  paymentRequired: boolean;
}

export interface PaymentResult {
  success: boolean;
  transactionId?: string;
  errorMessage?: string;
  amountCharged: number;
  currency: string;
}

export interface PricingConfiguration {
  freeConversionLimit: number;
  pricePerStringCents: number;
  currency: string;
  lastUpdated: string;
  updatedBy: string;
}

export interface BillingHistory {
  id: string;
  userId: string;
  timestamp: string;
  conversionCount: number;
  amountCharged: number;
  currency: string;
  paymentStatus: PaymentStatus;
  transactionId?: string;
}

export interface ExportedFile {
  filename: string;
  format: string;
  sizeBytes: number;
  createdAt: string;
  downloadUrl: string;
}

export interface ConversionHistoryEntry {
  timestamp: string;
  originalStrings: string[];
  results: ConversionResult[];
  exportedFiles?: ExportedFile[];
  billingInfo?: BillingInfo;
}

export interface UserSession {
  userId: string;
  sessionId: string;
  createdAt: string;
  lastActivity: string;
  conversionHistory: ConversionHistoryEntry[];
  currentQuota: UserQuota;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
  user: {
    id: string;
    username: string;
  };
}

// UI Component Props
export interface RecognitionFormProps {
  onSubmit: (strings: string[], sameVersion?: boolean) => void;
  loading?: boolean;
}

export interface ConversionFormProps {
  recognitionResult: RecognitionResult;
  availableVersions: EuringVersion[];
  onConvert: (targetVersion: string) => void;
  loading?: boolean;
}

export interface ResultsDisplayProps {
  results: ConversionResult[];
  onExport: (format: string) => void;
  onSave: () => void;
}

export interface BillingDisplayProps {
  quota: UserQuota;
  costCalculation?: CostCalculation;
  onPayment: (amount: number) => void;
}

export interface HistoryDisplayProps {
  history: ConversionHistoryEntry[];
  onExport: (entry: ConversionHistoryEntry, format: string) => void;
}

// Domain Analysis Types
export enum SemanticDomain {
  IDENTIFICATION_MARKING = "identification_marking",
  SPECIES = "species", 
  DEMOGRAPHICS = "demographics",
  TEMPORAL = "temporal",
  SPATIAL = "spatial",
  BIOMETRICS = "biometrics",
  METHODOLOGY = "methodology"
}

export interface DomainInfo {
  domain: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  stability_score: number;
  complexity: string;
  statistics: {
    total_fields: number;
    field_counts_by_version: Record<string, number>;
    versions_present: number;
    total_versions: number;
    coverage_percentage: number;
  };
  has_evolution_data: boolean;
  api_endpoints: string[];
}

export interface DomainListResponse {
  success: boolean;
  domains?: DomainInfo[];
  total_domains?: number;
  error?: string;
  processing_time_ms?: number;
}

export interface DomainEvolutionEntry {
  version: string;
  year: number;
  changes_summary: string;
  fields_added: string[];
  fields_removed: string[];
  fields_modified: string[];
  semantic_notes: string[];
  format_changes: string[];
}

export interface DomainEvolutionData {
  domain: string;
  evolution_summary: any;
  evolution_entries: DomainEvolutionEntry[];
  compatibility_matrix: {
    available: boolean;
    compatibility_map: Record<string, string>;
  };
  field_evolution_map: Record<string, any>;
}

export interface DomainEvolutionResponse {
  success: boolean;
  domain: string;
  evolution_data?: DomainEvolutionData;
  error?: string;
  processing_time_ms?: number;
}

export interface DomainDocumentationResponse {
  success: boolean;
  domain: string;
  documentation?: {
    domain_info: {
      name: string;
      description: string;
      purpose: string;
      key_concepts: string[];
    };
    field_definitions: Record<string, any[]>;
    evolution_history: DomainEvolutionEntry[];
    usage_guidelines: string[];
    statistics: {
      total_versions: number;
      versions_with_domain: number;
      total_fields_across_versions: number;
      evolution_entries: number;
    };
    related_domains: string[];
  };
  error?: string;
  processing_time_ms?: number;
}

// Domain Analysis Types
export interface DomainFieldsResponse {
  success: boolean;
  domain: string;
  field_groups?: Array<{
    group_id: string;
    group_name: string;
    fields: string[];
    semantic_theme: string;
    cohesion_score: number;
    relationships: Array<{
      field1: string;
      field2: string;
      relationship_type: string;
      strength: number;
      semantic_basis: string;
    }>;
  }>;
  semantic_analysis?: {
    domain_analysis: any;
    field_categories: any;
    total_fields: number;
    total_groups: number;
    versions_analyzed: number;
    grouping_statistics: {
      average_group_size: number;
      average_cohesion: number;
      ungrouped_fields: number;
    };
  };
  error?: string;
  processing_time_ms?: number;
}

export interface DomainCompatibilityResponse {
  success: boolean;
  domain: string;
  from_version: string;
  to_version: string;
  compatibility_data?: {
    assessment_result: any;
    compatibility_matrix: {
      available: boolean;
      compatibility_level?: string;
    };
    summary: {
      overall_compatibility: string;
      is_lossy_conversion: boolean;
      total_warnings: number;
      field_compatibility_count: number;
      loss_types: string[];
    };
    detailed_analysis: {
      field_level_compatibility: any[];
      conversion_warnings: string[];
      conversion_notes: string[];
      loss_details: any[];
    };
  };
  error?: string;
  processing_time_ms?: number;
}

export interface DomainExportResponse {
  success: boolean;
  domain: string;
  export_data?: {
    domain: string;
    export_metadata: {
      export_timestamp: string;
      export_format: string;
      versions_included: string[];
      total_versions: number;
      exporter_version: string;
    };
    evolution_data?: any;
    field_analysis?: any;
    compatibility_data?: any;
  };
  export_format?: string;
  error?: string;
  processing_time_ms?: number;
}

export interface DomainComparisonResponse {
  success: boolean;
  domain: string;
  version1: string;
  version2: string;
  comparison_data?: {
    domain: string;
    version1: string;
    version2: string;
    analyzer_comparison: any;
    skos_comparison: any;
    field_mappings: any[];
    summary: {
      compatibility_level: string;
      total_changes: number;
      fields_added: number;
      fields_removed: number;
      fields_modified: number;
      has_field_mappings: boolean;
    };
  };
  error?: string;
  processing_time_ms?: number;
}