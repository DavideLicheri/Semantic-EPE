/**
 * Registration Component for ECES
 */
import React, { useState } from 'react';
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
      setError('Le password non coincidono');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('La password deve essere di almeno 6 caratteri');
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
        setError(result.message || 'Errore durante la registrazione');
      }
    } catch (err) {
      setError('Errore di connessione. Riprova più tardi.');
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
            <h1>Registrazione Completata!</h1>
            <h2>ECES - EURING Code Evolution System</h2>
          </div>

          <div className="success-message">
            <div className="success-icon">✅</div>
            <h3>Benvenuto nel sistema ECES!</h3>
            <p>La tua registrazione è stata completata con successo.</p>
            <p>Hai accesso in <strong>sola lettura</strong> al sistema.</p>
            <p>L'amministratore è stato notificato e potrà modificare i tuoi permessi se necessario.</p>
          </div>

          <button 
            onClick={onBackToLogin}
            className="back-to-login-button"
          >
            Accedi al Sistema
          </button>

          <div className="register-footer">
            <p>🔒 Sistema interno ISPRA - DG SINA</p>
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
          <h1>Registrazione</h1>
          <h2>ECES - EURING Code Evolution System</h2>
          <p className="register-subtitle">ISPRA - DG SINA</p>
        </div>

        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="full_name">Nome Completo *</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Il tuo nome e cognome"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email ISPRA *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="nome.cognome@isprambiente.it"
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">Username *</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Il tuo username (senza spazi)"
              pattern="[a-zA-Z0-9_-]+"
              title="Solo lettere, numeri, underscore e trattini"
            />
          </div>

          <div className="form-group">
            <label htmlFor="department">Dipartimento</label>
            <select
              id="department"
              name="department"
              value={formData.department}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="">Seleziona dipartimento</option>
              <option value="ISPRA - DG SINA">ISPRA - DG SINA</option>
              <option value="ISPRA - DG AMB">ISPRA - DG AMB</option>
              <option value="ISPRA - DG GEO">ISPRA - DG GEO</option>
              <option value="ISPRA - DG MAR">ISPRA - DG MAR</option>
              <option value="ISPRA - Altro">ISPRA - Altro</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Almeno 6 caratteri"
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Conferma Password *</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Ripeti la password"
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
                Registrazione in corso...
              </>
            ) : (
              'Registrati al Sistema'
            )}
          </button>
        </form>

        <div className="register-actions">
          <button 
            onClick={onBackToLogin}
            className="back-link"
            disabled={loading}
          >
            ← Torna al Login
          </button>
        </div>

        <div className="register-footer">
          <p>🔒 Accesso riservato al personale ISPRA</p>
          <p>I nuovi utenti ricevono accesso in sola lettura</p>
          <p>L'amministratore può modificare i permessi dopo la registrazione</p>
        </div>
      </div>
    </div>
  );
};