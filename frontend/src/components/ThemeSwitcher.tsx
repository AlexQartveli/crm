import { Sun, Moon } from 'lucide-react'
import { useTheme } from '../theme/ThemeContext'
import { useI18n } from '../i18n/I18nContext'

type Variant = 'sidebar' | 'mobile'

export default function ThemeSwitcher({ variant = 'sidebar' }: { variant?: Variant }) {
  const { theme, setTheme } = useTheme()
  const { t } = useI18n()

  const wrap = variant === 'sidebar' ? 'sidebar-controls' : 'header-controls'
  const btn = variant === 'sidebar' ? 'sidebar-control-btn' : 'header-control-btn'
  const active = variant === 'sidebar' ? 'sidebar-control-btn-active' : 'header-control-btn-active'

  return (
    <div className={wrap} role="group" aria-label={t.common.theme}>
      <button
        type="button"
        onClick={() => setTheme('light')}
        aria-label={t.common.lightTheme}
        aria-pressed={theme === 'light'}
        className={`p-1.5 ${btn} ${theme === 'light' ? active : ''}`}
      >
        <Sun size={16} />
      </button>
      <button
        type="button"
        onClick={() => setTheme('dark')}
        aria-label={t.common.darkTheme}
        aria-pressed={theme === 'dark'}
        className={`p-1.5 ${btn} ${theme === 'dark' ? active : ''}`}
      >
        <Moon size={16} />
      </button>
    </div>
  )
}
