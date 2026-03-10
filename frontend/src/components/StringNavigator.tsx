import React, { useState, useRef } from 'react';
import EuringAPI from '../services/api';
import { SemanticDomain, getDomainInfo } from '../utils/semanticDomains';
import './StringNavigator.css';

interface ParsedString {
  index: number;
  success: boolean;
  euring_string: string;
  detected_version?: string;
  confidence?: number;
  parsed_fields?: Record<string, any>;
  epe_compatible?: boolean;
  field_count?: number;
  error?: string;
}

const StringNavigator: React.FC = () => {
  const [strings, setStrings] = useState<ParsedString[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [inputText, setInputText] = useState<string>('');
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Paginazione per i pulsanti di navigazione
  const BUTTONS_PER_PAGE = 50;
  const totalPages = Math.ceil(strings.length / BUTTONS_PER_PAGE);
  const startIndex = currentPage * BUTTONS_PER_PAGE;
  const endIndex = Math.min(startIndex + BUTTONS_PER_PAGE, strings.length);
  const currentPageStrings = strings.slice(startIndex, endIndex);

  const handleSingleSubmit = async () => {
    if (!inputText.trim()) {
      setError('Inserisci una stringa EURING');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await EuringAPI.parseEuringStringsBatch([inputText.trim()], 'it');
      
      if (response.success && response.results.length > 0) {
        setStrings(response.results);
        setCurrentIndex(0);
        setCurrentPage(0);
        setInputText('');
      } else {
        setError(response.error || 'Errore nel parsing della stringa');
      }
    } catch (err: any) {
      setError(err.message || 'Errore di parsing');
    } finally {
      setLoading(false);
    }
  };

  const handleBatchSubmit = async () => {
    if (!inputText.trim()) {
      setError('Inserisci le stringhe EURING (una per riga)');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const stringList = EuringAPI.parseEuringStrings(inputText);
      if (stringList.length === 0) {
        setError('Nessuna stringa valida trovata');
        return;
      }

      const response = await EuringAPI.parseEuringStringsBatch(stringList, 'it');
      
      if (response.success && response.results.length > 0) {
        setStrings(response.results);
        setCurrentIndex(0);
        setCurrentPage(0);
        setInputText('');
      } else {
        setError(response.error || 'Errore nel parsing delle stringhe');
      }
    } catch (err: any) {
      setError(err.message || 'Errore di parsing');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const text = await file.text();
      const stringList = EuringAPI.parseEuringStrings(text);
      
      if (stringList.length === 0) {
        setError('Nessuna stringa EURING valida trovata nel file');
        return;
      }

      const response = await EuringAPI.parseEuringStringsBatch(stringList, 'it');
      
      if (response.success && response.results.length > 0) {
        setStrings(response.results);
        setCurrentIndex(0);
        setCurrentPage(0);
      } else {
        setError(response.error || 'Errore nel parsing del file');
      }
    } catch (err: any) {
      setError(err.message || 'Errore nella lettura del file');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setStrings([]);
    setInputText('');
    setError(null);
    setCurrentIndex(0);
    setCurrentPage(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getFieldDomain = (fieldName: string): { domain: string; icon: string; color: string } => {
    // Mapping dei campi EURING ai domini semantici ufficiali
    const fieldLower = fieldName.toLowerCase();
    
    // IDENTIFICATION_MARKING - Anelli, schemi, marcaggi metallici e sistemi di verifica
    if (fieldLower.includes('osservatorio') || fieldLower.includes('centro') || 
        fieldLower.includes('anello') || fieldLower.includes('ring') ||
        fieldLower.includes('metodo di identificazione') || fieldLower.includes('verifica') ||
        fieldLower.includes('informazioni anello') || fieldLower.includes('altri segni') ||
        fieldLower.includes('identificatore')) {
      const info = getDomainInfo(SemanticDomain.IDENTIFICATION_MARKING);
      return { domain: info.name, icon: info.icon, color: info.color };
    }
    
    // SPECIES - Codici specie, tassonomia e sistemi di identificazione
    if (fieldLower.includes('specie') || fieldLower.includes('species')) {
      const info = getDomainInfo(SemanticDomain.SPECIES);
      return { domain: info.name, icon: info.icon, color: info.color };
    }
    
    // DEMOGRAPHICS - Sistemi di classificazione età e sesso
    if (fieldLower.includes('età') || fieldLower.includes('sesso') || 
        fieldLower.includes('age') || fieldLower.includes('sex') ||
        fieldLower.includes('conclus') || fieldLower.includes('riportat')) {
      const info = getDomainInfo(SemanticDomain.DEMOGRAPHICS);
      return { domain: info.name, icon: info.icon, color: info.color };
    }
    
    // TEMPORAL - Formati data e ora e loro evoluzione
    if (fieldLower.includes('data') || fieldLower.includes('ora') || 
        fieldLower.includes('date') || fieldLower.includes('time') ||
        fieldLower.includes('giorno') || fieldLower.includes('mese') || 
        fieldLower.includes('anno') || fieldLower.includes('day') ||
        fieldLower.includes('month') || fieldLower.includes('year')) {
      const info = getDomainInfo(SemanticDomain.TEMPORAL);
      return { domain: info.name, icon: info.icon, color: info.color };
    }
    
    // SPATIAL - Coordinate, accuratezza posizione e codifica geografica
    if (fieldLower.includes('coordinate') || fieldLower.includes('luogo') || 
        fieldLower.includes('latitudine') || fieldLower.includes('longitudine') ||
        fieldLower.includes('latitude') || fieldLower.includes('longitude') ||
        fieldLower.includes('codice luogo') || fieldLower.includes('precisione')) {
      const info = getDomainInfo(SemanticDomain.SPATIAL);
      return { domain: info.name, icon: info.icon, color: info.color };
    }
    
    // BIOMETRICS - Ala, peso, becco, tarso, grasso, muscolo e muta
    if (fieldLower.includes('lunghezza') || fieldLower.includes('massa') || 
        fieldLower.includes('ala') || fieldLower.includes('becco') || 
        fieldLower.includes('tarso') || fieldLower.includes('coda') ||
        fieldLower.includes('artiglio') || fieldLower.includes('testa') ||
        fieldLower.includes('grasso') || fieldLower.includes('muscolo') ||
        fieldLower.includes('primaria') || fieldLower.includes('muta') ||
        fieldLower.includes('piumaggio') || fieldLower.includes('placca') ||
        fieldLower.includes('copritrici') || fieldLower.includes('alula') ||
        fieldLower.includes('carpale') || fieldLower.includes('wing') ||
        fieldLower.includes('bill') || fieldLower.includes('tarsus') ||
        fieldLower.includes('weight') || fieldLower.includes('fat') ||
        fieldLower.includes('muscle')) {
      const info = getDomainInfo(SemanticDomain.BIOMETRICS);
      return { domain: info.name, icon: info.icon, color: info.color };
    }
    
    // METHODOLOGY - Metodi cattura, condizioni, codici manipolazione e procedure
    if (fieldLower.includes('condizione') || fieldLower.includes('circostanze') || 
        fieldLower.includes('metodo') || fieldLower.includes('stato') ||
        fieldLower.includes('punteggio') || fieldLower.includes('condition') ||
        fieldLower.includes('circumstances') || fieldLower.includes('method') ||
        fieldLower.includes('score') || fieldLower.includes('procedure')) {
      const info = getDomainInfo(SemanticDomain.METHODOLOGY);
      return { domain: info.name, icon: info.icon, color: info.color };
    }
    
    // Default fallback - use a neutral domain
    return { 
      domain: 'Altro', 
      icon: '📊', 
      color: '#95A5A6' 
    };
  };

  const isRelevantEuringField = (fieldName: string): boolean => {
    // Comprehensive blacklist of technical/internal fields that should not be shown to users
    const technicalFields = [
      'version', 'original_string', 'note', 'epe_error', 'parser_type', 'epe_validations',
      'field_count', 'confidence', 'detected_version', 'epe_compatible', 'success',
      'error', 'index', 'raw_value', 'validation_errors', 'parsing_errors',
      'internal_id', 'parser_version', 'validation_status', 'field_type',
      'data_type', 'field_length', 'field_position', 'field_format',
      'validation_rules', 'field_constraints', 'field_metadata',
      'processing_time', 'parser_confidence', 'field_validation',
      'semantic_domain', 'field_category', 'field_group', 'field_priority',
      'field_source', 'field_origin', 'field_mapping', 'field_transformation',
      'lookup_table', 'lookup_values', 'lookup_mapping', 'lookup_source',
      'domain_mapping', 'semantic_mapping', 'field_semantics',
      'conversion_notes', 'conversion_status', 'conversion_confidence',
      'field_notes', 'field_comments', 'field_description_internal',
      'parser_notes', 'validation_notes', 'processing_notes',
      'field_id', 'field_uuid', 'field_hash', 'field_checksum',
      'created_at', 'updated_at', 'processed_at', 'validated_at',
      'created_by', 'updated_by', 'processed_by', 'validated_by',
      'system_field', 'internal_field', 'technical_field', 'metadata_field',
      'debug_info', 'debug_data', 'debug_notes', 'debug_status',
      'test_field', 'test_data', 'test_notes', 'test_status',
      'temp_field', 'temporary_field', 'cache_field', 'buffer_field',
      '_epe_formatted_output', '_validation_timestamp'
    ];

    // Check if field name is in blacklist (case insensitive)
    const fieldLower = fieldName.toLowerCase();
    if (technicalFields.some(tech => fieldLower.includes(tech.toLowerCase()))) {
      return false;
    }

    // Additional checks for field patterns that indicate technical fields
    if (fieldLower.includes('_id') || fieldLower.includes('_uuid') || 
        fieldLower.includes('_hash') || fieldLower.includes('_checksum') ||
        fieldLower.includes('_metadata') || fieldLower.includes('_internal') ||
        fieldLower.includes('_system') || fieldLower.includes('_debug') ||
        fieldLower.includes('_test') || fieldLower.includes('_temp') ||
        fieldLower.includes('_cache') || fieldLower.includes('_buffer') ||
        fieldLower.startsWith('__') || fieldLower.endsWith('__')) {
      return false;
    }

    return true;
  };

  // Extract key information for quick navigation
  const getStringInfo = (parsedString: ParsedString) => {
    if (!parsedString.success || !parsedString.parsed_fields) {
      return {
        osservatorio: 'N/A',
        anello: 'N/A',
        specieRiportata: 'N/A',
        giorno: 'N/A',
        mese: 'N/A',
        anno: 'N/A',
        latitudine: 'N/A',
        longitudine: 'N/A'
      };
    }

    const fields = parsedString.parsed_fields;
    
    // Helper function to find field by multiple possible names
    const findFieldValue = (possibleNames: string[]): string => {
      for (const name of possibleNames) {
        // Check if field exists and has a value (could be direct value or object with value property)
        if (fields[name]) {
          const fieldData = fields[name];
          let value = '';
          
          // Handle different field data structures
          if (typeof fieldData === 'string') {
            value = fieldData;
          } else if (fieldData?.value) {
            value = fieldData.value;
          } else if (fieldData?.raw_value) {
            value = fieldData.raw_value;
          }
          
          if (value && value !== '' && value !== 'N/A') {
            return value;
          }
        }
      }
      return 'N/A';
    };

    // Extract fields with multiple possible names
    const osservatorio = findFieldValue([
      'Osservatorio', 'Centro', 'Schema', 'Observatory', 'Center', 'Scheme',
      'osservatorio', 'centro', 'schema'
    ]);
    
    const anello = findFieldValue([
      'Anello (10 caratteri)', "Verifica dell'anello metallico", 'Anello', 'Numero anello', 'Ring', 'Ring number', 'Numero_anello',
      'anello', 'numero anello', 'ring', 'ring number',
      'Informazioni anello metallico', 'Anello metallico', 'Metal ring', 'Ring info', 'Ring verification'
    ]);
    
    const specieRiportata = findFieldValue([
      'Specie riportata', 'Specie', 'Species', 'Codice specie', 'Species code',
      'specie riportata', 'specie', 'species', 'codice specie'
    ]);
    
    const giorno = findFieldValue([
      'Giorno', 'Day', 'giorno', 'day'
    ]);
    
    const mese = findFieldValue([
      'Mese', 'Month', 'mese', 'month'
    ]);
    
    const anno = findFieldValue([
      'Anno', 'Year', 'anno', 'year'
    ]);
    
    const latitudine = findFieldValue([
      'Latitudine', 'Latitude', 'Lat', 'latitudine', 'latitude', 'lat'
    ]);
    
    const longitudine = findFieldValue([
      'Longitudine', 'Longitude', 'Lon', 'Long', 'longitudine', 'longitude', 'lon', 'long'
    ]);

    const extractedInfo = { osservatorio, anello, specieRiportata, giorno, mese, anno, latitudine, longitudine };

    return extractedInfo;
  };

  // Funzione per cambiare stringa e aggiornare la pagina se necessario
  const changeCurrentIndex = (newIndex: number) => {
    setCurrentIndex(newIndex);
    // Calcola la pagina corretta per il nuovo indice
    const newPage = Math.floor(newIndex / BUTTONS_PER_PAGE);
    if (newPage !== currentPage) {
      setCurrentPage(newPage);
    }
  };

  const currentString = strings[currentIndex];

  return (
    <div className="string-navigator">
      <div className="navigator-header">
        <h2>Navigator Stringhe EURING</h2>
        <p>Analizza singole stringhe, batch di testo o file</p>
      </div>

      <div className="input-section">
        <div className="single-input">
          <div className="input-group">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Inserisci stringa EURING singola o multiple stringhe (una per riga)..."
              className="string-input"
              disabled={loading}
              rows={3}
            />
            <div className="button-group">
              <button
                onClick={handleSingleSubmit}
                disabled={loading || !inputText.trim()}
                className="parse-button"
              >
                {loading ? 'Analizzando...' : 'Analizza Singola'}
              </button>
              <button
                onClick={handleBatchSubmit}
                disabled={loading || !inputText.trim()}
                className="parse-button batch"
              >
                {loading ? 'Analizzando...' : 'Analizza Batch'}
              </button>
            </div>
          </div>
        </div>

        <div className="file-input">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".txt,.csv"
            className="file-input-hidden"
            disabled={loading}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
            className="file-button"
          >
            📁 Carica File (.txt, .csv)
          </button>
        </div>

        {strings.length > 0 && (
          <div className="action-buttons">
            <button onClick={handleClear} className="clear-button">
              Cancella Risultati
            </button>
            <span className="results-count">
              {strings.length} string{strings.length !== 1 ? 'he caricate' : 'a caricata'}
            </span>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {strings.length > 0 && (
        <>
          {/* Current string display - HORIZONTAL LAYOUT */}
          {currentString && (
            <div className="results-section">

              <div className="string-display">
                {currentString.success ? (
                  <>
                    {/* LAYOUT COMPLETAMENTE NUOVO - FORZATO */}
                    <div style={{
                      width: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '20px'
                    }}>
                      {/* STRINGA EURING IN ALTO - ORIZZONTALE */}
                      <div style={{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '15px',
                        background: '#e3f2fd',
                        border: '2px solid #1976d2',
                        borderRadius: '8px',
                        padding: '20px',
                        fontSize: '16px',
                        fontWeight: 'bold'
                      }}>
                        <span style={{
                          color: '#1976d2',
                          fontWeight: '700',
                          whiteSpace: 'nowrap',
                          fontSize: '16px'
                        }}>📍 STRINGA EURING:</span>
                        <span style={{
                          fontFamily: 'Monaco, Menlo, Ubuntu Mono, monospace',
                          fontSize: '14px',
                          color: '#0d47a1',
                          wordBreak: 'break-all',
                          flex: '1',
                          background: 'white',
                          padding: '8px 12px',
                          borderRadius: '4px',
                          border: '1px solid #bbdefb'
                        }}>{currentString.euring_string}</span>
                      </div>

                      {/* BARRA DI NAVIGAZIONE GRAFICA */}
                      {strings.length > 1 && (
                        <div style={{
                          width: '100%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '20px',
                          background: '#f8f9fa',
                          border: '1px solid #dee2e6',
                          borderRadius: '8px',
                          padding: '15px 20px'
                        }}>
                          {/* Pulsante Precedente */}
                          <button
                            onClick={() => changeCurrentIndex(Math.max(0, currentIndex - 1))}
                            disabled={currentIndex === 0}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              padding: '10px 16px',
                              background: currentIndex === 0 ? '#e9ecef' : '#007bff',
                              color: currentIndex === 0 ? '#6c757d' : 'white',
                              border: 'none',
                              borderRadius: '6px',
                              fontSize: '14px',
                              fontWeight: '500',
                              cursor: currentIndex === 0 ? 'not-allowed' : 'pointer',
                              transition: 'all 0.2s ease'
                            }}
                            onMouseEnter={(e) => {
                              if (currentIndex > 0) {
                                (e.target as HTMLButtonElement).style.background = '#0056b3';
                              }
                            }}
                            onMouseLeave={(e) => {
                              if (currentIndex > 0) {
                                (e.target as HTMLButtonElement).style.background = '#007bff';
                              }
                            }}
                          >
                            <span style={{ fontSize: '16px' }}>←</span>
                            Precedente
                          </button>

                          {/* Indicatore di Posizione */}
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '15px',
                            padding: '8px 20px',
                            background: 'white',
                            border: '2px solid #007bff',
                            borderRadius: '25px',
                            fontSize: '16px',
                            fontWeight: '600',
                            color: '#007bff'
                          }}>
                            <span style={{ fontSize: '14px', color: '#6c757d' }}>Stringa</span>
                            <span style={{ 
                              fontSize: '20px', 
                              color: '#007bff',
                              minWidth: '60px',
                              textAlign: 'center'
                            }}>
                              {currentIndex + 1} / {strings.length}
                            </span>
                          </div>

                          {/* Pulsante Successivo */}
                          <button
                            onClick={() => changeCurrentIndex(Math.min(strings.length - 1, currentIndex + 1))}
                            disabled={currentIndex === strings.length - 1}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              padding: '10px 16px',
                              background: currentIndex === strings.length - 1 ? '#e9ecef' : '#007bff',
                              color: currentIndex === strings.length - 1 ? '#6c757d' : 'white',
                              border: 'none',
                              borderRadius: '6px',
                              fontSize: '14px',
                              fontWeight: '500',
                              cursor: currentIndex === strings.length - 1 ? 'not-allowed' : 'pointer',
                              transition: 'all 0.2s ease'
                            }}
                            onMouseEnter={(e) => {
                              if (currentIndex < strings.length - 1) {
                                (e.target as HTMLButtonElement).style.background = '#0056b3';
                              }
                            }}
                            onMouseLeave={(e) => {
                              if (currentIndex < strings.length - 1) {
                                (e.target as HTMLButtonElement).style.background = '#007bff';
                              }
                            }}
                          >
                            Successiva
                            <span style={{ fontSize: '16px' }}>→</span>
                          </button>
                        </div>
                      )}

                      {/* TABELLA CAMPI AL CENTRO */}
                      <div style={{
                        width: '100%',
                        background: 'white',
                        border: '1px solid #e0e0e0',
                        borderRadius: '8px',
                        padding: '20px'
                      }}>
                        <h4 style={{
                          margin: '0 0 15px 0',
                          color: '#2c3e50',
                          fontSize: '18px'
                        }}>📊 Campi Analizzati</h4>
                        
                        {/* Header delle colonne */}
                        <div style={{
                          display: 'flex',
                          padding: '8px 12px',
                          background: '#e3f2fd',
                          borderRadius: '6px',
                          marginBottom: '12px',
                          fontSize: '14px',
                          fontWeight: '600',
                          color: '#1976d2',
                          gap: '12px',
                          alignItems: 'center'
                        }}>
                          <div style={{ minWidth: '60px', textAlign: 'center' }}>Dominio</div>
                          <div style={{ width: '35%', minWidth: '200px' }}>Campo</div>
                          <div style={{ flex: '1' }}>Valore</div>
                        </div>
                        <div style={{
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '8px'
                        }}>
                          {currentString.parsed_fields && Object.entries(currentString.parsed_fields)
                            .filter(([fieldName]) => isRelevantEuringField(fieldName))
                            .map(([fieldName, fieldData]: [string, any]) => {
                            const fieldValue = fieldData?.value || fieldData?.raw_value || fieldData || '-';
                            const domainInfo = getFieldDomain(fieldName);
                            
                            // Only show fields with actual values
                            if (!fieldValue || fieldValue === '-' || fieldValue === '' || fieldValue === null || fieldValue === undefined) {
                              return null;
                            }
                            
                            // Additional check for empty objects or arrays
                            if (typeof fieldValue === 'object') {
                              if (Array.isArray(fieldValue) && fieldValue.length === 0) return null;
                              if (!Array.isArray(fieldValue) && Object.keys(fieldValue).length === 0) return null;
                            }
                            
                            return (
                              <div key={fieldName} style={{
                                display: 'flex',
                                padding: '12px',
                                background: '#f8f9fa',
                                borderRadius: '6px',
                                borderLeft: `4px solid ${domainInfo.color}`,
                                minHeight: '50px',
                                alignItems: 'flex-start',
                                flexDirection: window.innerWidth < 768 ? 'column' : 'row',
                                gap: '12px'
                              }}>
                                {/* Colonna Dominio Semantico - SOLO ICONA */}
                                <div 
                                  style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    minWidth: '60px',
                                    width: '60px',
                                    height: '40px',
                                    background: domainInfo.color,
                                    color: 'white',
                                    borderRadius: '8px',
                                    fontSize: '20px',
                                    flexShrink: 0,
                                    cursor: 'help'
                                  }}
                                  title={domainInfo.domain}
                                >
                                  {domainInfo.icon}
                                </div>
                                
                                {/* Colonna Campo */}
                                <div style={{
                                  fontWeight: '600',
                                  color: '#2c3e50',
                                  width: window.innerWidth < 768 ? '100%' : '35%',
                                  minWidth: window.innerWidth < 768 ? 'auto' : '200px',
                                  lineHeight: '1.4',
                                  wordWrap: 'break-word'
                                }}>{fieldName}:</div>
                                
                                {/* Colonna Valore */}
                                <div style={{
                                  fontFamily: 'Monaco, Menlo, Ubuntu Mono, monospace',
                                  color: '#1a73e8',
                                  fontWeight: '500',
                                  flex: '1',
                                  lineHeight: '1.4',
                                  wordWrap: 'break-word',
                                  background: 'white',
                                  padding: '8px 12px',
                                  borderRadius: '4px',
                                  border: '1px solid #e0e0e0'
                                }}>{fieldValue}</div>
                              </div>
                            );
                          }).filter(Boolean)}
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="error-display">
                    <h4>Errore di Parsing</h4>
                    <p><strong>Stringa:</strong> {currentString.euring_string}</p>
                    <p><strong>Errore:</strong> {currentString.error}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Navigation buttons SOTTO la tabella */}
          {strings.length > 1 && (
            <div className="string-navigation">
              <div className="navigation-header">
                <h3>Navigazione Stringhe ({strings.length} caricate)</h3>
                {totalPages > 1 && (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '15px',
                    marginTop: '10px'
                  }}>
                    <span style={{ fontSize: '14px', color: '#6c757d' }}>
                      Pagina {currentPage + 1} di {totalPages} (stringhe {startIndex + 1}-{endIndex})
                    </span>
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <button
                        onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                        disabled={currentPage === 0}
                        style={{
                          padding: '6px 12px',
                          background: currentPage === 0 ? '#e9ecef' : '#6c757d',
                          color: currentPage === 0 ? '#6c757d' : 'white',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: currentPage === 0 ? 'not-allowed' : 'pointer'
                        }}
                      >
                        ← 50 Prec.
                      </button>
                      <button
                        onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                        disabled={currentPage === totalPages - 1}
                        style={{
                          padding: '6px 12px',
                          background: currentPage === totalPages - 1 ? '#e9ecef' : '#6c757d',
                          color: currentPage === totalPages - 1 ? '#6c757d' : 'white',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: currentPage === totalPages - 1 ? 'not-allowed' : 'pointer'
                        }}
                      >
                        50 Succ. →
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <div className="navigation-buttons">
                {currentPageStrings.map((str, pageIndex) => {
                  const globalIndex = startIndex + pageIndex;
                  const info = getStringInfo(str);
                  
                  // Formato esatto richiesto: OSSERVATORIO ANELLO (SPECIE RIPORTATA) "catturato il " GIORNO/MESE/ANNO "nelle coordinate " LATITUDINE "-" LONGITUDINE
                  let buttonText = '';
                  
                  // Costruisci il testo seguendo il formato esatto
                  if (info.osservatorio !== 'N/A') {
                    buttonText += info.osservatorio;
                  }
                  
                  if (info.anello !== 'N/A') {
                    if (buttonText) buttonText += ' ';
                    buttonText += info.anello;
                  }
                  
                  if (info.specieRiportata !== 'N/A') {
                    if (buttonText) buttonText += ' ';
                    buttonText += `(${info.specieRiportata})`;
                  }
                  
                  if (info.giorno !== 'N/A' && info.mese !== 'N/A' && info.anno !== 'N/A') {
                    if (buttonText) buttonText += ' ';
                    buttonText += `catturato il ${info.giorno}/${info.mese}/${info.anno}`;
                  }
                  
                  if (info.latitudine !== 'N/A' && info.longitudine !== 'N/A') {
                    if (buttonText) buttonText += ' ';
                    buttonText += `nelle coordinate ${info.latitudine}|${info.longitudine}`;
                  }
                  
                  // Fallback se non abbiamo nessuna informazione utile
                  if (buttonText === '') {
                    buttonText = `Stringa ${globalIndex + 1}`;
                  }
                  
                  return (
                    <button
                      key={globalIndex}
                      onClick={() => changeCurrentIndex(globalIndex)}
                      className={`nav-button ${globalIndex === currentIndex ? 'active' : ''} ${str.success ? 'success' : 'error'}`}
                      title={`${str.euring_string}\n\nDettagli:\n• Osservatorio: ${info.osservatorio}\n• Anello: ${info.anello}\n• Specie riportata: ${info.specieRiportata}\n• Data: ${info.giorno}/${info.mese}/${info.anno}\n• Coordinate: ${info.latitudine}, ${info.longitudine}`}
                    >
                      <div className="nav-button-number">#{globalIndex + 1}</div>
                      <div className="nav-button-text">{buttonText}</div>
                    </button>
                  );
                })}
              </div>
              
              {/* Page Navigation - Navigate through 50-record pages */}
              {totalPages > 1 && (
                <div className="page-navigation-bottom">
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '20px',
                    marginTop: '20px',
                    padding: '15px',
                    background: '#f8f9fa',
                    border: '1px solid #dee2e6',
                    borderRadius: '8px'
                  }}>
                    <button
                      onClick={() => {
                        const newPage = Math.max(0, currentPage - 1);
                        setCurrentPage(newPage);
                        // Set current index to first item of new page
                        setCurrentIndex(newPage * BUTTONS_PER_PAGE);
                      }}
                      disabled={currentPage === 0}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '12px 20px',
                        background: currentPage === 0 ? '#e9ecef' : '#28a745',
                        color: currentPage === 0 ? '#6c757d' : 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: currentPage === 0 ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <span style={{ fontSize: '16px' }}>←</span>
                      50 Precedenti
                    </button>

                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '10px 20px',
                      background: 'white',
                      border: '2px solid #28a745',
                      borderRadius: '25px',
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#28a745'
                    }}>
                      <span style={{ fontSize: '14px', color: '#6c757d' }}>Pagina</span>
                      <span style={{ fontSize: '18px', minWidth: '80px', textAlign: 'center' }}>
                        {currentPage + 1} / {totalPages}
                      </span>
                      <span style={{ fontSize: '12px', color: '#6c757d' }}>
                        ({startIndex + 1}-{endIndex} di {strings.length})
                      </span>
                    </div>

                    <button
                      onClick={() => {
                        const newPage = Math.min(totalPages - 1, currentPage + 1);
                        setCurrentPage(newPage);
                        // Set current index to first item of new page
                        setCurrentIndex(newPage * BUTTONS_PER_PAGE);
                      }}
                      disabled={currentPage === totalPages - 1}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '12px 20px',
                        background: currentPage === totalPages - 1 ? '#e9ecef' : '#28a745',
                        color: currentPage === totalPages - 1 ? '#6c757d' : 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: currentPage === totalPages - 1 ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      50 Successivi
                      <span style={{ fontSize: '16px' }}>→</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default StringNavigator;
