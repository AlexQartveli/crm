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

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <>
      <div className="p-5 border-b border-kinetix-700">
        <h1 className="text-xl font-bold tracking-tight">Kinetix</h1>
        <p className="text-kinetix-300 text-xs mt-1">CRM + Склад</p>
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
    <div className="flex min-h-screen">
      <aside className="hidden md:flex w-60 bg-kinetix-800 text-white flex-col shrink-0">
        <Sidebar />
      </aside>

      {menuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setMenuOpen(false)} />
          <aside className="relative w-64 h-full bg-kinetix-800 text-white flex flex-col">
            <button
              onClick={() => setMenuOpen(false)}
              className="absolute top-4 right-4 p-1 text-kinetix-200 hover:text-white"
            >
              <X size={22} />
            </button>
            <Sidebar onNavigate={() => setMenuOpen(false)} />
          </aside>
        </div>
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="md:hidden flex items-center gap-3 bg-kinetix-800 text-white px-4 py-3 shrink-0">
          <button onClick={() => setMenuOpen(true)} className="p-1">
            <Menu size={22} />
          </button>
          <span className="font-bold">Kinetix</span>
        </header>
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
