/**
 * User Management Component for ECES (Super Admin only)
 */
import React, { useState, useEffect } from 'react';
import { User } from '../services/auth';
import './UserManagement.css';

interface UserManagementProps {
  currentUser: User | null;
}

interface UserWithActions extends User {
  isUpdating?: boolean;
}

export const UserManagement: React.FC<UserManagementProps> = ({ currentUser }) => {
  const [users, setUsers] = useState<UserWithActions[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Check if current user is Super Admin
  if (!currentUser || currentUser.role !== 'super_admin') {
    return (
      <div className="user-management-container">
        <div className="access-denied">
          <h2>🚫 Accesso Negato</h2>
          <p>Solo il Super Admin può accedere alla gestione utenti.</p>
        </div>
      </div>
    );
  }

  useEffect(() => {
    loadUsers();
  }, []);

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
        setError('Errore nel caricamento degli utenti');
      }
    } catch (err) {
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (username: string, newRole: string) => {
    try {
      // Set updating state
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
        setError(errorData.detail || 'Errore nell\'aggiornamento del ruolo');
        // Reset updating state
        setUsers(prev => prev.map(user => 
          user.username === username ? { ...user, isUpdating: false } : user
        ));
      }
    } catch (err) {
      setError('Errore di connessione');
      // Reset updating state
      setUsers(prev => prev.map(user => 
        user.username === username ? { ...user, isUpdating: false } : user
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
        setError(errorData.detail || 'Errore nell\'aggiornamento dello stato');
        setUsers(prev => prev.map(user => 
          user.username === username ? { ...user, isUpdating: false } : user
        ));
      }
    } catch (err) {
      setError('Errore di connessione');
      setUsers(prev => prev.map(user => 
        user.username === username ? { ...user, isUpdating: false } : user
      ));
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'super_admin': return '👑';
      case 'admin': return '🔧';
      case 'user': return '👤';
      case 'viewer': return '👁️';
      default: return '❓';
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin': return '#e74c3c';
      case 'admin': return '#f39c12';
      case 'user': return '#3498db';
      case 'viewer': return '#95a5a6';
      default: return '#7f8c8d';
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
          <p>Caricamento utenti...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="user-management-container">
      <div className="user-management-header">
        <h1>👥 Gestione Utenti</h1>
        <p>Amministrazione utenti e permessi del sistema</p>
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
            placeholder="🔍 Cerca..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-tabs">
          <button 
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            Tutti ({users.length})
          </button>
          <button 
            className={filter === 'super_admin' ? 'active' : ''}
            onClick={() => setFilter('super_admin')}
          >
            Super Admin
          </button>
          <button 
            className={filter === 'admin' ? 'active' : ''}
            onClick={() => setFilter('admin')}
          >
            Admin
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
          🔄 Aggiorna
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
                  {getRoleIcon(user.role)} {user.role.replace('_', ' ').toUpperCase()}
                </div>
                
                <div className={`status-indicator ${user.is_active ? 'active' : 'inactive'}`}>
                  {user.is_active ? '🟢 Attivo' : '🔴 Disattivato'}
                </div>
              </div>
            </div>

            <div className="user-card-body">
              <div className="user-dates">
                <p><strong>Registrato:</strong> {new Date(user.created_at).toLocaleDateString('it-IT')}</p>
                {user.last_login && (
                  <p><strong>Ultimo accesso:</strong> {new Date(user.last_login).toLocaleDateString('it-IT')}</p>
                )}
              </div>

              {user.username !== currentUser.username && (
                <div className="user-actions">
                  <div className="role-selector">
                    <label>Ruolo:</label>
                    <select
                      value={user.role}
                      onChange={(e) => updateUserRole(user.username, e.target.value)}
                      disabled={user.isUpdating || user.role === 'super_admin'}
                    >
                      <option value="viewer">👁️ Viewer</option>
                      <option value="user">👤 User</option>
                      <option value="admin">🔧 Admin</option>
                      {user.role === 'super_admin' && (
                        <option value="super_admin">👑 Super Admin</option>
                      )}
                    </select>
                  </div>

                  <div className="status-actions">
                    {user.is_active ? (
                      <button
                        onClick={() => toggleUserStatus(user.username, false)}
                        disabled={user.isUpdating}
                        className="deactivate-button"
                      >
                        {user.isUpdating ? '⏳' : '🚫'} Disattiva
                      </button>
                    ) : (
                      <button
                        onClick={() => toggleUserStatus(user.username, true)}
                        disabled={user.isUpdating}
                        className="activate-button"
                      >
                        {user.isUpdating ? '⏳' : '✅'} Attiva
                      </button>
                    )}
                  </div>
                </div>
              )}

              {user.username === currentUser.username && (
                <div className="current-user-badge">
                  ⭐ Il tuo account
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredUsers.length === 0 && (
        <div className="no-users">
          <p>Nessun utente trovato con i filtri selezionati.</p>
        </div>
      )}

      <div className="user-management-footer">
        <p>Totale utenti: {users.length} | Filtrati: {filteredUsers.length}</p>
        <p>Le modifiche ai ruoli inviano automaticamente una notifica email all'utente.</p>
      </div>
    </div>
  );
};