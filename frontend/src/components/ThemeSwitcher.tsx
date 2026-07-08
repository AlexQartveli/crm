import { Sun, Moon } from 'lucide-react'
import { useTheme } from '../theme/ThemeContext'
import { useI18n } from '../i18n/I18nContext'

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

export default function ThemeSwitcher({ variant = 'sidebar' }: { variant?: Variant }) {
  const { theme, setTheme } = useTheme()
  const { t } = useI18n()
  const styles = VARIANT_STYLES[variant]

  return (
    <div className={styles.wrap} role="group" aria-label={t.common.theme}>
      <button
        type="button"
        onClick={() => setTheme('light')}
        aria-label={t.common.lightTheme}
        aria-pressed={theme === 'light'}
        className={`p-1.5 rounded-md transition-colors ${
          theme === 'light' ? styles.active : styles.inactive
        }`}
      >
        <Sun size={16} />
      </button>
      <button
        type="button"
        onClick={() => setTheme('dark')}
        aria-label={t.common.darkTheme}
        aria-pressed={theme === 'dark'}
        className={`p-1.5 rounded-md transition-colors ${
          theme === 'dark' ? styles.active : styles.inactive
        }`}
      >
        <Moon size={16} />
      </button>
    </div>
  )
}
