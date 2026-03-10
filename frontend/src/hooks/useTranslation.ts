import { useState, useEffect } from 'react';
import { i18n, TranslationKey } from '../i18n';

export function useTranslation() {
  const [, setLanguage] = useState(i18n.getLanguage());

  useEffect(() => {
    const handleLanguageChange = () => {
      setLanguage(i18n.getLanguage());
    };

    window.addEventListener('languageChanged', handleLanguageChange);
    return () => window.removeEventListener('languageChanged', handleLanguageChange);
  }, []);

  const t = (key: TranslationKey): string => {
    return i18n.t(key);
  };

  return { t, i18n };
}
