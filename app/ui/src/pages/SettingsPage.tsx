import { Settings, Mail, Bell, Lock, Zap } from 'lucide-react'
import { useState } from 'react'

export function SettingsPage() {
  const [settings, setSettings] = useState({
    apiKey: '••••••••••••••••',
    notifications: true,
    emailAlerts: true,
    autoOptimize: true,
  })

  return (
    <div className="space-y-8 max-w-2xl">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-3">
            <Settings size={28} className="text-indigo-600" />
            Settings
          </h1>
          <p className="page-subtitle">Configure orchestrator preferences and integrations</p>
        </div>
      </div>

      {/* API Configuration */}
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <Lock size={18} />
          <h3>API Configuration</h3>
        </div>
        <div className="card-body space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">API Key</label>
            <div className="flex gap-2">
              <input
                type="password"
                value={settings.apiKey}
                readOnly
                className="input flex-1"
              />
              <button className="btn btn-secondary">Copy</button>
            </div>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Backend URL</label>
            <input
              type="text"
              defaultValue="http://localhost:8005"
              className="input"
              readOnly
            />
          </div>
          <button className="btn btn-primary">Regenerate API Key</button>
        </div>
      </div>

      {/* Notifications */}
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <Bell size={18} />
          <h3>Notifications</h3>
        </div>
        <div className="card-body space-y-4">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={settings.notifications}
              onChange={e => setSettings({ ...settings, notifications: e.target.checked })}
              className="w-4 h-4 rounded"
            />
            <span className="text-gray-700">Enable push notifications</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={settings.emailAlerts}
              onChange={e => setSettings({ ...settings, emailAlerts: e.target.checked })}
              className="w-4 h-4 rounded"
            />
            <span className="text-gray-700">Email alerts for orchestrations</span>
          </label>
        </div>
      </div>

      {/* Optimization */}
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <Zap size={18} />
          <h3>Optimization</h3>
        </div>
        <div className="card-body space-y-4">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={settings.autoOptimize}
              onChange={e => setSettings({ ...settings, autoOptimize: e.target.checked })}
              className="w-4 h-4 rounded"
            />
            <span className="text-gray-700">Auto-optimize rail selection</span>
          </label>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Cost Weight
            </label>
            <input type="range" min="0" max="100" defaultValue="30" className="w-full" />
            <p className="text-xs text-gray-500 mt-1">30% of optimization score</p>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Speed Weight
            </label>
            <input type="range" min="0" max="100" defaultValue="40" className="w-full" />
            <p className="text-xs text-gray-500 mt-1">40% of optimization score</p>
          </div>
        </div>
      </div>

      <button className="btn btn-primary w-full">Save Settings</button>
    </div>
  )
}
