/**
 * User Management Component for ECES (Super Admin only)
 */
import React, { useState, useEffect } from 'react';
import { User } from '../services/auth';
import { useTranslation } from '../hooks/useTranslation';
import { i18n } from '../i18n';
import './UserManagement.css';

interface UserManagementProps {
  currentUser: User | null;
}

interface UserWithActions extends User {
  isUpdating?: boolean;
}

export const UserManagement: React.FC<UserManagementProps> = ({ currentUser }) => {
  const { t } = useTranslation();
  const locale = i18n.getLanguage() === 'it' ? 'it-IT' : 'en-GB';
  const [users, setUsers] = useState<UserWithActions[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  // Stato per il pannello di assegnazione scheme/territorio dei rings_admin
  // (priorita' #6 della scaletta, 02/09/2026). Dizionario codice->descrizione
  // per la dropdown scheme (161 voci, caricato una volta sola all'avvio).
  const [ringingSchemes, setRingingSchemes] = useState<Record<string, string>>({});
  // Bozza locale (non ancora salvata) per riga utente, chiave = username.
  const [assignmentDrafts, setAssignmentDrafts] = useState<Record<string, { ringingScheme: string; territoryCode: string }>>({});
  // Testo digitato nel campo di ricerca territorio, per riga utente.
  const [territoryQuery, setTerritoryQuery] = useState<Record<string, string>>({});
  // Risultati della ricerca su /api/euring/field/place_code/search, per riga utente.
  const [territoryResults, setTerritoryResults] = useState<Record<string, { code: string; description: string }[]>>({});

  // Fix 02/09/2026: questo useEffect era dichiarato DOPO il return anticipato
  // sotto (violazione delle Rules of Hooks -- un hook non puo' essere chiamato
  // condizionatamente). Spostato prima del guard, con il controllo
  // super_admin ora dentro il corpo dell'effetto: stesso comportamento
  // (loadUsers parte solo per un super_admin), ordine degli hook stabile a
  // ogni render.
  useEffect(() => {
    if (currentUser?.role === 'super_admin') {
      loadUsers();
      loadRingingSchemes();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentUser]);

  // Check if current user is Super Admin
  if (!currentUser || currentUser.role !== 'super_admin') {
    return (
      <div className="user-management-container">
        <div className="access-denied">
          <h2>{t('mgmt.access_denied')}</h2>
          <p>{t('mgmt.access_denied_text')}</p>
        </div>
      </div>
    );
  }

  const loadUsers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('eces_token');

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/users`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
      } else {
        setError(t('mgmt.error.load'));
      }
    } catch (err) {
      setError(t('mgmt.error.connection'));
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (username: string, newRole: string) => {
    try {
      setUsers(prev => prev.map(user =>
        user.username === username ? { ...user, isUpdating: true } : user
      ));

      const token = localStorage.getItem('eces_token');

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/users/role`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: username,
          new_role: newRole
        }),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUsers(prev => prev.map(user =>
          user.username === username ? { ...updatedUser, isUpdating: false } : user
        ));
      } else {
        const errorData = await response.json();
        setError(errorData.detail || t('mgmt.error.role_update'));
        setUsers(prev => prev.map(user =>
          user.username === username ? { ...user, isUpdating: false } : user
        ));
      }
    } catch (err) {
      setError(t('mgmt.error.connection'));
      setUsers(prev => prev.map(user =>
        user.username === username ? { ...user, isUpdating: false } : user
      ));
    }
  };

  const loadRingingSchemes = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/euring/field/ringing_scheme?version=2020`);
      if (response.ok) {
        const data = await response.json();
        setRingingSchemes(data.valid_values_descriptions || {});
      }
      // Non bloccante se fallisce: la dropdown scheme resta vuota, il resto
      // della pagina utenti funziona comunque.
    } catch (err) {
      // idem
    }
  };

  const getAssignmentDraft = (user: UserWithActions) => {
    return assignmentDrafts[user.username] ?? {
      ringingScheme: user.ringing_scheme || '',
      territoryCode: user.territory_place_codes?.[0] || '',
    };
  };

  const updateAssignmentDraft = (user: UserWithActions, patch: Partial<{ ringingScheme: string; territoryCode: string }>) => {
    const current = getAssignmentDraft(user);
    setAssignmentDrafts(prev => ({ ...prev, [user.username]: { ...current, ...patch } }));
  };

  const searchTerritoryPlaceCodes = async (username: string, query: string) => {
    setTerritoryQuery(prev => ({ ...prev, [username]: query }));
    if (query.trim().length < 2) {
      setTerritoryResults(prev => ({ ...prev, [username]: [] }));
      return;
    }
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/euring/field/place_code/search?q=${encodeURIComponent(query)}&version=2020`);
      if (response.ok) {
        const data = await response.json();
        setTerritoryResults(prev => ({ ...prev, [username]: data.matches || [] }));
      }
    } catch (err) {
      // Non bloccante: la ricerca territorio resta vuota.
    }
  };

  const saveRingsAdminAssignment = async (user: UserWithActions) => {
    const draft = getAssignmentDraft(user);
    try {
      setUsers(prev => prev.map(u =>
        u.username === user.username ? { ...u, isUpdating: true } : u
      ));

      const token = localStorage.getItem('eces_token');

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/users/rings-admin-assignment`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: user.username,
          ringing_scheme: draft.ringingScheme || null,
          territory_place_code: draft.territoryCode || null,
        }),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUsers(prev => prev.map(u =>
          u.username === user.username ? { ...updatedUser, isUpdating: false } : u
        ));
        setAssignmentDrafts(prev => {
          const next = { ...prev };
          delete next[user.username];
          return next;
        });
      } else {
        const errorData = await response.json();
        setError(errorData.detail || t('mgmt.error.assignment_update'));
        setUsers(prev => prev.map(u =>
          u.username === user.username ? { ...u, isUpdating: false } : u
        ));
      }
    } catch (err) {
      setError(t('mgmt.error.connection'));
      setUsers(prev => prev.map(u =>
        u.username === user.username ? { ...u, isUpdating: false } : u
      ));
    }
  };

  const toggleUserStatus = async (username: string, activate: boolean) => {
    try {
      setUsers(prev => prev.map(user =>
        user.username === username ? { ...user, isUpdating: true } : user
      ));

      const token = localStorage.getItem('eces_token');
      const action = activate ? 'activate' : 'deactivate';

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/users/${username}/${action}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUsers(prev => prev.map(user =>
          user.username === username ? { ...updatedUser, isUpdating: false } : user
        ));
      } else {
        const errorData = await response.json();
        setError(errorData.detail || t('mgmt.error.status_update'));
        setUsers(prev => prev.map(user =>
          user.username === username ? { ...user, isUpdating: false } : user
        ));
      }
    } catch (err) {
      setError(t('mgmt.error.connection'));
      setUsers(prev => prev.map(user =>
        user.username === username ? { ...user, isUpdating: false } : user
      ));
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'super_admin': return '👑';
      case 'rings_admin': return '🔧';
      case 'user': return '👤';
      case 'viewer': return '👁️';
      default: return '❓';
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin': return '#e74c3c';
      case 'rings_admin': return '#f39c12';
      case 'user': return '#3498db';
      case 'viewer': return '#95a5a6';
      default: return '#7f8c8d';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'super_admin': return 'Super Admin';
      case 'rings_admin': return 'Operatore Centro di inanellamento';
      case 'user': return 'User';
      case 'viewer': return 'Viewer';
      default: return role;
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesFilter = filter === 'all' || user.role === filter;
    const matchesSearch = user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  if (loading) {
    return (
      <div className="user-management-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>{t('mgmt.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="user-management-container">
      <div className="user-management-header">
        <h1>{t('mgmt.title')}</h1>
        <p>{t('mgmt.subtitle')}</p>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="user-management-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder={t('mgmt.search_placeholder')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-tabs">
          <button
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            {t('mgmt.filter.all')} ({users.length})
          </button>
          <button
            className={filter === 'super_admin' ? 'active' : ''}
            onClick={() => setFilter('super_admin')}
          >
            Super Admin
          </button>
          <button
            className={filter === 'rings_admin' ? 'active' : ''}
            onClick={() => setFilter('rings_admin')}
          >
            Operatore Centro di inanellamento
          </button>
          <button
            className={filter === 'user' ? 'active' : ''}
            onClick={() => setFilter('user')}
          >
            User
          </button>
          <button
            className={filter === 'viewer' ? 'active' : ''}
            onClick={() => setFilter('viewer')}
          >
            Viewer
          </button>
        </div>

        <button
          onClick={loadUsers}
          className="refresh-button"
          disabled={loading}
        >
          {t('mgmt.refresh')}
        </button>
      </div>

      <div className="users-grid">
        {filteredUsers.map((user) => (
          <div key={user.username} className="user-card">
            <div className="user-card-header">
              <div className="user-info">
                <h3>{user.full_name}</h3>
                <p className="username">@{user.username}</p>
                <p className="email">{user.email}</p>
                {user.department && (
                  <p className="department">{user.department}</p>
                )}
              </div>

              <div className="user-status">
                <div
                  className="role-badge"
                  style={{ backgroundColor: getRoleColor(user.role) }}
                >
                  {getRoleIcon(user.role)} {getRoleLabel(user.role)}
                </div>

                <div className={`status-indicator ${user.is_active ? 'active' : 'inactive'}`}>
                  {user.is_active ? t('mgmt.status.active') : t('mgmt.status.inactive')}
                </div>
              </div>
            </div>

            <div className="user-card-body">
              <div className="user-dates">
                <p><strong>{t('mgmt.registered')}</strong> {new Date(user.created_at).toLocaleDateString(locale)}</p>
                {user.last_login && (
                  <p><strong>{t('mgmt.last_login')}</strong> {new Date(user.last_login).toLocaleDateString(locale)}</p>
                )}
              </div>

              {user.username !== currentUser.username && (
                <div className="user-actions">
                  <div className="role-selector">
                    <label>{t('mgmt.role_label')}</label>
                    <select
                      value={user.role}
                      onChange={(e) => updateUserRole(user.username, e.target.value)}
                      disabled={user.isUpdating || user.role === 'super_admin'}
                    >
                      <option value="viewer">👁️ Viewer</option>
                      <option value="user">👤 User</option>
                      <option value="rings_admin">🔧 Operatore Centro di inanellamento</option>
                      {user.role === 'super_admin' && (
                        <option value="super_admin">👑 Super Admin</option>
                      )}
                    </select>
                  </div>

                  {user.role === 'rings_admin' && (() => {
                    const draft = getAssignmentDraft(user);
                    const query = territoryQuery[user.username] ?? '';
                    const results = territoryResults[user.username] ?? [];
                    return (
                      <div className="rings-admin-assignment">
                        <label>{t('mgmt.assignment_title')}</label>
                        <select
                          value={draft.ringingScheme}
                          onChange={(e) => updateAssignmentDraft(user, { ringingScheme: e.target.value })}
                          disabled={user.isUpdating}
                        >
                          <option value="">{t('mgmt.assignment_scheme_placeholder')}</option>
                          {Object.entries(ringingSchemes).map(([code, desc]) => (
                            <option key={code} value={code}>{code} — {desc}</option>
                          ))}
                        </select>

                        <input
                          type="text"
                          list={`territory-options-${user.username}`}
                          placeholder={t('mgmt.assignment_territory_placeholder')}
                          value={query || draft.territoryCode}
                          onChange={(e) => {
                            searchTerritoryPlaceCodes(user.username, e.target.value);
                            // Se l'utente cancella il testo, azzera anche il codice scelto.
                            if (!e.target.value) {
                              updateAssignmentDraft(user, { territoryCode: '' });
                            }
                          }}
                          onBlur={(e) => {
                            // Se il testo digitato corrisponde esattamente a un
                            // risultato trovato, lo adotta come codice scelto.
                            const match = results.find(r => `${r.code} — ${r.description}` === e.target.value || r.code === e.target.value);
                            if (match) {
                              updateAssignmentDraft(user, { territoryCode: match.code });
                              setTerritoryQuery(prev => ({ ...prev, [user.username]: `${match.code} — ${match.description}` }));
                            }
                          }}
                          disabled={user.isUpdating}
                        />
                        <datalist id={`territory-options-${user.username}`}>
                          {results.map(r => (
                            <option key={r.code} value={`${r.code} — ${r.description}`} />
                          ))}
                        </datalist>

                        <button
                          onClick={() => saveRingsAdminAssignment(user)}
                          disabled={user.isUpdating}
                          className="assignment-save-button"
                        >
                          {user.isUpdating ? '⏳' : '💾'} {t('mgmt.assignment_save')}
                        </button>
                      </div>
                    );
                  })()}

                  <div className="status-actions">
                    {user.is_active ? (
                      <button
                        onClick={() => toggleUserStatus(user.username, false)}
                        disabled={user.isUpdating}
                        className="deactivate-button"
                      >
                        {user.isUpdating ? '⏳' : '🚫'} {t('mgmt.deactivate')}
                      </button>
                    ) : (
                      <button
                        onClick={() => toggleUserStatus(user.username, true)}
                        disabled={user.isUpdating}
                        className="activate-button"
                      >
                        {user.isUpdating ? '⏳' : '✅'} {t('mgmt.activate')}
                      </button>
                    )}
                  </div>
                </div>
              )}

              {user.username === currentUser.username && (
                <div className="current-user-badge">
                  {t('mgmt.your_account')}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredUsers.length === 0 && (
        <div className="no-users">
          <p>{t('mgmt.no_users')}</p>
        </div>
      )}

      <div className="user-management-footer">
        <p>{t('mgmt.footer.total')} {users.length} | {t('mgmt.footer.filtered')} {filteredUsers.length}</p>
        <p>{t('mgmt.footer.role_notification')}</p>
      </div>
    </div>
  );
};
