import { useState } from 'react';
import { EuringAPI } from '../services/api';
import './RecognitionPanel.css';

const RecognitionPanel = () => {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      setError('Inserisci un codice EURING da analizzare');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await EuringAPI.recognize({
        euring_string: inputText.trim(),
        include_analysis: false
      });

      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Riconoscimento fallito');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="recognition-panel">
      <div className="panel-header">
        <h2>🔍 Riconoscimento Codici EURING</h2>
        <p>Inserisci il codice EURING da analizzare</p>
      </div>

      <form onSubmit={handleSubmit} className="recognition-form">
        <div className="form-group">
          <label htmlFor="input-text">Stringa EURING:</label>
          <textarea
            id="input-text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Esempio: 5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750"
            rows={4}
            className={loading ? 'loading' : ''}
          />
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? '🔄 Analizzando...' : '🔍 Analizza Codice'}
          </button>
        </div>
      </form>

      <div className="examples-section">
        <h3>📋 Esempi:</h3>
        <div className="examples-grid">
          <button 
            onClick={() => setInputText('5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750')}
            className="example-btn"
            type="button"
          >
            EURING 1966 (spazi)
          </button>
          <button 
            onClick={() => setInputText('05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------')}
            className="example-btn"
            type="button"
          >
            EURING 1979 (fisso)
          </button>
          <button 
            onClick={() => setInputText('IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086')}
            className="example-btn"
            type="button"
          >
            EURING 2000 (codificato)
          </button>
          <button 
            onClick={() => setInputText('05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2')}
            className="example-btn"
            type="button"
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

      {result && (
        <div className="results-section">
          <h3>📊 Risultato Riconoscimento</h3>
          
          <div className="result-card success">
            <div className="result-content">
              <div className="original-string">
                <strong>Stringa originale:</strong>
                <code>{result.euring_string}</code>
              </div>

              {result.success ? (
                <div className="recognition-info">
                  <div className="info-item">
                    <span className="label">Versione:</span>
                    <span className="value version-badge">
                      {EuringAPI.getVersionDisplayName(result.version || 'sconosciuta')}
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
                </div>
              ) : (
                <div className="error-info">
                  <strong>Errore:</strong> {result.error}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecognitionPanel;
