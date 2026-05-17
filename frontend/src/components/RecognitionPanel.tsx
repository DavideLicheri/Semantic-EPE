import { useState } from 'react';
import { EuringAPI } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';
import './RecognitionPanel.css';

const RecognitionPanel = () => {
  const { t } = useTranslation();
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputText.trim()) {
      setError(t('recognition.error.empty'));
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
      setError(err.message || t('recognition.error.failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="recognition-panel">
      <div className="panel-header">
        <h2>{t('recognition.title')}</h2>
        <p>{t('recognition.subtitle')}</p>
      </div>

      <form onSubmit={handleSubmit} className="recognition-form">
        <div className="form-group">
          <label htmlFor="input-text">{t('recognition.input.label')}</label>
          <textarea
            id="input-text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750"
            rows={4}
            className={loading ? 'loading' : ''}
          />
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? t('recognition.button.analyzing') : t('recognition.button.analyze')}
          </button>
        </div>
      </form>

      <div className="examples-section">
        <h3>{t('recognition.examples.title')}</h3>
        <div className="examples-grid">
          <button
            onClick={() => setInputText('5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750')}
            className="example-btn"
            type="button"
          >
            {t('recognition.example.1966')}
          </button>
          <button
            onClick={() => setInputText('05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------')}
            className="example-btn"
            type="button"
          >
            {t('recognition.example.1979')}
          </button>
          <button
            onClick={() => setInputText('IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086')}
            className="example-btn"
            type="button"
          >
            {t('recognition.example.2000')}
          </button>
          <button
            onClick={() => setInputText('05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2')}
            className="example-btn"
            type="button"
          >
            {t('recognition.example.2020')}
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
          <h3>{t('recognition.result.recognize_title')}</h3>

          <div className="result-card success">
            <div className="result-content">
              <div className="original-string">
                <strong>{t('recognition.result.original_string')}</strong>
                <code>{result.euring_string}</code>
              </div>

              {result.success ? (
                <div className="recognition-info">
                  <div className="info-item">
                    <span className="label">{t('recognition.result.version')}</span>
                    <span className="value version-badge">
                      {EuringAPI.getVersionDisplayName(result.version || t('recognition.result.unknown'))}
                    </span>
                  </div>

                  <div className="info-item">
                    <span className="label">{t('recognition.result.confidence')}</span>
                    <span className="value confidence-badge">
                      {EuringAPI.formatConfidence(result.confidence)}
                    </span>
                  </div>

                  <div className="info-item">
                    <span className="label">{t('recognition.result.length')}</span>
                    <span className="value">{result.length} {t('recognition.result.chars')}</span>
                  </div>
                </div>
              ) : (
                <div className="error-info">
                  <strong>{t('recognition.result.error_label')}</strong> {result.error}
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
