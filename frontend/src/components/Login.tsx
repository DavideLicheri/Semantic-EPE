import React, { useState } from 'react';
import { authService, LoginRequest } from '../services/auth';
import { useTranslation } from '../hooks/useTranslation';
import { i18n } from '../i18n';
import './Login.css';

interface LoginProps {
  onLoginSuccess: () => void;
  onShowRegister?: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess, onShowRegister }) => {
  const { t } = useTranslation();
  const [credentials, setCredentials] = useState<LoginRequest>({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await authService.login(credentials);
      onLoginSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : t('login.error.invalid_credentials'));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-lang-toggle">
          <button
            className="lang-toggle"
            onClick={() => i18n.setLanguage(i18n.getLanguage() === 'en' ? 'it' : 'en')}
          >
            {i18n.getLanguage() === 'en' ? t('lang.switch_to_it') : t('lang.switch_to_en')}
          </button>
        </div>

        <div className="login-header">
          <img
            src="/images/epeLogo.jpg"
            alt="EPE Logo"
            className="login-logo"
          />
          <h1>ECES</h1>
          <h2>{t('login.title_full')}</h2>
          <p className="login-subtitle">{t('login.institution')}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">{t('login.username.label')}</label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder={t('login.username.placeholder')}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">{t('login.password.label')}</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder={t('login.password.placeholder')}
            />
          </div>

          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={loading || !credentials.username || !credentials.password}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                {t('login.loading')}
              </>
            ) : (
              t('login.button')
            )}
          </button>
        </form>

        <div className="login-footer">
          <p>{t('login.footer.restricted')}</p>
          <p>{t('login.footer.internal')}</p>

          {onShowRegister && (
            <div className="register-link">
              <p>{t('login.register.text')}</p>
              <button
                onClick={onShowRegister}
                className="register-button-link"
                disabled={loading}
              >
                {t('login.register.link')}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
