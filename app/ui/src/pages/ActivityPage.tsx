import { Activity, Zap, Clock, TrendingUp } from 'lucide-react'

export function ActivityPage() {
  const activities = [
    {
      timestamp: '2 minutes ago',
      action: 'Payment Orchestrated',
      details: 'RTP selected for US → UK, $50,000',
      status: 'success' as const,
      icon: Zap,
    },
    {
      timestamp: '5 minutes ago',
      action: 'Compliance Check Passed',
      details: 'AML screening completed, low risk',
      status: 'success' as const,
      icon: Activity,
    },
    {
      timestamp: '8 minutes ago',
      action: 'Rail Optimization',
      details: '4 rails evaluated, SWIFT GPI selected',
      status: 'success' as const,
      icon: TrendingUp,
    },
    {
      timestamp: '12 minutes ago',
      action: 'Context Collection',
      details: 'Payment context enriched with metadata',
      status: 'success' as const,
      icon: Clock,
    },
  ]

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-3">
            <Activity size={28} className="text-indigo-600" />
            Activity Log
          </h1>
          <p className="page-subtitle">Real-time orchestration and agent activity</p>
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="card">
        <div className="card-body">
          <div className="space-y-6">
            {activities.map((activity, idx) => {
              const Icon = activity.icon
              return (
                <div key={idx} className="flex gap-4">
                  <div className="relative">
                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                      <Icon size={18} className="text-green-600" />
                    </div>
                    {idx < activities.length - 1 && (
                      <div className="absolute left-5 top-10 w-0.5 h-8 bg-gray-200" />
                    )}
                  </div>
                  <div className="flex-1 pt-1">
                    <div className="flex items-start justify-between mb-1">
                      <h4 className="font-semibold text-gray-900">{activity.action}</h4>
                      <span className="text-xs text-gray-500">{activity.timestamp}</span>
                    </div>
                    <p className="text-sm text-gray-600">{activity.details}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
