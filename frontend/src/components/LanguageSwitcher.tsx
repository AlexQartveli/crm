import { useI18n } from '../i18n/I18nContext'
import { LOCALE_LABELS, type Locale } from '../i18n/translations'

const LOCALES: Locale[] = ['ru', 'en', 'ka']

type Variant = 'sidebar' | 'mobile'

const VARIANT_STYLES: Record<Variant, { wrap: string; active: string; inactive: string }> = {
  sidebar: {
    wrap: 'flex gap-1 p-1 bg-kinetix-900/50 rounded-lg',
    active: 'bg-kinetix-600 text-white',
    inactive: 'text-kinetix-300 hover:text-white hover:bg-kinetix-700',
  },
  mobile: {
    wrap: 'flex gap-1 p-1 bg-kinetix-900/60 rounded-lg shrink-0',
    active: 'bg-white text-kinetix-800',
    inactive: 'text-kinetix-200 hover:text-white hover:bg-kinetix-700',
  },
}

export default function LanguageSwitcher({ variant = 'sidebar' }: { variant?: Variant }) {
  const { locale, setLocale } = useI18n()
  const styles = VARIANT_STYLES[variant]

  return (
    <div className={styles.wrap} role="group" aria-label="Language">
      {LOCALES.map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => setLocale(l)}
          className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
            locale === l ? styles.active : styles.inactive
          }`}
        >
          {LOCALE_LABELS[l]}
        </button>
      ))}
    </div>
  )
}
