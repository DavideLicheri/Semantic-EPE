/**
 * API Types for EURING Frontend
 * Simplified types matching the actual backend API
 */

// Recognition API Types
export interface RecognitionRequest {
  euring_string: string;
  include_analysis?: boolean;
}

export interface RecognitionResponse {
  success: boolean;
  version?: string;
  confidence?: number;
  euring_string: string;
  length: number;
  discriminant_analysis?: Record<string, any>;
  detailed_analysis?: Record<string, any>;
  error?: string;
  processing_time_ms?: number;
}

// Conversion API Types
export interface ConversionRequest {
  euring_string: string;
  source_version: string;
  target_version: string;
  use_semantic?: boolean;
}

export interface ConversionResponse {
  success: boolean;
  converted_string?: string;
  source_version: string;
  target_version: string;
  conversion_method?: string;
  conversion_notes?: string[];
  semantic_data?: Record<string, any>;
  error?: string;
  processing_time_ms?: number;
}

// Batch API Types
export interface BatchRecognitionRequest {
  euring_strings: string[];
  include_analysis?: boolean;
  max_concurrent?: number;
}

export interface BatchRecognitionResponse {
  success: boolean;
  total_processed: number;
  results: RecognitionResponse[];
  processing_time_ms?: number;
  error?: string;
}

export interface BatchConversionRequest {
  conversions: ConversionRequest[];
  max_concurrent?: number;
}

export interface BatchConversionResponse {
  success: boolean;
  total_processed: number;
  results: ConversionResponse[];
  processing_time_ms?: number;
  error?: string;
}

// Version Info Types
export interface VersionInfo {
  version: string;
  name: string;
  description: string;
  format: string;
  typical_length: number;
  example: string;
}

export interface VersionsResponse {
  supported_versions: VersionInfo[];
  conversion_matrix: Record<string, string[]>;
}

// Health Check Types
export interface HealthResponse {
  status: string;
  services?: Record<string, string>;
  timestamp?: string;
  error?: string;
}

// UI State Types
export interface ProcessingState {
  loading: boolean;
  error?: string;
  success?: string;
}

export interface RecognitionResult {
  original_string: string;
  version: string;
  confidence: number;
  processing_time: number;
  analysis?: Record<string, any>;
}

export interface ConversionResult {
  original_string: string;
  converted_string: string;
  source_version: string;
  target_version: string;
  processing_time: number;
  notes: string[];
}

// Form Types
export interface RecognitionFormData {
  input_text: string;
  include_analysis: boolean;
  batch_mode: boolean;
}

export interface ConversionFormData {
  input_text: string;
  source_version: string;
  target_version: string;
  use_semantic: boolean;
  batch_mode: boolean;
}

// Domain Analysis API Types
export interface DomainListResponse {
  success: boolean;
  domains?: Array<{
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
  }>;
  total_domains?: number;
  error?: string;
  processing_time_ms?: number;
}

export interface DomainEvolutionResponse {
  success: boolean;
  domain: string;
  evolution_data?: {
    domain: string;
    evolution_summary: any;
    evolution_entries: Array<{
      version: string;
      year: number;
      changes_summary: string;
      fields_added: string[];
      fields_removed: string[];
      fields_modified: string[];
      semantic_notes: string[];
      format_changes: string[];
    }>;
    compatibility_matrix: {
      available: boolean;
      compatibility_map: Record<string, string>;
    };
    field_evolution_map: Record<string, any>;
  };
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
    evolution_history: Array<{
      version: string;
      year: number;
      changes_summary: string;
      fields_added: string[];
      fields_removed: string[];
      fields_modified: string[];
      semantic_notes: string[];
      format_changes: string[];
    }>;
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

// Domain Analysis API Types
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