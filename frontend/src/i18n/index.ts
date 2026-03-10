// Complete i18n service for ECES application
import { itTranslations } from './translations/it';
import { enTranslations } from './translations/en';

type TranslationKey = string;
type Translations = Record<string, string>;

class CompleteI18nService {
  private currentLanguage: string = 'it';
  private translations: Record<string, Translations> = {
    it: itTranslations,
    en: enTranslations,
  };

  constructor() {
    // Load saved language preference
    const saved = localStorage.getItem('eces_language');
    if (saved && (saved === 'it' || saved === 'en')) {
      this.currentLanguage = saved;
    }
  }

  setLanguage(lang: string): void {
    if (lang === 'it' || lang === 'en') {
      this.currentLanguage = lang;
      localStorage.setItem('eces_language', lang);
      // Trigger a custom event to notify components
      window.dispatchEvent(new CustomEvent('languageChanged', { detail: lang }));
    }
  }

  getLanguage(): string {
    return this.currentLanguage;
  }

  t(key: TranslationKey): string {
    const translation = this.translations[this.currentLanguage]?.[key];
    if (translation === undefined) {
      console.warn(`Missing translation for key: ${key} in language: ${this.currentLanguage}`);
      return key;
    }
    return translation;
  }

  getAvailableLanguages(): Array<{ code: string; name: string }> {
    return [
      { code: 'it', name: 'Italiano' },
      { code: 'en', name: 'English' },
    ];
  }
}

export const i18n = new CompleteI18nService();
export type { TranslationKey };
