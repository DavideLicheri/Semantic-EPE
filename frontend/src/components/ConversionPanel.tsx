import { useState } from 'react';
import { EuringAPI } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';
import './ConversionPanel.css';

const ConversionPanel = () => {
  const { t } = useTranslation();
  const [inputText, setInputText] = useState('');
  const [sourceVersion, setSourceVersion] = useState('1966');
  const [targetVersion, setTargetVersion] = useState('2020');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      setError(t('conversion.error.empty'));
      return;
    }

    if (sourceVersion === targetVersion) {
      setError(t('conversion.error.same'));
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await EuringAPI.convert({
        euring_string: inputText.trim(),
        source_version: sourceVersion,
        target_version: targetVersion,
        use_semantic: true
      });

      setResult(response);
    } catch (err: any) {
      setError(err.message || t('conversion.error.generic'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="conversion-panel">
      <div className="panel-header">
        <h2>{t('conversion.title')}</h2>
        <p>{t('conversion.subtitle')}</p>
      </div>

      <form onSubmit={handleSubmit} className="conversion-form">
        <div className="form-group">
          <label htmlFor="input-text">{t('conversion.input.label')}</label>
          <textarea
            id="input-text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={t('conversion.input.placeholder')}
            rows={3}
            className={loading ? 'loading' : ''}
          />
        </div>

        <div className="version-selection">
          <div className="version-group">
            <label>{t('conversion.source.label')}</label>
            <select
              value={sourceVersion}
              onChange={(e) => setSourceVersion(e.target.value)}
            >
              <option value="1966">{t('version.1966')}</option>
              <option value="1979">{t('version.1979')}</option>
              <option value="2000">{t('version.2000')}</option>
              <option value="2020">{t('version.2020')}</option>
            </select>
          </div>

          <div className="arrow-icon">➡️</div>

          <div className="version-group">
            <label>{t('conversion.target.label')}</label>
            <select
              value={targetVersion}
              onChange={(e) => setTargetVersion(e.target.value)}
            >
              <option value="1966">{t('version.1966')}</option>
              <option value="1979">{t('version.1979')}</option>
              <option value="2000">{t('version.2000')}</option>
              <option value="2020">{t('version.2020')}</option>
            </select>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? t('conversion.button.converting') : t('conversion.button.convert')}
          </button>
        </div>
      </form>

      <div className="examples-section">
        <h3>{t('conversion.examples.title')}</h3>
        <div className="examples-grid">
          <button 
            onClick={() => {
              setInputText('5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750');
              setSourceVersion('1966');
              setTargetVersion('2020');
            }}
            className="example-btn"
            type="button"
          >
            1966 → 2020
          </button>
          <button 
            onClick={() => {
              setInputText('05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2');
              setSourceVersion('2020');
              setTargetVersion('1966');
            }}
            className="example-btn"
            type="button"
          >
            2020 → 1966
          </button>
          <button 
            onClick={() => {
              setInputText('05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------');
              setSourceVersion('1979');
              setTargetVersion('2020');
            }}
            className="example-btn"
            type="button"
          >
            1979 → 2020
          </button>
          <button 
            onClick={() => {
              setInputText('IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086');
              setSourceVersion('2000');
              setTargetVersion('2020');
            }}
            className="example-btn"
            type="button"
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

      {result && (
        <div className="results-section">
          <h3>{t('conversion.result.title')}</h3>
          
          <div className="result-card success">
            <div className="result-content">
              <div className="string-comparison">
                <div className="string-item">
                  <strong>{t('conversion.result.original')}</strong>
                  <div className="string-display">
                    <code>{result.source_string || inputText}</code>
                  </div>
                </div>

                {result.success && result.converted_string && (
                  <div className="string-item">
                    <strong>{t('conversion.result.converted')}</strong>
                    <div className="string-display">
                      <code className="converted">{result.converted_string}</code>
                    </div>
                  </div>
                )}
              </div>

              {result.success ? (
                <div className="conversion-info">
                  <div className="info-item">
                    <span className="label">{t('conversion.result.method')}</span>
                    <span className="value method-badge">
                      {result.conversion_method || 'semantico'}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="error-info">
                  <strong>{t('conversion.result.error')}</strong> {result.error}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConversionPanel;
