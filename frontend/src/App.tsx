import { useState, useEffect, useRef, useMemo } from 'react'
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
import ISPRAQuery from './components/ISPRAQuery'
import ArchivePanel from './components/ArchivePanel'
import LizzyButton from './components/LizzyButton'
import { authService, User } from './services/auth'
import { useTranslation } from './hooks/useTranslation'
import { i18n } from './i18n'
import epeLogo from './assets/images/epeLogo.jpg'
import './App.css'

type TabKey = 'recognize' | 'convert' | 'domains' | 'navigator' | 'matrix' | 'editor' | 'users' | 'analytics' | 'ispra' | 'archive'

interface NavTab {
  key: TabKey
  label: string
}

interface NavGroup {
  id: string
  label: string
  tabs: NavTab[]
}

function App() {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<TabKey>('recognize')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [showRegister, setShowRegister] = useState(false)
  const [showUserProfile, setShowUserProfile] = useState(false)
  const [openMenu, setOpenMenu] = useState<string | null>(null)
  const navRef = useRef<HTMLElement>(null)

  // Voci di menu raggruppate per cluster funzionale (troppe tab singole in fila
  // erano diventate difficili da scansionare -- discusso con Davide 03/08/2026).
  // Ogni gruppo si apre come dropdown dal proprio pulsante di categoria.
  const navGroups: NavGroup[] = useMemo(() => {
    const groups: NavGroup[] = [
      {
        id: 'operations',
        label: 'Operazioni EURING',
        tabs: [
          { key: 'recognize', label: t('nav.recognition') },
          { key: 'convert', label: t('nav.conversion') },
          { key: 'navigator', label: t('nav.navigator') },
        ],
      },
      {
        id: 'analysis',
        label: 'Analisi',
        tabs: [
          { key: 'matrix', label: t('nav.matrix') },
          { key: 'domains', label: t('nav.domains') },
          { key: 'ispra', label: 'EPE ISPRA' },
        ],
      },
      {
        id: 'archive',
        label: 'Archivio & Comunità',
        tabs: [
          { key: 'archive', label: 'Archivio' },
        ],
      },
    ]

    const adminTabs: NavTab[] = []
    // Editing matrice riservato a super_admin (auth_service.can_edit_matrix);
    // "matrix_editor" non e' un ruolo backend reale, rimosso riferimento
    // morto il 04/08/2026.
    if (currentUser?.role === 'super_admin') {
      adminTabs.push({ key: 'editor', label: t('nav.editor') })
    }
    if (currentUser?.role === 'super_admin') {
      adminTabs.push({ key: 'users', label: t('nav.users') })
      adminTabs.push({ key: 'analytics', label: t('nav.analytics') })
    }
    if (adminTabs.length > 0) {
      groups.push({ id: 'admin', label: 'Amministrazione', tabs: adminTabs })
    }

    return groups
  }, [t, currentUser?.role])

  // Chiude il dropdown aperto se si clicca fuori dalla barra di navigazione.
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setOpenMenu(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

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
            <button
              className="lang-toggle"
              onClick={() => i18n.setLanguage(i18n.getLanguage() === 'en' ? 'it' : 'en')}
              title={i18n.getLanguage() === 'en' ? 'Switch to Italian' : "Passa all'inglese"}
            >
              {i18n.getLanguage() === 'en' ? t('lang.switch_to_it') : t('lang.switch_to_en')}
            </button>
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

      <nav className="tab-navigation" ref={navRef}>
        {navGroups.map((group) => {
          const isGroupActive = group.tabs.some((tab) => tab.key === activeTab)
          const isOpen = openMenu === group.id
          return (
            <div className="nav-group" key={group.id}>
              <button
                className={`tab-button nav-group-button ${isGroupActive ? 'active' : ''}`}
                onClick={() => setOpenMenu(isOpen ? null : group.id)}
              >
                {group.label}
                <span className="nav-group-caret">▾</span>
              </button>
              {isOpen && (
                <div className="nav-dropdown">
                  {group.tabs.map((tabItem) => (
                    <button
                      key={tabItem.key}
                      className={`nav-dropdown-item ${activeTab === tabItem.key ? 'active' : ''}`}
                      onClick={() => {
                        setActiveTab(tabItem.key)
                        setOpenMenu(null)
                      }}
                    >
                      {tabItem.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )
        })}
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
          <ErrorBoundary fallbackTitle={t('app.error.field_editor')}>
            <PositionalMatrixEditor currentUser={currentUser} />
          </ErrorBoundary>
        ) : activeTab === 'users' ? (
          <UserManagement currentUser={currentUser} />
        ) : activeTab === 'analytics' ? (
          <Analytics />
        ) : activeTab === 'ispra' ? (
          <ISPRAQuery />
        ) : activeTab === 'archive' ? (
          <ArchivePanel />
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
      <LizzyButton />
    </div>
  )
}

export default App
