import { useI18n } from '../i18n/I18nContext'
import { LOCALE_LABELS, type Locale } from '../i18n/translations'

const LOCALES: Locale[] = ['ru', 'en', 'ka']

type Variant = 'sidebar' | 'mobile'

export default function LanguageSwitcher({ variant = 'sidebar' }: { variant?: Variant }) {
  const { locale, setLocale } = useI18n()

  const wrap = variant === 'sidebar' ? 'sidebar-controls' : 'header-controls'
  const btn = variant === 'sidebar' ? 'sidebar-control-btn' : 'header-control-btn'
  const active = variant === 'sidebar' ? 'sidebar-control-btn-active' : 'header-control-btn-active'

  return (
    <div className={wrap} role="group" aria-label="Language">
      {LOCALES.map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => setLocale(l)}
          className={`px-2.5 py-1 text-xs font-semibold ${btn} ${locale === l ? active : ''}`}
        >
          {LOCALE_LABELS[l]}
        </button>
      ))}
    </div>
  )
}
