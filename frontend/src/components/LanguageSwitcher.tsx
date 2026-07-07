import { useI18n } from '../i18n/I18nContext'
import { LOCALE_LABELS, type Locale } from '../i18n/translations'

const LOCALES: Locale[] = ['ru', 'en', 'ka']

export default function LanguageSwitcher({ compact = false }: { compact?: boolean }) {
  const { locale, setLocale } = useI18n()

  return (
    <div className={`flex gap-1 ${compact ? '' : 'p-1 bg-kinetix-900/50 rounded-lg'}`}>
      {LOCALES.map((l) => (
        <button
          key={l}
          onClick={() => setLocale(l)}
          className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
            locale === l
              ? 'bg-kinetix-600 text-white'
              : 'text-kinetix-300 hover:text-white hover:bg-kinetix-700'
          }`}
        >
          {LOCALE_LABELS[l]}
        </button>
      ))}
    </div>
  )
}
