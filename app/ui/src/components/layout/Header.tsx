import { Bell, Settings } from 'lucide-react'

export default function Header() {
  return (
    <header className="fixed top-0 left-60 right-0 h-16 bg-white/80 backdrop-blur-xl shadow-header z-30 border-b border-gray-100/80">
      <div className="h-full px-6 flex items-center justify-between">
        {/* Title */}
        <div>
          <h1 className="text-lg font-semibold text-gray-900">Payment Orchestrator</h1>
          <p className="text-xs text-gray-500">AI-powered payment routing & optimization</p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4">
          <button className="relative p-2 text-gray-500 hover:text-gray-700 transition-colors">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-red-500" />
          </button>
          <button className="p-2 text-gray-500 hover:text-gray-700 transition-colors">
            <Settings size={20} />
          </button>
        </div>
      </div>
    </header>
  )
}
