/**
 * API Service for EURING Backend Communication
 */
import axios from 'axios';
import { authService } from './auth';
import {
  RecognitionRequest,
  RecognitionResponse,
  ConversionRequest,
  ConversionResponse,
  BatchRecognitionRequest,
  BatchRecognitionResponse,
  BatchConversionRequest,
  BatchConversionResponse,
  VersionsResponse,
  HealthResponse,
  DomainListResponse,
  DomainEvolutionResponse,
  DomainDocumentationResponse,
  DomainFieldsResponse,
  DomainCompatibilityResponse,
  DomainExportResponse,
  DomainComparisonResponse
} from '../types/api-types';

// Configure axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      authService.logout();
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

export class EuringAPI {
  
  /**
   * Recognize EURING code version
   */
  static async recognize(request: RecognitionRequest): Promise<RecognitionResponse> {
    try {
      const response = await api.post<RecognitionResponse>('/api/euring/recognize', request);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Recognition failed');
    }
  }

  /**
   * Convert EURING code between versions
   */
  static async convert(request: ConversionRequest): Promise<ConversionResponse> {
    try {
      const response = await api.post<ConversionResponse>('/api/euring/convert', request);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Conversion failed');
    }
  }

  /**
   * Batch recognize multiple EURING codes
   */
  static async batchRecognize(request: BatchRecognitionRequest): Promise<BatchRecognitionResponse> {
    try {
      const response = await api.post<BatchRecognitionResponse>('/api/euring/batch/recognize', request);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Batch recognition failed');
    }
  }

  /**
   * Batch convert multiple EURING codes
   */
  static async batchConvert(request: BatchConversionRequest): Promise<BatchConversionResponse> {
    try {
      const response = await api.post<BatchConversionResponse>('/api/euring/batch/convert', request);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Batch conversion failed');
    }
  }

  /**
   * Get EURING versions matrix for comparative view
   */
  static async getEuringVersionsMatrix(): Promise<any> {
    try {
      // Add timestamp to bypass cache
      const timestamp = new Date().getTime();
      const response = await api.get(`/api/euring/versions/matrix?_t=${timestamp}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get EURING versions matrix');
    }
  }

  /**
   * Get supported versions information
   */
  static async getVersions(): Promise<VersionsResponse> {
    try {
      const response = await api.get<VersionsResponse>('/api/euring/versions');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get versions');
    }
  }

  /**
   * Health check
   */
  static async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await api.get<HealthResponse>('/api/euring/health');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Health check failed');
    }
  }

  /**
   * Parse multiple EURING strings from text
   */
  static parseEuringStrings(text: string): string[] {
    if (!text.trim()) return [];
    
    // Split by newlines and filter empty lines
    const lines = text.split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);
    
    return lines;
  }

  /**
   * Validate EURING string format (basic check)
   */
  static validateEuringString(euringString: string): { valid: boolean; message?: string } {
    if (!euringString || !euringString.trim()) {
      return { valid: false, message: 'EURING string cannot be empty' };
    }

    const trimmed = euringString.trim();
    
    // Basic length check
    if (trimmed.length < 20) {
      return { valid: false, message: 'EURING string too short (minimum 20 characters)' };
    }

    if (trimmed.length > 150) {
      return { valid: false, message: 'EURING string too long (maximum 150 characters)' };
    }

    // Check for obvious format patterns
    const hasPipes = trimmed.includes('|');
    const hasSpaces = trimmed.includes(' ');
    
    if (hasPipes && hasSpaces) {
      return { valid: false, message: 'EURING string cannot contain both pipes and spaces' };
    }

    return { valid: true };
  }

  /**
   * Format processing time for display
   */
  static formatProcessingTime(timeMs?: number): string {
    if (!timeMs) return 'N/A';
    
    if (timeMs < 1000) {
      return `${Math.round(timeMs)}ms`;
    } else {
      return `${(timeMs / 1000).toFixed(2)}s`;
    }
  }

  /**
   * Format confidence score for display
   */
  static formatConfidence(confidence?: number): string {
    if (confidence === undefined || confidence === null) return 'N/A';
    return `${Math.round(confidence * 100)}%`;
  }

  /**
   * Get version display name
   */
  static getVersionDisplayName(version: string): string {
    const versionMap: Record<string, string> = {
      'euring_1966': 'EURING 1966',
      'euring_1979': 'EURING 1979', 
      'euring_2000': 'EURING 2000',
      'euring_2020': 'EURING 2020',
      '1966': 'EURING 1966',
      '1979': 'EURING 1979',
      '2000': 'EURING 2000',
      '2020': 'EURING 2020'
    };
    
    return versionMap[version] || version;
  }

  /**
   * Get list of available semantic domains
   */
  static async getDomainsList(): Promise<DomainListResponse> {
    try {
      const response = await api.get<DomainListResponse>('/api/euring/domains/list');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get domains list');
    }
  }

  /**
   * Get domain evolution data
   */
  static async getDomainEvolution(domain: string): Promise<DomainEvolutionResponse> {
    try {
      const response = await api.get<DomainEvolutionResponse>(`/api/euring/domains/${domain}/evolution`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get domain evolution');
    }
  }

  /**
   * Get domain documentation
   */
  static async getDomainDocumentation(domain: string): Promise<DomainDocumentationResponse> {
    try {
      const response = await api.get<DomainDocumentationResponse>(`/api/euring/domains/${domain}/documentation`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get domain documentation');
    }
  }

  /**
   * Get domain display name
   */
  static getDomainDisplayName(domain: string): string {
    const domainMap: Record<string, string> = {
      'identification_marking': 'Identification & Marking',
      'species': 'Species Classification',
      'demographics': 'Demographics',
      'temporal': 'Temporal Information',
      'spatial': 'Spatial Information',
      'biometrics': 'Biometric Measurements',
      'methodology': 'Methodology & Conditions'
    };
    
    return domainMap[domain] || domain.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  /**
   * Get domain icon
   */
  static getDomainIcon(domain: string): string {
    const iconMap: Record<string, string> = {
      'identification_marking': '🏷️',
      'species': '🐦',
      'demographics': '👥',
      'temporal': '⏰',
      'spatial': '🌍',
      'biometrics': '📏',
      'methodology': '🔬'
    };
    
    return iconMap[domain] || '📊';
  }

  /**
   * Get domain field analysis
   */
  static async getDomainFields(domain: string): Promise<DomainFieldsResponse> {
    try {
      const response = await api.get<DomainFieldsResponse>(`/api/euring/domains/${domain}/fields`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get domain fields');
    }
  }

  /**
   * Get domain compatibility assessment
   */
  static async getDomainCompatibility(domain: string, fromVersion: string, toVersion: string): Promise<DomainCompatibilityResponse> {
    try {
      const response = await api.get<DomainCompatibilityResponse>(`/api/euring/domains/${domain}/compatibility/${fromVersion}/${toVersion}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get domain compatibility');
    }
  }

  /**
   * Parse a single EURING string into field-value pairs
   */
  static async parseEuringString(euringString: string, language: string = 'it'): Promise<any> {
    try {
      const response = await api.post('/api/euring/parse', {
        euring_string: euringString,
        language: language
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to parse EURING string');
    }
  }

  /**
   * Parse multiple EURING strings in batch
   */
  static async parseEuringStringsBatch(euringStrings: string[], language: string = 'it'): Promise<any> {
    try {
      const response = await api.post('/api/euring/parse/batch', {
        euring_strings: euringStrings,
        language: language
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to parse EURING strings batch');
    }
  }

  /**
   * Export domain data
   */
  static async exportDomainData(
    domain: string, 
    format: string = 'json',
    includeEvolution: boolean = true,
    includeFieldAnalysis: boolean = true,
    includeCompatibility: boolean = true
  ): Promise<DomainExportResponse> {
    try {
      const params = new URLSearchParams({
        format,
        include_evolution: includeEvolution.toString(),
        include_field_analysis: includeFieldAnalysis.toString(),
        include_compatibility: includeCompatibility.toString()
      });
      
      const response = await api.get<DomainExportResponse>(`/api/euring/domains/export/${domain}?${params}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to export domain data');
    }
  }

  /**
   * Compare domain versions
   */
  static async compareDomainVersions(domain: string, version1: string, version2: string): Promise<DomainComparisonResponse> {
    try {
      const response = await api.get<DomainComparisonResponse>(`/api/euring/domains/${domain}/compare/${version1}/${version2}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to compare domain versions');
    }
  }

  /**
   * Update a single field in the EURING matrix
   */
  static async updateMatrixField(
    fieldName: string,
    version: string,
    property: string,
    value: string,
    notes?: string
  ): Promise<any> {
    try {
      const response = await api.put('/api/euring/versions/matrix/field', {
        field_name: fieldName,
        version: version,
        property: property,
        value: value,
        notes: notes
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to update matrix field');
    }
  }

  /**
   * Add a new field to a specific EURING version
   */
  static async addFieldToVersion(
    fieldName: string,
    version: string,
    position: number,
    dataType: string = 'string',
    length: number = 10,
    description?: string
  ): Promise<any> {
    try {
      const response = await api.post('/api/euring/versions/matrix/field/add', {
        field_name: fieldName,
        version: version,
        position: position,
        data_type: dataType,
        length: length,
        description: description || `Campo ${fieldName} aggiunto manualmente alla versione ${version}`
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to add field to version');
    }
  }

  /**
   * Delete a field from a specific EURING version
   */
  static async deleteFieldFromVersion(fieldName: string, version: string): Promise<any> {
    try {
      const response = await api.delete('/api/euring/versions/matrix/field/remove', {
        data: { field_name: fieldName, version: version }
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to delete field from version');
    }
  }

  /**
   * Update multiple fields in the EURING matrix in bulk
   */
  static async updateMatrixBulk(updates: Array<{
    field_name: string;
    version: string;
    property: string;
    value: string;
    notes?: string;
  }>): Promise<any> {
    try {
      const response = await api.put('/api/euring/versions/matrix/bulk', {
        updates: updates
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to update matrix fields in bulk');
    }
  }

  /**
   * Get lookup table for a specific field in a version
   */
  static async getFieldLookupTable(fieldName: string, version: string): Promise<any> {
    try {
      const response = await api.get(`/api/euring/versions/${version}/field/${fieldName}/lookup`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get field lookup table');
    }
  }

  /**
   * Get all lookup tables for a version
   */
  static async getAllLookupTables(version: string): Promise<any> {
    try {
      const response = await api.get(`/api/euring/versions/${version}/lookups`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get lookup tables');
    }
  }

  /**
   * Update lookup table for a specific field
   */
  static async updateFieldLookupTable(fieldName: string, version: string, lookupData: any): Promise<any> {
    try {
      const response = await api.put(`/api/euring/versions/${version}/field/${fieldName}/lookup`, {
        field_name: fieldName,
        version: version,
        lookup_data: lookupData
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to update field lookup table');
    }
  }

  /**
   * Get field description for EURING fields
   */
  static getFieldDescription(fieldName: string): string {
    const descriptions: Record<string, string> = {
      // Campi in italiano
      'Osservatorio': 'Codice dell\'osservatorio che ha emesso l\'anello',
      'Centro': 'Centro di inanellamento',
      'Metodo di identificazione primario': 'Metodo principale utilizzato per identificare l\'uccello',
      'Verifica dell\'anello metallico': 'Verifica della presenza e leggibilità dell\'anello metallico',
      'Informazioni anello metallico': 'Dettagli sull\'anello metallico applicato',
      'Informazioni altri segni': 'Informazioni su altri segni di identificazione',
      'Specie': 'Codice della specie secondo la classificazione EURING',
      'Età conclusa': 'Età dell\'uccello determinata dall\'operatore',
      'Età riportata': 'Età dell\'uccello come riportata originariamente',
      'Sesso concluso': 'Sesso dell\'uccello determinato dall\'operatore',
      'Sesso riportato': 'Sesso dell\'uccello come riportato originariamente',
      'Data': 'Data dell\'osservazione o cattura',
      'Giorno': 'Giorno del mese (1-31)',
      'Mese': 'Mese dell\'anno (1-12)',
      'Anno': 'Anno dell\'osservazione',
      'Ora': 'Ora dell\'osservazione o cattura',
      'Codice luogo': 'Codice del luogo di osservazione',
      'Coordinate': 'Coordinate geografiche del luogo',
      'Latitudine': 'Latitudine in gradi decimali',
      'Longitudine': 'Longitudine in gradi decimali',
      'Precisione delle coordinate': 'Precisione delle coordinate geografiche',
      'Condizione': 'Condizione fisica dell\'uccello',
      'Circostanze': 'Circostanze della cattura o osservazione',
      'Circostanze presunte': 'Circostanze presunte della cattura',
      'Identificatore codice EURING': 'Identificatore univoco del codice EURING',
      'Lunghezza ala': 'Lunghezza dell\'ala in millimetri',
      'Terza primaria': 'Lunghezza della terza penna primaria',
      'Stato della punta dell\'ala': 'Condizione della punta dell\'ala',
      'Massa': 'Peso dell\'uccello in grammi',
      'Muta': 'Stato della muta delle penne',
      'Codice piumaggio': 'Codice che descrive il piumaggio',
      'Artiglio posteriore': 'Lunghezza dell\'artiglio posteriore',
      'Lunghezza becco': 'Lunghezza del becco in millimetri',
      'Metodo becco': 'Metodo utilizzato per misurare il becco',
      'Lunghezza totale testa': 'Lunghezza totale della testa',
      'Tarso': 'Lunghezza del tarso in millimetri',
      'Metodo tarso': 'Metodo utilizzato per misurare il tarso',
      'Lunghezza coda': 'Lunghezza della coda in millimetri',
      'Differenza coda': 'Differenza nella lunghezza delle penne della coda',
      'Punteggio grasso': 'Valutazione della quantità di grasso',
      'Metodo punteggio grasso': 'Metodo utilizzato per valutare il grasso',
      'Muscolo pettorale': 'Valutazione del muscolo pettorale',
      'Placca incubatrice': 'Presenza e stato della placca incubatrice',
      'Punteggio primarie': 'Valutazione dello stato delle penne primarie',
      'Muta primarie': 'Stato della muta delle penne primarie',
      'Copritrici maggiori vecchie': 'Numero di copritrici maggiori vecchie',
      'Alula': 'Stato dell\'alula',
      'Copritrice carpale': 'Stato della copritrice carpale'
    };
    
    return descriptions[fieldName] || 'Campo della stringa EURING';
  }
}

export default EuringAPI;