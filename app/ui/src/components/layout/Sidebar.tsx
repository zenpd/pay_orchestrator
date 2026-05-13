import { Plus, Settings, Activity, BarChart3, Zap, Bot } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import clsx from 'clsx'

const BASE_NAV = [
  { label: 'Orchestrate',    icon: Zap,       path: '/' },
  { label: 'Analytics',      icon: BarChart3, path: '/analytics' },
  { label: 'Agent Status',   icon: Bot,       path: '/agents' },
  { label: 'Activity',       icon: Activity,  path: '/activity' },
]

const BOTTOM_NAV = [
  { label: 'Settings', icon: Settings, path: '/settings' },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-white/90 backdrop-blur-xl shadow-sidebar z-40 border-r border-gray-100/80">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-gray-100/80">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-700 shadow-glow flex items-center justify-center ring-2 ring-indigo-500/20">
            <Zap size={18} className="text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-sm text-gray-900">PayFlow</span>
            <span className="text-xs text-gray-500 font-medium">Orchestrator</span>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="px-4 py-6 flex flex-col flex-1 gap-1">
        <div>
          <p className="section-title px-3 mb-3">Navigation</p>
          {BASE_NAV.map(item => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => clsx(
                  'sidebar-link group',
                  isActive && 'active'
                )}
              >
                <Icon size={16} className="opacity-70 group-hover:scale-110 transition-transform" />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </div>

        <div className="flex-1" />

        <div className="space-y-1 pt-4 border-t border-gray-100">
          <p className="section-title px-3 mb-3">System</p>
          {BOTTOM_NAV.map(item => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => clsx(
                  'sidebar-link',
                  isActive && 'active'
                )}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </div>
      </nav>

      {/* Status */}
      <div className="px-4 py-4 border-t border-gray-100/80 space-y-2">
        <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-100/50">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-medium text-emerald-700">All systems operational</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
