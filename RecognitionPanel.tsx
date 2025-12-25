import { useState } from 'react';
import { EuringAPI } from '../services/api';
import { RecognitionResponse } from '../types/api-types';
import './RecognitionPanel.css';

interface RecognitionResult extends RecognitionResponse {
  original_string: string;
}

const RecognitionPanel = () => {
  const [inputText, setInputText] = useState('');
  const [includeAnalysis, setIncludeAnalysis] = useState(false);
  const [batchMode, setBatchMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<RecognitionResult[]>([]);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      setError('Inserisci almeno una stringa EURING');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      if (batchMode) {
        // Batch recognition
        const strings = EuringAPI.parseEuringStrings(inputText);
        
        if (strings.length === 0) {
          throw new Error('Nessuna stringa EURING valida trovata');
        }

        if (strings.length > 100) {
          throw new Error('Massimo 100 stringhe per batch');
        }

        const response = await EuringAPI.batchRecognize({
          euring_strings: strings,
          include_analysis: includeAnalysis,
          max_concurrent: 10
        });

        if (response.success) {
          const resultsWithOriginal = response.results.map((result, index) => ({
            ...result,
            original_string: strings[index] || result.euring_string
          }));
          setResults(resultsWithOriginal);
        } else {
          throw new Error(response.error || 'Batch recognition failed');
        }
      } else {
        // Single recognition
        const validation = EuringAPI.validateEuringString(inputText.trim());
        if (!validation.valid) {
          throw new Error(validation.message);
        }

        const response = await EuringAPI.recognize({
          euring_string: inputText.trim(),
          include_analysis: includeAnalysis
        });

        setResults([{
          ...response,
          original_string: inputText.trim()
        }]);
      }
    } catch (err: any) {
      setError(err.message || 'Errore durante il riconoscimento');
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setError('');
  };

  const loadExample = (example: string) => {
    setInputText(example);
    setBatchMode(false);
  };

  return (
    <div className="recognition-panel">
      <div className="panel-header">
        <h2>🔍 Riconoscimento Versione EURING</h2>
        <p>Identifica automaticamente la versione di uno o più codici EURING</p>
      </div>

      <form onSubmit={handleSubmit} className="recognition-form">
        <div className="form-group">
          <label htmlFor="input-text">
            {batchMode ? 'Stringhe EURING (una per riga):' : 'Stringa EURING:'}
          </label>
          <textarea
            id="input-text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={batchMode 
              ? "Inserisci una stringa EURING per riga...\n\nEsempio:\n5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750\n05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2"
              : "Inserisci una stringa EURING..."
            }
            rows={batchMode ? 8 : 4}
            className={loading ? 'loading' : ''}
          />
        </div>

        <div className="form-options">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={batchMode}
              onChange={(e) => setBatchMode(e.target.checked)}
            />
            Modalità batch (più stringhe)
          </label>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={includeAnalysis}
              onChange={(e) => setIncludeAnalysis(e.target.checked)}
            />
            Includi analisi dettagliata
          </label>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? '🔄 Analizzando...' : '🔍 Riconosci'}
          </button>
          
          {results.length > 0 && (
            <button type="button" onClick={clearResults} className="btn-secondary">
              🗑️ Pulisci risultati
            </button>
          )}
        </div>
      </form>

      <div className="examples-section">
        <h3>📋 Esempi:</h3>
        <div className="examples-grid">
          <button 
            onClick={() => loadExample('5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750')}
            className="example-btn"
          >
            EURING 1966 (spazi)
          </button>
          <button 
            onClick={() => loadExample('05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------')}
            className="example-btn"
          >
            EURING 1979 (fisso)
          </button>
          <button 
            onClick={() => loadExample('IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086')}
            className="example-btn"
          >
            EURING 2000 (codificato)
          </button>
          <button 
            onClick={() => loadExample('05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2')}
            className="example-btn"
          >
            EURING 2020 (pipe)
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
          <h3>📊 Risultati del Riconoscimento</h3>
          
          <div className="results-summary">
            <span className="summary-item">
              📝 Stringhe analizzate: <strong>{results.length}</strong>
            </span>
            <span className="summary-item">
              ✅ Riconosciute: <strong>{results.filter(r => r.success).length}</strong>
            </span>
            <span className="summary-item">
              ❌ Errori: <strong>{results.filter(r => !r.success).length}</strong>
            </span>
          </div>

          <div className="results-list">
            {results.map((result, index) => (
              <div key={index} className={`result-card ${result.success ? 'success' : 'error'}`}>
                <div className="result-header">
                  <span className="result-index">#{index + 1}</span>
                  <span className="result-status">
                    {result.success ? '✅' : '❌'}
                  </span>
                </div>

                <div className="result-content">
                  <div className="original-string">
                    <strong>Stringa originale:</strong>
                    <code>{result.original_string}</code>
                  </div>

                  {result.success ? (
                    <>
                      <div className="recognition-info">
                        <div className="info-item">
                          <span className="label">Versione:</span>
                          <span className="value version-badge">
                            {EuringAPI.getVersionDisplayName(result.version || 'unknown')}
                          </span>
                        </div>
                        
                        <div className="info-item">
                          <span className="label">Confidenza:</span>
                          <span className="value confidence-badge">
                            {EuringAPI.formatConfidence(result.confidence)}
                          </span>
                        </div>
                        
                        <div className="info-item">
                          <span className="label">Lunghezza:</span>
                          <span className="value">{result.length} caratteri</span>
                        </div>
                        
                        <div className="info-item">
                          <span className="label">Tempo:</span>
                          <span className="value">{EuringAPI.formatProcessingTime(result.processing_time_ms)}</span>
                        </div>
                      </div>

                      {includeAnalysis && result.discriminant_analysis && (
                        <div className="analysis-section">
                          <h4>🔬 Analisi Discriminanti:</h4>
                          <div className="analysis-grid">
                            {Object.entries(result.discriminant_analysis).map(([key, value]) => (
                              <div key={key} className="analysis-item">
                                <span className="analysis-key">{key}:</span>
                                <span className="analysis-value">{String(value)}</span>
                              </div>
                            ))}
                          </div>
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

export default RecognitionPanel;