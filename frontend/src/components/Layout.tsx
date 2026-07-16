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
  MessageCircle,
  Plug,
  Bot,
  UserCog,
  LogOut,
  Settings2,
  CalendarDays,
} from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { PERM, ROUTE_PERMISSIONS, ROLE_LABELS } from '../auth/permissions'
import { useCrmConfig } from '../crm/CrmConfigContext'
import { useI18n } from '../i18n/I18nContext'
import HeaderControls from './HeaderControls'

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const { t, locale } = useI18n()
  const { user, can, logout } = useAuth()
  const { entityLabel, moduleEnabled } = useCrmConfig()

  const navItems = [
    { module: 'dashboard', to: '/', icon: LayoutDashboard, label: t.nav.dashboard, permission: ROUTE_PERMISSIONS['/'] },
    { module: 'leads', to: '/leads', icon: UserPlus, label: entityLabel('leads', t.nav.leads), permission: ROUTE_PERMISSIONS['/leads'] },
    { module: 'deals', to: '/deals', icon: Handshake, label: entityLabel('deals', t.nav.deals), permission: ROUTE_PERMISSIONS['/deals'] },
    { module: 'schedule', to: '/schedule', icon: CalendarDays, label: entityLabel('schedule', t.nav.schedule), permission: ROUTE_PERMISSIONS['/schedule'] },
    { module: 'contacts', to: '/contacts', icon: Users, label: entityLabel('contacts', t.nav.contacts), permission: ROUTE_PERMISSIONS['/contacts'] },
    { module: 'companies', to: '/companies', icon: Building2, label: entityLabel('companies', t.nav.companies), permission: ROUTE_PERMISSIONS['/companies'] },
    { module: 'products', to: '/products', icon: Package, label: entityLabel('products', t.nav.products), permission: ROUTE_PERMISSIONS['/products'] },
    { module: 'warehouse', to: '/warehouse', icon: Warehouse, label: entityLabel('warehouse', t.nav.warehouse), permission: ROUTE_PERMISSIONS['/warehouse'] },
    { module: 'movements', to: '/movements', icon: ArrowLeftRight, label: entityLabel('movements', t.nav.movements), permission: ROUTE_PERMISSIONS['/movements'] },
    { module: 'inbox', to: '/inbox', icon: MessageCircle, label: entityLabel('inbox', t.nav.inbox), permission: ROUTE_PERMISSIONS['/inbox'] },
    { module: 'bots', to: '/bots', icon: Bot, label: entityLabel('bots', t.nav.bots), permission: ROUTE_PERMISSIONS['/bots'] },
    { module: 'integrations', to: '/integrations', icon: Plug, label: t.nav.integrations, permission: ROUTE_PERMISSIONS['/integrations'] },
    { module: 'accounting', to: '/accounting', icon: Calculator, label: entityLabel('accounting', t.nav.accounting), permission: ROUTE_PERMISSIONS['/accounting'] },
    { module: 'accounting', to: '/accounting/settings', icon: Settings, label: t.nav.rsge, permission: ROUTE_PERMISSIONS['/accounting/settings'] },
    { module: 'cabinet', to: '/cabinet', icon: Settings2, label: t.nav.cabinet, permission: PERM.dashboard },
    { module: 'users', to: '/users', icon: UserCog, label: t.nav.users, permission: PERM.usersManage },
  ].filter((item) => moduleEnabled(item.module) && can(item.permission))

  const roleLabel = user ? (ROLE_LABELS[user.role]?.[locale] || ROLE_LABELS[user.role]?.ru || user.role) : ''

  return (
    <>
      <div className="p-5 border-b border-kinetix-700">
        <a href="https://kinetiks.online/" target="_blank" rel="noopener" className="block hover:opacity-90 transition-opacity">
          <h1 className="text-xl font-bold tracking-tight">KINETIKS</h1>
          <p className="text-kinetix-300 text-xs mt-1">{t.app.tagline}</p>
        </a>
        {user && (
          <div className="mt-3 text-xs text-kinetix-200">
            <div className="font-medium truncate">{user.tenant.name}</div>
            <div className="truncate">{user.full_name}</div>
            <div className="text-kinetix-400 truncate">{roleLabel} · {user.tenant.slug}</div>
          </div>
        )}
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
      <div className="p-3 border-t border-kinetix-700">
        <button
          type="button"
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-kinetix-200 hover:bg-kinetix-700 hover:text-white transition-colors"
        >
          <LogOut size={18} />
          {t.auth.logout}
        </button>
      </div>
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
            <a href="https://kinetiks.online/" target="_blank" rel="noopener" className="font-bold truncate text-app-text hover:text-kinetix-600">KINETIKS</a>
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
