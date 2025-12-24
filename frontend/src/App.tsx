import { useState } from 'react'
import RecognitionPanel from './components/RecognitionPanel'
import ConversionPanel from './components/ConversionPanel'
import DomainPanel from './components/DomainPanel'
import StringNavigator from './components/StringNavigator'
import EuringMatrix from './components/EuringMatrix'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState<'recognize' | 'convert' | 'domains' | 'navigator' | 'matrix'>('recognize')

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <img 
            src="/src/assets/images/epeLogo.jpg" 
            alt="EPE Logo" 
            className="epe-logo"
            onError={(e) => {
              // Fallback to text logo if image fails to load
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              const textLogo = document.createElement('div');
              textLogo.className = 'epe-logo-text';
              textLogo.textContent = 'EPE';
              target.parentNode?.insertBefore(textLogo, target);
            }}
          />
          <div className="header-text">
            <h1>EURING Code Recognition System</h1>
            <p className="subtitle">Riconoscimento e conversione automatica dei codici EURING</p>
          </div>
        </div>
      </header>

      <nav className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'recognize' ? 'active' : ''}`}
          onClick={() => setActiveTab('recognize')}
        >
          Riconoscimento
        </button>
        <button
          className={`tab-button ${activeTab === 'convert' ? 'active' : ''}`}
          onClick={() => setActiveTab('convert')}
        >
          Conversione
        </button>
        <button
          className={`tab-button ${activeTab === 'navigator' ? 'active' : ''}`}
          onClick={() => setActiveTab('navigator')}
        >
          📋 Navigatore Stringhe
        </button>
        <button
          className={`tab-button ${activeTab === 'matrix' ? 'active' : ''}`}
          onClick={() => setActiveTab('matrix')}
        >
          📊 Matrice EURING
        </button>
        <button
          className={`tab-button ${activeTab === 'domains' ? 'active' : ''}`}
          onClick={() => setActiveTab('domains')}
        >
          Domini Semantici
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'recognize' ? (
          <RecognitionPanel />
        ) : activeTab === 'convert' ? (
          <ConversionPanel />
        ) : activeTab === 'navigator' ? (
          <StringNavigator />
        ) : activeTab === 'matrix' ? (
          <EuringMatrix />
        ) : (
          <DomainPanel />
        )}
      </main>

      <footer className="app-footer">
        <p>
          EURING Code Recognition System v1.0.0 | 
          Powered by <strong>EPE</strong> | 
          Backend API: <a href="http://localhost:8000/docs" target="_blank">Documentazione</a>
        </p>
      </footer>
    </div>
  )
}

export default App