import React, { useState } from 'react';
import { authService, User, PasswordChangeRequest } from '../services/auth';
import { useTranslation } from '../hooks/useTranslation';
import { i18n } from '../i18n';
import './UserProfile.css';

interface UserProfileProps {
  currentUser: User;
  onClose: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ currentUser, onClose }) => {
  const { t } = useTranslation();
  const [passwordData, setPasswordData] = useState<PasswordChangeRequest>({
    current_password: '',
    new_password: ''
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [showPasswords, setShowPasswords] = useState(false);

  const locale = i18n.getLanguage() === 'it' ? 'it-IT' : 'en-GB';

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!passwordData.current_password || !passwordData.new_password) {
      setMessage({ type: 'error', text: t('profile.error.all_fields') });
      return;
    }

    if (passwordData.new_password !== confirmPassword) {
      setMessage({ type: 'error', text: t('profile.error.no_match') });
      return;
    }

    if (passwordData.new_password.length < 4) {
      setMessage({ type: 'error', text: t('profile.error.too_short') });
      return;
    }

    if (passwordData.current_password === passwordData.new_password) {
      setMessage({ type: 'error', text: t('profile.error.same_password') });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await authService.changePassword(passwordData);

      if (response.success) {
        setMessage({ type: 'success', text: response.message });
        setPasswordData({ current_password: '', new_password: '' });
        setConfirmPassword('');

        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        setMessage({ type: 'error', text: response.message });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : t('profile.error.change_failed')
      });
    } finally {
      setLoading(false);
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'super_admin': return t('profile.role.super_admin');
      case 'admin': return t('profile.role.admin');
      case 'user': return t('profile.role.user');
      case 'viewer': return t('profile.role.viewer');
      default: return role;
    }
  };

  return (
    <div className="user-profile-overlay">
      <div className="user-profile-modal">
        <div className="user-profile-header">
          <h2>{t('profile.header')}</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="user-profile-content">
          <div className="user-info-section">
            <h3>{t('profile.info.title')}</h3>
            <div className="user-info-grid">
              <div className="info-item">
                <label>{t('profile.info.fullname')}</label>
                <span>{currentUser.full_name}</span>
              </div>
              <div className="info-item">
                <label>{t('profile.info.username')}</label>
                <span>{currentUser.username}</span>
              </div>
              <div className="info-item">
                <label>{t('profile.info.email_label')}</label>
                <span>{currentUser.email}</span>
              </div>
              <div className="info-item">
                <label>{t('profile.info.role_label')}</label>
                <span className={`role-badge role-${currentUser.role}`}>
                  {getRoleLabel(currentUser.role)}
                </span>
              </div>
              {currentUser.department && (
                <div className="info-item">
                  <label>{t('profile.info.department')}</label>
                  <span>{currentUser.department}</span>
                </div>
              )}
              <div className="info-item">
                <label>{t('profile.info.registered')}</label>
                <span>{new Date(currentUser.created_at).toLocaleDateString(locale)}</span>
              </div>
              {currentUser.last_login && (
                <div className="info-item">
                  <label>{t('profile.info.last_login')}</label>
                  <span>{new Date(currentUser.last_login).toLocaleString(locale)}</span>
                </div>
              )}
            </div>
          </div>

          <div className="password-change-section">
            <h3>{t('profile.password.title')}</h3>

            {message && (
              <div className={`message ${message.type}`}>
                {message.text}
              </div>
            )}

            <form onSubmit={handlePasswordChange} className="password-form">
              <div className="form-group">
                <label htmlFor="current_password">{t('profile.password.current')}</label>
                <div className="password-input-group">
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    id="current_password"
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                    placeholder={t('profile.password.placeholder.current')}
                    disabled={loading}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="new_password">{t('profile.password.new')}</label>
                <div className="password-input-group">
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    id="new_password"
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                    placeholder={t('profile.password.placeholder.new')}
                    disabled={loading}
                    minLength={4}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="confirm_password">{t('profile.password.confirm')}</label>
                <div className="password-input-group">
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    id="confirm_password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder={t('profile.password.placeholder.confirm')}
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
                  {t('profile.password.show')}
                </label>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={onClose}
                  className="cancel-button"
                  disabled={loading}
                >
                  {t('common.cancel')}
                </button>
                <button
                  type="submit"
                  className="submit-button"
                  disabled={loading}
                >
                  {loading ? t('profile.password.submitting') : t('profile.password.submit')}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
