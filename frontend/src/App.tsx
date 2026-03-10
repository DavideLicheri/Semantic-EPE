import { useState, useEffect } from 'react'
import RecognitionPanel from './components/RecognitionPanel'
import ConversionPanel from './components/ConversionPanel'
import DomainPanel from './components/DomainPanel'
import StringNavigator from './components/StringNavigator'
import EuringMatrix from './components/EuringMatrix'
import PositionalMatrixEditor from './components/PositionalMatrixEditor'
import ErrorBoundary from './components/ErrorBoundary'
import { Login } from './components/Login'
import { Register } from './components/Register'
import { UserManagement } from './components/UserManagement'
import { UserProfile } from './components/UserProfile'
import Analytics from './components/Analytics'
import { authService, User } from './services/auth'
import { useTranslation } from './hooks/useTranslation'
import epeLogo from './assets/images/epeLogo.jpg'
import './App.css'

function App() {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<'recognize' | 'convert' | 'domains' | 'navigator' | 'matrix' | 'editor' | 'users' | 'analytics'>('recognize')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [showRegister, setShowRegister] = useState(false)
  const [showUserProfile, setShowUserProfile] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      if (authService.isAuthenticated() && !authService.isTokenExpired()) {
        try {
          const user = await authService.getCurrentUser()
          setCurrentUser(user)
          setIsAuthenticated(true)
        } catch (error) {
          console.warn('Auth check failed:', error)
          authService.logout()
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const handleLoginSuccess = async () => {
    try {
      const user = await authService.getCurrentUser()
      setCurrentUser(user)
      setIsAuthenticated(true)
    } catch (error) {
      console.error('Failed to get user after login:', error)
    }
  }

  const handleLogout = async () => {
    await authService.logout()
    setCurrentUser(null)
    setIsAuthenticated(false)
    setActiveTab('recognize')
  }

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>{t('app.loading')}</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    if (showRegister) {
      return <Register onBackToLogin={() => setShowRegister(false)} />
    }
    return <Login onLoginSuccess={handleLoginSuccess} onShowRegister={() => setShowRegister(true)} />
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <img src={epeLogo} alt="EPE Logo" className="epe-logo" />
          <div className="header-text">
            <h1>{t('app.title')}</h1>
            <p className="subtitle">{t('app.subtitle')}</p>
          </div>
          
          <div className="header-right">
            <div className="user-info">
              <div className="user-details">
                <span className="user-name">{currentUser?.full_name}</span>
                <span className="user-role">{currentUser?.role}</span>
              </div>
              <div className="user-actions">
                <button 
                  onClick={() => setShowUserProfile(true)} 
                  className="profile-button"
                >
                  {t('user.profile')}
                </button>
                <button onClick={handleLogout} className="logout-button">
                  {t('user.logout')}
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <nav className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'recognize' ? 'active' : ''}`}
          onClick={() => setActiveTab('recognize')}
        >
          {t('nav.recognition')}
        </button>
        <button
          className={`tab-button ${activeTab === 'convert' ? 'active' : ''}`}
          onClick={() => setActiveTab('convert')}
        >
          {t('nav.conversion')}
        </button>
        <button
          className={`tab-button ${activeTab === 'navigator' ? 'active' : ''}`}
          onClick={() => setActiveTab('navigator')}
        >
          {t('nav.navigator')}
        </button>
        <button
          className={`tab-button ${activeTab === 'matrix' ? 'active' : ''}`}
          onClick={() => setActiveTab('matrix')}
        >
          {t('nav.matrix')}
        </button>
        <button
          className={`tab-button ${activeTab === 'domains' ? 'active' : ''}`}
          onClick={() => setActiveTab('domains')}
        >
          {t('nav.domains')}
        </button>
        {(currentUser?.role === 'matrix_editor' || currentUser?.role === 'super_admin') && (
          <button
            className={`tab-button ${activeTab === 'editor' ? 'active' : ''}`}
            onClick={() => setActiveTab('editor')}
          >
            Editor Campi
          </button>
        )}
        {currentUser?.role === 'super_admin' && (
          <>
            <button
              className={`tab-button ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              {t('nav.users')}
            </button>
            <button
              className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveTab('analytics')}
            >
              {t('nav.analytics')}
            </button>
          </>
        )}
      </nav>

      <main className="app-main">
        {activeTab === 'recognize' ? (
          <RecognitionPanel />
        ) : activeTab === 'convert' ? (
          <ConversionPanel />
        ) : activeTab === 'navigator' ? (
          <StringNavigator />
        ) : activeTab === 'matrix' ? (
          <EuringMatrix currentUser={currentUser} />
        ) : activeTab === 'editor' ? (
          <ErrorBoundary fallbackTitle="Errore nell'Editor Campi">
            <PositionalMatrixEditor currentUser={currentUser} />
          </ErrorBoundary>
        ) : activeTab === 'users' ? (
          <UserManagement currentUser={currentUser} />
        ) : activeTab === 'analytics' ? (
          <Analytics />
        ) : (
          <DomainPanel />
        )}
      </main>

      {showUserProfile && currentUser && (
        <UserProfile 
          currentUser={currentUser} 
          onClose={() => setShowUserProfile(false)} 
        />
      )}
    </div>
  )
}

export default App
