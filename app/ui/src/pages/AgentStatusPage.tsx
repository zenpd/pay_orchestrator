import { Bot, CheckCircle2, AlertCircle, Clock } from 'lucide-react'

export function AgentStatusPage() {
  const agents = [
    {
      name: 'Policy Reasoner Agent',
      status: 'active' as const,
      uptime: '99.8%',
      lastCheck: '2 seconds ago',
      tasks: 1247,
      description: 'Compliance and regulatory validation',
    },
    {
      name: 'Optimizer Agent',
      status: 'active' as const,
      uptime: '99.9%',
      lastCheck: '1 second ago',
      tasks: 2841,
      description: 'Multi-objective rail selection and scoring',
    },
    {
      name: 'Context Collector Agent',
      status: 'active' as const,
      uptime: '99.7%',
      lastCheck: '3 seconds ago',
      tasks: 1923,
      description: 'Payment context enrichment and analysis',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-3">
            <Bot size={28} className="text-indigo-600" />
            Agent Status
          </h1>
          <p className="page-subtitle">LangGraph agent orchestration status and performance</p>
        </div>
      </div>

      {/* System Status Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center gap-3 mb-2">
              <CheckCircle2 size={20} className="text-green-600" />
              <p className="text-sm text-gray-600">Active Agents</p>
            </div>
            <p className="text-3xl font-bold text-gray-900">3/3</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center gap-3 mb-2">
              <Clock size={20} className="text-blue-600" />
              <p className="text-sm text-gray-600">Avg Response Time</p>
            </div>
            <p className="text-3xl font-bold text-gray-900">142ms</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center gap-3 mb-2">
              <AlertCircle size={20} className="text-amber-600" />
              <p className="text-sm text-gray-600">System Health</p>
            </div>
            <p className="text-3xl font-bold text-gray-900">99.8%</p>
          </div>
        </div>
      </div>

      {/* Individual Agent Status */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Bot size={20} />
          Active Agents
        </h2>

        {agents.map(agent => (
          <div key={agent.name} className="card">
            <div className="card-body">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                    {agent.name}
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-green-100">
                      <span className="w-2 h-2 rounded-full bg-green-600 animate-pulse" />
                      <span className="text-xs font-semibold text-green-700">{agent.status}</span>
                    </span>
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">{agent.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-gray-100">
                <div>
                  <p className="text-xs text-gray-500 uppercase mb-1">Uptime</p>
                  <p className="font-semibold text-gray-900">{agent.uptime}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase mb-1">Last Check</p>
                  <p className="font-semibold text-gray-900">{agent.lastCheck}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase mb-1">Tasks Processed</p>
                  <p className="font-semibold text-gray-900">{agent.tasks}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase mb-1">Status</p>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="font-semibold text-green-700 text-sm">Healthy</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Agent Workflow Diagram */}
      <div className="card">
        <div className="card-header">
          <h3>Agent Workflow Pipeline</h3>
        </div>
        <div className="card-body">
          <div className="flex items-center justify-between">
            <div className="flex-1 text-center">
              <div className="w-12 h-12 rounded-lg bg-indigo-100 flex items-center justify-center mx-auto mb-2">
                <span className="font-bold text-indigo-600">1</span>
              </div>
              <p className="text-sm font-semibold text-gray-900">Context Collector</p>
              <p className="text-xs text-gray-500 mt-1">Gather payment data</p>
            </div>

            <div className="hidden sm:block flex-1 h-1 bg-gradient-to-r from-indigo-300 to-indigo-600" />

            <div className="flex-1 text-center">
              <div className="w-12 h-12 rounded-lg bg-indigo-100 flex items-center justify-center mx-auto mb-2">
                <span className="font-bold text-indigo-600">2</span>
              </div>
              <p className="text-sm font-semibold text-gray-900">Policy Reasoner</p>
              <p className="text-xs text-gray-500 mt-1">Compliance check</p>
            </div>

            <div className="hidden sm:block flex-1 h-1 bg-gradient-to-r from-indigo-300 to-indigo-600" />

            <div className="flex-1 text-center">
              <div className="w-12 h-12 rounded-lg bg-indigo-100 flex items-center justify-center mx-auto mb-2">
                <span className="font-bold text-indigo-600">3</span>
              </div>
              <p className="text-sm font-semibold text-gray-900">Optimizer</p>
              <p className="text-xs text-gray-500 mt-1">Select optimal rail</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
