import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard,
  UserPlus,
  Handshake,
  Users,
  Building2,
  Package,
  Warehouse,
  ArrowLeftRight,
  Menu,
  X,
  Calculator,
  Settings,
} from 'lucide-react'
import { useI18n } from '../i18n/I18nContext'
import HeaderControls from './HeaderControls'

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const { t } = useI18n()

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: t.nav.dashboard },
    { to: '/leads', icon: UserPlus, label: t.nav.leads },
    { to: '/deals', icon: Handshake, label: t.nav.deals },
    { to: '/contacts', icon: Users, label: t.nav.contacts },
    { to: '/companies', icon: Building2, label: t.nav.companies },
    { to: '/products', icon: Package, label: t.nav.products },
    { to: '/warehouse', icon: Warehouse, label: t.nav.warehouse },
    { to: '/movements', icon: ArrowLeftRight, label: t.nav.movements },
    { to: '/accounting', icon: Calculator, label: t.nav.accounting },
    { to: '/accounting/settings', icon: Settings, label: t.nav.rsge },
  ]

  return (
    <>
      <div className="p-5 border-b border-kinetix-700">
        <h1 className="text-xl font-bold tracking-tight">Kinetix</h1>
        <p className="text-kinetix-300 text-xs mt-1">{t.app.tagline}</p>
        <div className="hidden md:block">
          <HeaderControls variant="sidebar" />
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-kinetix-600 text-white'
                  : 'text-kinetix-200 hover:bg-kinetix-700 hover:text-white'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </>
  )
}

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-app-bg">
      <aside className="hidden md:flex w-60 bg-kinetix-800 text-white flex-col shrink-0">
        <Sidebar />
      </aside>

      {menuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-app-overlay/50" onClick={() => setMenuOpen(false)} />
          <aside className="relative w-64 h-full bg-kinetix-800 text-white flex flex-col">
            <button
              onClick={() => setMenuOpen(false)}
              className="absolute top-4 right-4 p-1 text-kinetix-200 hover:text-white z-10"
            >
              <X size={22} />
            </button>
            <Sidebar onNavigate={() => setMenuOpen(false)} />
          </aside>
        </div>
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="mobile-header md:hidden">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => setMenuOpen(true)}
              className="p-1 shrink-0 text-app-text-secondary hover:text-app-text"
              aria-label="Menu"
            >
              <Menu size={22} />
            </button>
            <span className="font-bold truncate text-app-text">Kinetix</span>
          </div>
          <HeaderControls variant="mobile" />
        </header>

        <main className="flex-1 overflow-auto bg-app-bg">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
