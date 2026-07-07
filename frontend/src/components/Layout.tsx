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
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Дашборд' },
  { to: '/leads', icon: UserPlus, label: 'Лиды' },
  { to: '/deals', icon: Handshake, label: 'Сделки' },
  { to: '/contacts', icon: Users, label: 'Контакты' },
  { to: '/companies', icon: Building2, label: 'Компании' },
  { to: '/products', icon: Package, label: 'Товары' },
  { to: '/warehouse', icon: Warehouse, label: 'Склад' },
  { to: '/movements', icon: ArrowLeftRight, label: 'Движения' },
]

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      <aside className="w-60 bg-bitrix-800 text-white flex flex-col shrink-0">
        <div className="p-5 border-b border-bitrix-700">
          <h1 className="text-xl font-bold tracking-tight">BitrixCRM</h1>
          <p className="text-bitrix-300 text-xs mt-1">CRM + Склад</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-bitrix-600 text-white'
                    : 'text-bitrix-200 hover:bg-bitrix-700 hover:text-white'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
