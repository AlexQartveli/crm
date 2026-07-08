import LanguageSwitcher from './LanguageSwitcher'
import ThemeSwitcher from './ThemeSwitcher'

type Variant = 'sidebar' | 'mobile'

export default function HeaderControls({ variant }: { variant: Variant }) {
  return (
    <div className={`flex items-center gap-2 ${variant === 'mobile' ? 'shrink-0' : 'mt-3'}`}>
      <ThemeSwitcher variant={variant} />
      <LanguageSwitcher variant={variant} />
    </div>
  )
}
