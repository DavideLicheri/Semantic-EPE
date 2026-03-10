import React, { useState } from 'react';
import { authService, User, PasswordChangeRequest } from '../services/auth';
import './UserProfile.css';

interface UserProfileProps {
  currentUser: User;
  onClose: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ currentUser, onClose }) => {
  const [passwordData, setPasswordData] = useState<PasswordChangeRequest>({
    current_password: '',
    new_password: ''
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [showPasswords, setShowPasswords] = useState(false);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!passwordData.current_password || !passwordData.new_password) {
      setMessage({ type: 'error', text: 'Tutti i campi sono obbligatori' });
      return;
    }

    if (passwordData.new_password !== confirmPassword) {
      setMessage({ type: 'error', text: 'Le nuove password non coincidono' });
      return;
    }

    if (passwordData.new_password.length < 4) {
      setMessage({ type: 'error', text: 'La nuova password deve essere di almeno 4 caratteri' });
      return;
    }

    if (passwordData.current_password === passwordData.new_password) {
      setMessage({ type: 'error', text: 'La nuova password deve essere diversa da quella attuale' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await authService.changePassword(passwordData);
      
      if (response.success) {
        setMessage({ type: 'success', text: response.message });
        // Reset form
        setPasswordData({ current_password: '', new_password: '' });
        setConfirmPassword('');
        
        // Auto-close after success
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        setMessage({ type: 'error', text: response.message });
      }
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Errore durante il cambio password' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="user-profile-overlay">
      <div className="user-profile-modal">
        <div className="user-profile-header">
          <h2>👤 Profilo Utente</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="user-profile-content">
          {/* User Information */}
          <div className="user-info-section">
            <h3>Informazioni Utente</h3>
            <div className="user-info-grid">
              <div className="info-item">
                <label>Nome Completo:</label>
                <span>{currentUser.full_name}</span>
              </div>
              <div className="info-item">
                <label>Username:</label>
                <span>{currentUser.username}</span>
              </div>
              <div className="info-item">
                <label>Email:</label>
                <span>{currentUser.email}</span>
              </div>
              <div className="info-item">
                <label>Ruolo:</label>
                <span className={`role-badge role-${currentUser.role}`}>
                  {currentUser.role === 'super_admin' && '👑 Super Admin'}
                  {currentUser.role === 'admin' && '🔧 Admin'}
                  {currentUser.role === 'user' && '👤 User'}
                  {currentUser.role === 'viewer' && '👁️ Viewer'}
                </span>
              </div>
              {currentUser.department && (
                <div className="info-item">
                  <label>Dipartimento:</label>
                  <span>{currentUser.department}</span>
                </div>
              )}
              <div className="info-item">
                <label>Registrato:</label>
                <span>{new Date(currentUser.created_at).toLocaleDateString('it-IT')}</span>
              </div>
              {currentUser.last_login && (
                <div className="info-item">
                  <label>Ultimo Accesso:</label>
                  <span>{new Date(currentUser.last_login).toLocaleString('it-IT')}</span>
                </div>
              )}
            </div>
          </div>

          {/* Password Change Form */}
          <div className="password-change-section">
            <h3>🔐 Cambia Password</h3>
            
            {message && (
              <div className={`message ${message.type}`}>
                {message.text}
              </div>
            )}

            <form onSubmit={handlePasswordChange} className="password-form">
              <div className="form-group">
                <label htmlFor="current_password">Password Attuale:</label>
                <div className="password-input-group">
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    id="current_password"
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                    placeholder="Inserisci la password attuale"
                    disabled={loading}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="new_password">Nuova Password:</label>
                <div className="password-input-group">
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    id="new_password"
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                    placeholder="Inserisci la nuova password (min. 4 caratteri)"
                    disabled={loading}
                    minLength={4}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="confirm_password">Conferma Nuova Password:</label>
                <div className="password-input-group">
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    id="confirm_password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Conferma la nuova password"
                    disabled={loading}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={showPasswords}
                    onChange={(e) => setShowPasswords(e.target.checked)}
                  />
                  Mostra password
                </label>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={onClose}
                  className="cancel-button"
                  disabled={loading}
                >
                  Annulla
                </button>
                <button
                  type="submit"
                  className="submit-button"
                  disabled={loading}
                >
                  {loading ? 'Cambiando...' : 'Cambia Password'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};