import { useState, useEffect } from 'react';
import { EuringAPI } from '../services/api';
import { ConversionResponse } from '../types/api-types';
import './ConversionPanel.css';

interface ConversionResult extends ConversionResponse {
  original_string: string;
}

const ConversionPanel = () => {
  const [inputText, setInputText] = useState('');
  const [sourceVersion, setSourceVersion] = useState('1966');
  const [targetVersion, setTargetVersion] = useState('2020');
  const [useAutoDetect, setUseAutoDetect] = useState(true);
  const [useSemantic, setUseSemantic] = useState(true);
  const [batchMode, setBatchMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ConversionResult[]>([]);
  const [error, setError] = useState<string>('');
  // const [versions, setVersions] = useState<VersionInfo[]>([]);

  // Load available versions on component mount
  useEffect(() => {
    const loadVersions = async () => {
      try {
        await EuringAPI.getVersions();
        // setVersions(response.supported_versions);
      } catch (err) {
        console.error('Failed to load versions:', err);
      }
    };
    
    loadVersions();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      setError('Inserisci almeno una stringa EURING');
      return;
    }

    if (!useAutoDetect && sourceVersion === targetVersion) {
      setError('La versione sorgente e quella target devono essere diverse');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      if (batchMode) {
        // Batch conversion
        const strings = EuringAPI.parseEuringStrings(inputText);
        
        if (strings.length === 0) {
          throw new Error('Nessuna stringa EURING valida trovata');
        }

        if (strings.length > 50) {
          throw new Error('Massimo 50 stringhe per batch conversion');
        }

        const conversions = await Promise.all(
          strings.map(async (euringString) => {
            let actualSourceVersion = sourceVersion;
            
            // Auto-detect source version if enabled
            if (useAutoDetect) {
              try {
                const recognition = await EuringAPI.recognize({
                  euring_string: euringString,
                  include_analysis: false
                });
                
                if (recognition.success && recognition.version) {
                  // Extract version number from response (e.g., "euring_1966" -> "1966")
                  const versionMatch = recognition.version.match(/(\d{4})/);
                  if (versionMatch) {
                    actualSourceVersion = versionMatch[1];
                  }
                }
              } catch (recognitionError) {
                console.warn('Auto-detection failed for string:', euringString);
              }
            }

            return {
              euring_string: euringString,
              source_version: actualSourceVersion,
              target_version: targetVersion,
              use_semantic: useSemantic
            };
          })
        );

        const response = await EuringAPI.batchConvert({
          conversions,
          max_concurrent: 10
        });

        if (response.success) {
          const resultsWithOriginal = response.results.map((result, index) => ({
            ...result,
            original_string: strings[index] || result.source_version
          }));
          setResults(resultsWithOriginal);
        } else {
          throw new Error(response.error || 'Batch conversion failed');
        }
      } else {
        // Single conversion
        const validation = EuringAPI.validateEuringString(inputText.trim());
        if (!validation.valid) {
          throw new Error(validation.message);
        }

        let actualSourceVersion = sourceVersion;
        
        // Auto-detect source version if enabled
        if (useAutoDetect) {
          try {
            const recognition = await EuringAPI.recognize({
              euring_string: inputText.trim(),
              include_analysis: false
            });
            
            if (recognition.success && recognition.version) {
              // Extract version number from response
              const versionMatch = recognition.version.match(/(\d{4})/);
              if (versionMatch) {
                actualSourceVersion = versionMatch[1];
              }
            }
          } catch (recognitionError) {
            console.warn('Auto-detection failed, using manual selection');
          }
        }

        const response = await EuringAPI.convert({
          euring_string: inputText.trim(),
          source_version: actualSourceVersion,
          target_version: targetVersion,
          use_semantic: useSemantic
        });

        setResults([{
          ...response,
          original_string: inputText.trim()
        }]);
      }
    } catch (err: any) {
      setError(err.message || 'Errore durante la conversione');
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setError('');
  };

  const loadExample = (example: string, source: string, target: string) => {
    setInputText(example);
    setSourceVersion(source);
    setTargetVersion(target);
    setBatchMode(false);
    setUseAutoDetect(false);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      // Could add a toast notification here
    });
  };

  return (
    <div className="conversion-panel">
      <div className="panel-header">
        <h2>🔄 Conversione Codici EURING</h2>
        <p>Converti codici EURING tra diverse versioni mantenendo l'integrità semantica</p>
      </div>

      <form onSubmit={handleSubmit} className="conversion-form">
        <div className="form-group">
          <label htmlFor="input-text">
            {batchMode ? 'Stringhe EURING (una per riga):' : 'Stringa EURING:'}
          </label>
          <textarea
            id="input-text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={batchMode 
              ? "Inserisci una stringa EURING per riga...\n\nEsempio:\n5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750\n05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------"
              : "Inserisci una stringa EURING da convertire..."
            }
            rows={batchMode ? 6 : 3}
            className={loading ? 'loading' : ''}
          />
        </div>

        <div className="version-selection">
          <div className="version-group">
            <label>Versione sorgente:</label>
            <select
              value={sourceVersion}
              onChange={(e) => setSourceVersion(e.target.value)}
              disabled={useAutoDetect}
            >
              <option value="1966">EURING 1966</option>
              <option value="1979">EURING 1979</option>
              <option value="2000">EURING 2000</option>
              <option value="2020">EURING 2020</option>
            </select>
          </div>

          <div className="arrow-icon">➡️</div>

          <div className="version-group">
            <label>Versione target:</label>
            <select
              value={targetVersion}
              onChange={(e) => setTargetVersion(e.target.value)}
            >
              <option value="1966">EURING 1966</option>
              <option value="1979">EURING 1979</option>
              <option value="2000">EURING 2000</option>
              <option value="2020">EURING 2020</option>
            </select>
          </div>
        </div>

        <div className="form-options">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={useAutoDetect}
              onChange={(e) => setUseAutoDetect(e.target.checked)}
            />
            Rileva automaticamente versione sorgente
          </label>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={useSemantic}
              onChange={(e) => setUseSemantic(e.target.checked)}
            />
            Usa conversione semantica (consigliato)
          </label>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={batchMode}
              onChange={(e) => setBatchMode(e.target.checked)}
            />
            Modalità batch (più stringhe)
          </label>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? '🔄 Convertendo...' : '🔄 Converti'}
          </button>
          
          {results.length > 0 && (
            <button type="button" onClick={clearResults} className="btn-secondary">
              🗑️ Pulisci risultati
            </button>
          )}
        </div>
      </form>

      <div className="examples-section">
        <h3>📋 Esempi di Conversione:</h3>
        <div className="examples-grid">
          <button 
            onClick={() => loadExample(
              '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750',
              '1966',
              '2020'
            )}
            className="example-btn"
          >
            1966 → 2020
          </button>
          <button 
            onClick={() => loadExample(
              '05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2',
              '2020',
              '1966'
            )}
            className="example-btn"
          >
            2020 → 1966
          </button>
          <button 
            onClick={() => loadExample(
              '05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------',
              '1979',
              '2020'
            )}
            className="example-btn"
          >
            1979 → 2020
          </button>
          <button 
            onClick={() => loadExample(
              'IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086',
              '2000',
              '2020'
            )}
            className="example-btn"
          >
            2000 → 2020
          </button>
        </div>
      </div>

      {error && (
        <div className="error">
          ❌ {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="results-section">
          <h3>🎯 Risultati della Conversione</h3>
          
          <div className="results-summary">
            <span className="summary-item">
              📝 Conversioni richieste: <strong>{results.length}</strong>
            </span>
            <span className="summary-item">
              ✅ Riuscite: <strong>{results.filter(r => r.success).length}</strong>
            </span>
            <span className="summary-item">
              ❌ Fallite: <strong>{results.filter(r => !r.success).length}</strong>
            </span>
          </div>

          <div className="results-list">
            {results.map((result, index) => (
              <div key={index} className={`result-card ${result.success ? 'success' : 'error'}`}>
                <div className="result-header">
                  <span className="result-index">#{index + 1}</span>
                  <div className="conversion-path">
                    <span className="version-badge source">
                      {EuringAPI.getVersionDisplayName(result.source_version)}
                    </span>
                    <span className="arrow">→</span>
                    <span className="version-badge target">
                      {EuringAPI.getVersionDisplayName(result.target_version)}
                    </span>
                  </div>
                  <span className="result-status">
                    {result.success ? '✅' : '❌'}
                  </span>
                </div>

                <div className="result-content">
                  <div className="string-comparison">
                    <div className="string-item">
                      <strong>Originale:</strong>
                      <div className="string-display">
                        <code>{result.original_string}</code>
                        <button 
                          onClick={() => copyToClipboard(result.original_string)}
                          className="copy-btn"
                          title="Copia negli appunti"
                        >
                          📋
                        </button>
                      </div>
                    </div>

                    {result.success && result.converted_string && (
                      <div className="string-item">
                        <strong>Convertito:</strong>
                        <div className="string-display">
                          <code className="converted">{result.converted_string}</code>
                          <button 
                            onClick={() => copyToClipboard(result.converted_string || '')}
                            className="copy-btn"
                            title="Copia negli appunti"
                          >
                            📋
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  {result.success ? (
                    <>
                      <div className="conversion-info">
                        <div className="info-item">
                          <span className="label">Metodo:</span>
                          <span className="value method-badge">
                            {result.conversion_method || 'semantic'}
                          </span>
                        </div>
                        
                        <div className="info-item">
                          <span className="label">Tempo:</span>
                          <span className="value">{EuringAPI.formatProcessingTime(result.processing_time_ms)}</span>
                        </div>
                      </div>

                      {result.conversion_notes && result.conversion_notes.length > 0 && (
                        <div className="notes-section">
                          <h4>📝 Note di Conversione:</h4>
                          <ul className="notes-list">
                            {result.conversion_notes.map((note, noteIndex) => (
                              <li key={noteIndex}>{note}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="error-info">
                      <strong>Errore:</strong> {result.error}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConversionPanel;