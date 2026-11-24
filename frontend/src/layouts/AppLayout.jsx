import React, { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { ShieldCheck, LayoutDashboard, UploadCloud, History, Settings, LogOut, Menu, X } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/upload', label: 'Upload & Analyze', icon: UploadCloud },
  { to: '/history', label: 'Analysis History', icon: History },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function AppLayout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex bg-base-950">
      {/* Mobile top bar */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-30 flex items-center justify-between px-4 py-3 bg-base-900 border-b border-base-700">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-accent-500" size={22} />
          <span className="font-bold text-slate-100">TruthLens AI</span>
        </div>
        <button onClick={() => setOpen(!open)} aria-label="Toggle menu" className="text-slate-300">
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={`fixed md:sticky top-0 left-0 h-screen w-64 bg-base-900 border-r border-base-700 flex flex-col z-20 transition-transform duration-200
        ${open ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 pt-16 md:pt-0`}
      >
        <div className="hidden md:flex items-center gap-2 px-6 py-6 border-b border-base-700">
          <ShieldCheck className="text-accent-500" size={26} />
          <span className="font-bold text-lg text-slate-100">TruthLens AI</span>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-accent-500/10 text-accent-500 border border-accent-500/30' : 'text-slate-400 hover:bg-base-800 hover:text-slate-200'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 py-4 border-t border-base-700">
          <div className="px-3 py-2 mb-2">
            <p className="text-sm font-medium text-slate-200 truncate">{user?.name}</p>
            <p className="text-xs text-slate-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-sm font-medium text-slate-400 hover:bg-base-800 hover:text-red-400 transition-colors"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </aside>

      {open && (
        <div className="fixed inset-0 bg-black/50 z-10 md:hidden" onClick={() => setOpen(false)} />
      )}

      <main className="flex-1 min-w-0 pt-16 md:pt-0">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">{children}</div>
      </main>
    </div>
  )
}
