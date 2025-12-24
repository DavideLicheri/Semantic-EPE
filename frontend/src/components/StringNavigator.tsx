import React, { useState } from 'react';
import EuringAPI from '../services/api';
import SemanticDomainBadge from './SemanticDomainBadge';
import { getDomainClassName } from '../utils/semanticDomains';
import './StringNavigator.css';
import './SemanticDomains.css';

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

interface StringNavigatorProps {
  // Props opzionali per configurazione
}

const StringNavigator: React.FC<StringNavigatorProps> = () => {
  const [strings, setStrings] = useState<ParsedString[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [inputText, setInputText] = useState<string>('');
  const [uploadMode, setUploadMode] = useState<'single' | 'batch'>('single');

  const currentString = strings.length > 0 ? strings[currentIndex] : null;

  const handleSingleStringSubmit = async () => {
    if (!inputText.trim()) {
      setError('Inserisci una stringa EURING');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await EuringAPI.parseEuringString(inputText.trim());
      
      if (response.success) {
        const newString: ParsedString = {
          index: 0,
          success: response.success,
          euring_string: response.euring_string,
          detected_version: response.detected_version,
          confidence: response.confidence,
          parsed_fields: response.parsed_fields,
          epe_compatible: response.epe_compatible,
          field_count: response.field_count,
          error: response.error
        };
        
        setStrings([newString]);
        setCurrentIndex(0);
        setInputText('');
      } else {
        setError(response.error || 'Errore nel parsing della stringa');
      }
    } catch (err: any) {
      setError(err.message || 'Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  const handleBatchUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const text = await file.text();
      const lines = text.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);

      if (lines.length === 0) {
        setError('Il file non contiene stringhe EURING valide');
        return;
      }

      if (lines.length > 1000) {
        setError('Massimo 1000 stringhe per file');
        return;
      }

      const response = await EuringAPI.parseEuringStringsBatch(lines);
      
      if (response.success) {
        setStrings(response.results);
        setCurrentIndex(0);
      } else {
        setError(response.error || 'Errore nel parsing batch');
      }
    } catch (err: any) {
      setError(err.message || 'Errore nel caricamento del file');
    } finally {
      setLoading(false);
    }
  };

  const handleTextAreaBatch = async () => {
    if (!inputText.trim()) {
      setError('Inserisci le stringhe EURING (una per riga)');
      return;
    }

    const lines = inputText.split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);

    if (lines.length === 0) {
      setError('Nessuna stringa EURING valida trovata');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await EuringAPI.parseEuringStringsBatch(lines);
      
      if (response.success) {
        setStrings(response.results);
        setCurrentIndex(0);
        setInputText('');
      } else {
        setError(response.error || 'Errore nel parsing batch');
      }
    } catch (err: any) {
      setError(err.message || 'Errore nel parsing');
    } finally {
      setLoading(false);
    }
  };

  const navigateTo = (index: number) => {
    if (index >= 0 && index < strings.length) {
      setCurrentIndex(index);
    }
  };

  const navigatePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const navigateNext = () => {
    if (currentIndex < strings.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const formatFieldValue = (key: string, value: any): string => {
    if (value === null || value === undefined || value === '') return '-';
    if (typeof value === 'object') return JSON.stringify(value);
    
    const strValue = String(value).trim();
    if (!strValue) return '-';
    
    // Interpretazioni specifiche per migliorare la leggibilità
    switch (key) {
      case 'Sesso riportato':
      case 'Sesso concluso':
        if (strValue === 'M') return 'M (Maschio)';
        if (strValue === 'F') return 'F (Femmina)';
        if (strValue === 'U') return 'U (Sconosciuto)';
        return strValue;
        
      case 'Verifica dell\'anello metallico':
        if (strValue === '0') return '0 (Non pervenuto)';
        if (strValue === '1') return '1 (Pervenuto)';
        return strValue;
        
      case 'Circostanze presunte':
        if (strValue === '0') return '0 (No)';
        if (strValue === '1') return '1 (Sì)';
        return strValue;
        
      case 'Giorno':
      case 'Mese':
        if (strValue === '00') return '00 (Non specificato)';
        return strValue;
        
      case 'Anno':
        if (strValue === '0000') return '0000 (Non specificato)';
        return strValue;
        
      case 'Ora':
        if (strValue === '0000') return '0000 (Non specificata)';
        if (strValue.length === 4) {
          const hours = strValue.substring(0, 2);
          const minutes = strValue.substring(2, 4);
          return `${hours}:${minutes}`;
        }
        return strValue;
        
      default:
        return strValue;
    }
  };

  const getFieldDescription = (key: string): string => {
    // Le descrizioni sono già in italiano dal parser EPE
    // Aggiungiamo solo alcune note esplicative per campi complessi
    const additionalNotes: Record<string, string> = {
      'Osservatorio': 'Codice identificativo dell\'osservatorio',
      'Anello': 'Numero identificativo dell\'anello (10 caratteri)',
      'Specie riportata': 'Codice specie come riportato',
      'Specie conclusa': 'Codice specie dopo verifica',
      'Latitudine': 'Coordinate geografiche (formato decimale)',
      'Longitudine': 'Coordinate geografiche (formato decimale)',
      'Distanza': 'Distanza in chilometri',
      'Direzione': 'Direzione in gradi (0-360)',
      'Tempo trascorso': 'Giorni trascorsi dall\'inanellamento'
    };
    
    return additionalNotes[key] || '';
  };

  const getFieldSemanticDomain = (fieldName: string): string | null => {
    // Mappa i nomi dei campi italiani ai domini semantici
    const fieldToDomain: Record<string, string> = {
      // Identification & Marking
      'Osservatorio': 'identification_marking',
      'Metodo di identificazione primaria': 'identification_marking',
      'Anello (10 caratteri)': 'identification_marking',
      'Verifica dell\'anello metallico': 'identification_marking',
      'Informazioni sull\'anello metallico': 'identification_marking',
      'Altri marcaggi': 'identification_marking',
      
      // Species
      'Specie riportata': 'species',
      'Specie conclusa': 'species',
      
      // Demographics
      'Sesso riportato': 'demographics',
      'Sesso concluso': 'demographics',
      'Età riportata': 'demographics',
      'Età conclusa': 'demographics',
      'Status': 'demographics',
      'Dimensione della covata': 'demographics',
      'Età dei pulcini': 'demographics',
      'Accuratezza età dei pulcini': 'demographics',
      
      // Temporal
      'Giorno': 'temporal',
      'Mese': 'temporal',
      'Anno': 'temporal',
      'Accuratezza data': 'temporal',
      'Ora': 'temporal',
      'Tempo trascorso': 'temporal',
      
      // Spatial
      'Codice area Euring': 'spatial',
      'Latitudine': 'spatial',
      'Longitudine': 'spatial',
      'Accuratezza coordinate': 'spatial',
      
      // Methodology
      'Manipolazione': 'methodology',
      'Traslocazione prima della cattura': 'methodology',
      'Metodo di cattura': 'methodology',
      'Richiamo': 'methodology',
      'Condizioni': 'methodology',
      'Circostanze': 'methodology',
      'Circostanze presunte': 'methodology',
      'Identificatore codice Euring': 'methodology',
      'Distanza': 'methodology',
      'Direzione': 'methodology'
    };
    
    return fieldToDomain[fieldName] || null;
  };

  return (
    <div className="string-navigator">
      <div className="navigator-header">
        <h2>🔍 Navigatore Stringhe EURING</h2>
        <p>Carica e naviga tra stringhe EURING per vedere la traduzione campo-valore</p>
      </div>

      {/* Input Section */}
      <div className="input-section">
        <div className="mode-selector">
          <button 
            className={`mode-button ${uploadMode === 'single' ? 'active' : ''}`}
            onClick={() => setUploadMode('single')}
          >
            📝 Stringa Singola
          </button>
          <button 
            className={`mode-button ${uploadMode === 'batch' ? 'active' : ''}`}
            onClick={() => setUploadMode('batch')}
          >
            📄 Caricamento Batch
          </button>
        </div>

        {uploadMode === 'single' ? (
          <div className="single-input">
            <div className="input-group">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Inserisci una stringa EURING..."
                className="string-input"
                onKeyPress={(e) => e.key === 'Enter' && handleSingleStringSubmit()}
              />
              <button 
                onClick={handleSingleStringSubmit}
                disabled={loading || !inputText.trim()}
                className="parse-button"
              >
                {loading ? 'Parsing...' : 'Analizza'}
              </button>
            </div>
          </div>
        ) : (
          <div className="batch-input">
            <div className="batch-options">
              <div className="file-upload">
                <label htmlFor="file-input" className="file-label">
                  📁 Carica File
                </label>
                <input
                  id="file-input"
                  type="file"
                  accept=".txt,.csv"
                  onChange={handleBatchUpload}
                  disabled={loading}
                />
              </div>
              <span className="or-separator">oppure</span>
              <div className="text-input">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Incolla stringhe EURING (una per riga)..."
                  className="batch-textarea"
                  rows={5}
                />
                <button 
                  onClick={handleTextAreaBatch}
                  disabled={loading || !inputText.trim()}
                  className="parse-button"
                >
                  {loading ? 'Parsing...' : 'Analizza Batch'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span className="error-icon">❌</span>
          {error}
        </div>
      )}

      {/* Navigation and Results */}
      {strings.length > 0 && (
        <div className="results-section">
          {/* Navigation Controls */}
          <div className="navigation-controls">
            <div className="nav-info">
              <span className="current-position">
                {currentIndex + 1} di {strings.length}
              </span>
              {strings.length > 1 && (
                <span className="nav-stats">
                  ({strings.filter(s => s.success).length} successi, {strings.filter(s => !s.success).length} errori)
                </span>
              )}
            </div>
            
            {strings.length > 1 && (
              <div className="nav-buttons">
                <button 
                  onClick={navigatePrevious}
                  disabled={currentIndex === 0}
                  className="nav-button"
                >
                  ← Precedente
                </button>
                <button 
                  onClick={navigateNext}
                  disabled={currentIndex === strings.length - 1}
                  className="nav-button"
                >
                  Successiva →
                </button>
              </div>
            )}
          </div>

          {/* Current String Display */}
          {currentString && (
            <div className="string-display">
              <div className="string-header">
                <div className="string-info">
                  <h3>Stringa EURING</h3>
                  <div className="string-meta">
                    <span className="string-text">{currentString.euring_string}</span>
                    <span className="string-length">({currentString.euring_string.length} caratteri)</span>
                  </div>
                </div>
                
                {currentString.success && (
                  <div className="detection-info">
                    <div className="version-badge">
                      {currentString.detected_version}
                    </div>
                    <div className="confidence-score">
                      Confidenza: {((currentString.confidence || 0) * 100).toFixed(1)}%
                    </div>
                    {currentString.epe_compatible && (
                      <div className="epe-badge">
                        EPE Compatible
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Field-Value Pairs */}
              {currentString.success && currentString.parsed_fields ? (
                <div className="field-value-pairs">
                  <h4>📋 Traduzione Campo-Valore ({currentString.field_count} campi)</h4>
                  <div className="fields-table-container">
                    <div className="fields-table">
                      <div className="table-header">
                        <div className="header-field">Campo</div>
                        <div className="header-domain">Dominio</div>
                        <div className="header-value">Valore</div>
                        <div className="header-description">Note</div>
                      </div>
                    
                    {Object.entries(currentString.parsed_fields)
                      .filter(([key]) => !key.startsWith('_'))
                      .map(([key, value]) => {
                        const formattedValue = formatFieldValue(key, value);
                        const description = getFieldDescription(key);
                        const domain = getFieldSemanticDomain(key);
                        const isEmpty = formattedValue === '-' || formattedValue === '';
                        const domainClassName = domain ? getDomainClassName(domain) : '';
                        
                        return (
                          <div key={key} className={`field-row ${isEmpty ? 'empty-field' : ''} ${domainClassName ? `string-field-${domainClassName}` : ''}`}>
                            <div className="field-name">{key}</div>
                            <div className="field-domain">
                              {domain && (
                                <SemanticDomainBadge 
                                  domain={domain} 
                                  variant="compact"
                                  showTooltip={true}
                                />
                              )}
                            </div>
                            <div className="field-value">{formattedValue}</div>
                            <div className="field-description">{description}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  
                  {/* Summary Info */}
                  <div className="parsing-summary">
                    <div className="summary-item">
                      <span className="summary-label">Versione rilevata:</span>
                      <span className="summary-value">{currentString.detected_version}</span>
                    </div>
                    <div className="summary-item">
                      <span className="summary-label">Confidenza:</span>
                      <span className="summary-value">{((currentString.confidence || 0) * 100).toFixed(1)}%</span>
                    </div>
                    {currentString.epe_compatible && (
                      <div className="summary-item">
                        <span className="summary-label">Compatibilità:</span>
                        <span className="summary-value epe-compatible">✓ EPE Compatible</span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="error-display">
                  <h4>❌ Errore nel Parsing</h4>
                  <p>{currentString.error}</p>
                </div>
              )}
            </div>
          )}

          {/* Quick Navigation for Multiple Strings */}
          {strings.length > 1 && (
            <div className="quick-navigation">
              <h4>Navigazione Rapida</h4>
              <div className="string-list">
                {strings.map((str, index) => (
                  <button
                    key={index}
                    onClick={() => navigateTo(index)}
                    className={`string-item ${index === currentIndex ? 'active' : ''} ${str.success ? 'success' : 'error'}`}
                  >
                    <span className="item-index">{index + 1}</span>
                    <span className="item-preview">
                      {str.euring_string.substring(0, 20)}...
                    </span>
                    <span className="item-status">
                      {str.success ? '✓' : '❌'}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StringNavigator;