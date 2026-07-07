import { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react'
import { translations, LOCALE_STORAGE_KEY, type Locale, type Translations } from './translations'

interface I18nContextType {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: Translations
}

const I18nContext = createContext<I18nContextType | null>(null)

function getInitialLocale(): Locale {
  const saved = localStorage.getItem(LOCALE_STORAGE_KEY) as Locale | null
  if (saved && translations[saved]) return saved
  const browser = navigator.language.slice(0, 2)
  if (browser === 'ka') return 'ka'
  if (browser === 'en') return 'en'
  return 'ru'
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(getInitialLocale)

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l)
    localStorage.setItem(LOCALE_STORAGE_KEY, l)
    document.documentElement.lang = l
  }, [])

  useEffect(() => {
    document.documentElement.lang = locale
    document.title = translations[locale].app.title
  }, [locale])

  return (
    <I18nContext.Provider value={{ locale, setLocale, t: translations[locale] }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useI18n() {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useI18n must be used within I18nProvider')
  return ctx
}
