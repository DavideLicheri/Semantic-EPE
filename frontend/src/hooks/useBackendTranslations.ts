import { useState, useEffect, useCallback } from 'react';

interface Translations {
  [key: string]: string;
}

const TRANSLATIONS: { [lang: string]: Translations } = {
  it: {
    'recognition.title': 'Riconoscimento Codice EURING',
    'recognition.input.label': 'Inserisci il codice EURING da analizzare',
    'recognition.button.analyze': 'Analizza Codice',
    'recognition.button.clear': 'Pulisci',
    'recognition.examples.title': 'Esempi:',
    'recognition.examples.euring1966': 'EURING 1966 (spazi)',
    'recognition.examples.euring1979': 'EURING 1979 (fisso)',
    'recognition.examples.euring2000': 'EURING 2000 (codificato)',
    'recognition.examples.euring2020': 'EURING 2020 (pipe)',
    'recognition.batch.mode': 'Modalità batch (più stringhe)',
    'recognition.include.analysis': 'Includi analisi dettagliata',
    'app.title': 'ECES - Sistema di Evoluzione Codici EURING',
    'app.subtitle': 'Sistema completo per l\'evoluzione e gestione dei codici EURING tra diverse versioni',
    'auth.loading': 'Caricamento...',
    'auth.profile': 'Profilo',
    'auth.logout': 'Esci',
    'nav.recognition': 'Riconoscimento',
    'nav.conversion': 'Conversione',
    'nav.navigator': 'Navigatore',
    'nav.matrix': 'Matrice',
    'nav.domains': 'Domini',
    'nav.users': 'Utenti',
    'nav.analytics': 'Analytics',
    'common.loading': 'Caricamento...',
    'common.error': 'Errore',
    'common.success': 'Successo'
  },
  en: {
    'recognition.title': 'EURING Code Recognition',
    'recognition.input.label': 'Enter the EURING code to analyze',
    'recognition.button.analyze': 'Analyze Code',
    'recognition.button.clear': 'Clear',
    'recognition.examples.title': 'Examples:',
    'recognition.examples.euring1966': 'EURING 1966 (spaces)',
    'recognition.examples.euring1979': 'EURING 1979 (fixed)',
    'recognition.examples.euring2000': 'EURING 2000 (encoded)',
    'recognition.examples.euring2020': 'EURING 2020 (pipe)',
    'recognition.batch.mode': 'Batch mode (multiple strings)',
    'recognition.include.analysis': 'Include detailed analysis',
    'app.title': 'ECES - EURING Code Evolution System',
    'app.subtitle': 'Complete system for evolution and management of EURING codes between different versions',
    'auth.loading': 'Loading...',
    'auth.profile': 'Profile',
    'auth.logout': 'Logout',
    'nav.recognition': 'Recognition',
    'nav.conversion': 'Conversion',
    'nav.navigator': 'Navigator',
    'nav.matrix': 'Matrix',
    'nav.domains': 'Domains',
    'nav.users': 'Users',
    'nav.analytics': 'Analytics',
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success'
  }
};

export function useSimpleTranslations() {
  const [language, setLanguageState] = useState<'it' | 'en'>('it');
  const [forceUpdate, setForceUpdate] = useState(0);

  // Load language from localStorage on mount
  useEffect(() => {
    const savedLang = localStorage.getItem('eces_language') as 'it' | 'en';
    if (savedLang && ['it', 'en'].includes(savedLang)) {
      console.log(`🔄 [SimpleTranslations] Loading saved language: ${savedLang}`);
      setLanguageState(savedLang);
    } else {
      console.log('🔄 [SimpleTranslations] No saved language, defaulting to Italian');
      localStorage.setItem('eces_language', 'it');
    }
  }, []);

  const setLanguage = useCallback((newLanguage: 'it' | 'en') => {
    console.log(`🔄 [SimpleTranslations] Changing language from ${language} to ${newLanguage}`);
    
    if (newLanguage === language) {
      console.log('🔄 [SimpleTranslations] Same language, skipping');
      return;
    }

    // Update localStorage
    localStorage.setItem('eces_language', newLanguage);
    console.log(`💾 [SimpleTranslations] Saved to localStorage: ${newLanguage}`);

    // Update state
    setLanguageState(newLanguage);
    
    // Force all components to re-render
    setForceUpdate(prev => prev + 1);
    console.log(`🔄 [SimpleTranslations] Force update triggered: ${forceUpdate + 1}`);

    // Dispatch global event
    window.dispatchEvent(new CustomEvent('languageChanged', { 
      detail: { language: newLanguage, forceUpdate: forceUpdate + 1 } 
    }));
    console.log(`📡 [SimpleTranslations] Global event dispatched for ${newLanguage}`);

  }, [language, forceUpdate]);

  const t = useCallback((key: string): string => {
    const translation = TRANSLATIONS[language]?.[key] || key;
    
    if (translation === key && key.includes('.')) {
      console.warn(`🔍 [SimpleTranslations] Missing translation for key: ${key} (language: ${language})`);
    }
    
    return translation;
  }, [language]);

  return {
    t,
    language,
    setLanguage,
    forceUpdate, // Expose for components that need to track updates
    availableLanguages: [
      { code: 'it' as const, name: 'Italiano', flag: '🇮🇹' },
      { code: 'en' as const, name: 'English', flag: '🇬🇧' }
    ]
  };
}
