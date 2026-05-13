import { CheckCircle2, Circle, Zap, TrendingUp, Database, Rocket } from 'lucide-react'

interface OrchestrationStep {
  id: string
  name: string
  label: string
  status: 'pending' | 'active' | 'complete' | 'error'
  icon: React.ReactNode
}

interface AgentOrchestrationFlowProps {
  steps: OrchestrationStep[]
}

export default function AgentOrchestrationFlow({ steps }: AgentOrchestrationFlowProps) {
  const icons: Record<string, React.ReactNode> = {
    analyze: <Database size={20} />,
    score: <TrendingUp size={20} />,
    select: <Zap size={20} />,
    execute: <Rocket size={20} />,
  }

  return (
    <div className="card p-6">
      <div className="mb-4">
        <h3 className="section-title">Agent Orchestration Flow</h3>
      </div>

      <div className="space-y-3">
        {steps.map((step, idx) => (
          <div key={step.id}>
            <div className="flex items-center gap-4">
              {/* Node */}
              <div className="relative flex-shrink-0">
                {step.status === 'complete' ? (
                  <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center">
                    <CheckCircle2 size={24} className="text-emerald-600" />
                  </div>
                ) : step.status === 'active' ? (
                  <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center animate-pulse">
                    <div className="w-6 h-6 text-indigo-600">
                      {icons[step.id] || <Circle size={20} />}
                    </div>
                  </div>
                ) : (
                  <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                    <Circle size={20} className="text-gray-400" />
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{step.label}</p>
                    <p className="text-xs text-gray-500">
                      {step.status === 'active' && 'Processing...'}
                      {step.status === 'complete' && 'Completed'}
                      {step.status === 'pending' && 'Waiting...'}
                      {step.status === 'error' && 'Failed'}
                    </p>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded ${
                    step.status === 'complete' ? 'badge-success' :
                    step.status === 'active' ? 'bg-indigo-50 text-indigo-600' :
                    step.status === 'error' ? 'badge-error' :
                    'bg-gray-50 text-gray-600'
                  }`}>
                    {step.status}
                  </span>
                </div>
              </div>
            </div>

            {/* Connection line */}
            {idx < steps.length - 1 && (
              <div className="ml-5 h-4 border-l border-dashed border-gray-200" />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
