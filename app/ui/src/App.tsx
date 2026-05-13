import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import { OrchestratorPage } from './pages/OrchestratorPage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { AgentStatusPage } from './pages/AgentStatusPage'
import { ActivityPage } from './pages/ActivityPage'
import { SettingsPage } from './pages/SettingsPage'
import './index.css'

function App() {
  return (
    <Router>
      <AppShell>
        <Routes>
          <Route path="/" element={<OrchestratorPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/agents" element={<AgentStatusPage />} />
          <Route path="/activity" element={<ActivityPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </Router>
  )
}

export default App
