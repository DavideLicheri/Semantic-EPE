/**
 * Registration Component for ECES
 */
import React, { useState } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import './Register.css';

interface RegistrationData {
  username: string;
  email: string;
  full_name: string;
  password: string;
  confirmPassword: string;
  department?: string;
}

interface RegisterProps {
  onBackToLogin: () => void;
}

export const Register: React.FC<RegisterProps> = ({ onBackToLogin }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState<RegistrationData>({
    username: '',
    email: '',
    full_name: '',
    password: '',
    confirmPassword: '',
    department: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError(t('register.error.password_mismatch'));
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError(t('register.error.password_short'));
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          password: formData.password,
          department: formData.department || 'ISPRA'
        }),
      });

      const result = await response.json();

      if (result.success) {
        setSuccess(true);
      } else {
        setError(result.message || t('register.error.generic'));
      }
    } catch (err) {
      setError(t('register.error.connection'));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (success) {
    return (
      <div className="register-container">
        <div className="register-card">
          <div className="register-header">
            <img
              src="/src/assets/images/epeLogo.jpg"
              alt="EPE Logo"
              className="register-logo"
            />
            <h1>{t('register.success.title')}</h1>
            <h2>{t('register.success.subtitle')}</h2>
          </div>

          <div className="success-message">
            <div className="success-icon">✅</div>
            <h3>{t('register.success.welcome')}</h3>
            <p>{t('register.success.completed')}</p>
            <p>{t('register.success.readonly')}</p>
            <p>{t('register.success.admin_notified')}</p>
          </div>

          <button
            onClick={onBackToLogin}
            className="back-to-login-button"
          >
            {t('register.success.login_button')}
          </button>

          <div className="register-footer">
            <p>{t('register.success.footer')}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <img
            src="/src/assets/images/epeLogo.jpg"
            alt="EPE Logo"
            className="register-logo"
          />
          <h1>{t('register.form.title')}</h1>
          <h2>{t('register.success.subtitle')}</h2>
          <p className="register-subtitle">{t('register.form.subtitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="full_name">{t('register.fullname.label')}</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder={t('register.fullname.placeholder')}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">{t('register.email_ispra.label')}</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder={t('register.email_ispra.placeholder')}
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">{t('register.username.label')}</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder={t('register.username.placeholder')}
              pattern="[a-zA-Z0-9_-]+"
              title={t('register.username.title')}
            />
          </div>

          <div className="form-group">
            <label htmlFor="department">{t('register.department.label')}</label>
            <select
              id="department"
              name="department"
              value={formData.department}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="">{t('register.department.select')}</option>
              <option value="ISPRA - DG SINA">ISPRA - DG SINA</option>
              <option value="ISPRA - DG AMB">ISPRA - DG AMB</option>
              <option value="ISPRA - DG GEO">ISPRA - DG GEO</option>
              <option value="ISPRA - DG MAR">ISPRA - DG MAR</option>
              <option value="ISPRA - Altro">ISPRA - Altro</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="password">{t('register.password.label2')}</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder={t('register.password.placeholder2')}
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">{t('register.confirm.label2')}</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder={t('register.confirm.placeholder2')}
            />
          </div>

          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
            </div>
          )}

          <button
            type="submit"
            className="register-button"
            disabled={loading || !formData.username || !formData.email || !formData.full_name || !formData.password || !formData.confirmPassword}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                {t('register.submitting')}
              </>
            ) : (
              t('register.submit')
            )}
          </button>
        </form>

        <div className="register-actions">
          <button
            onClick={onBackToLogin}
            className="back-link"
            disabled={loading}
          >
            {t('register.back_to_login')}
          </button>
        </div>

        <div className="register-footer">
          <p>{t('register.footer.restricted')}</p>
          <p>{t('register.footer.readonly')}</p>
          <p>{t('register.footer.admin')}</p>
        </div>
      </div>
    </div>
  );
};
