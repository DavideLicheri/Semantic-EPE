/**
 * Login Component for ECES
 */
import React, { useState } from 'react';
import { authService, LoginRequest } from '../services/auth';
import './Login.css';

interface LoginProps {
  onLoginSuccess: () => void;
  onShowRegister?: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess, onShowRegister }) => {
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
      setError(err instanceof Error ? err.message : 'Credenziali non valide');
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
        <div className="login-header">
          <img 
            src="/images/epeLogo.jpg" 
            alt="EPE Logo" 
            className="login-logo"
          />
          <h1>ECES</h1>
          <h2>Sistema Evoluzione Codici EURING</h2>
          <p className="login-subtitle">ISPRA - DG SINA</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Nome Utente</label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Nome utente"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Password"
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
                Accesso in corso...
              </>
            ) : (
              'Accedi'
            )}
          </button>
        </form>

        <div className="login-footer">
          <p>🔒 Accesso riservato al personale ISPRA</p>
          <p>Sistema interno - Rete ISPRA</p>
          
          {onShowRegister && (
            <div className="register-link">
              <p>Non hai un account?</p>
              <button 
                onClick={onShowRegister}
                className="register-button-link"
                disabled={loading}
              >
                Registrati
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};