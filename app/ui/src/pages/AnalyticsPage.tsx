import { BarChart3, TrendingUp, ActivitySquare, Zap } from 'lucide-react'

export function AnalyticsPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-3">
            <BarChart3 size={28} className="text-indigo-600" />
            Analytics Dashboard
          </h1>
          <p className="page-subtitle">Payment orchestration metrics and performance</p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={ActivitySquare}
          label="Total Orchestrations"
          value="2,847"
          change="+12.5%"
          positive
        />
        <MetricCard
          icon={TrendingUp}
          label="Avg Speed Score"
          value="87.3"
          change="+2.1%"
          positive
        />
        <MetricCard
          icon={Zap}
          label="Rail Efficiency"
          value="94.2%"
          change="-0.3%"
          positive={false}
        />
        <MetricCard
          icon={ActivitySquare}
          label="Cost Optimization"
          value="$12.4K"
          change="+8.7%"
          positive
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h3>Payment Rails Usage</h3>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              {[
                { name: 'SWIFT GPI', usage: 45, color: 'bg-indigo-500' },
                { name: 'Real-Time Payments', usage: 28, color: 'bg-blue-500' },
                { name: 'ACH Batch', usage: 18, color: 'bg-green-500' },
                { name: 'SEPA', usage: 9, color: 'bg-purple-500' },
              ].map(rail => (
                <div key={rail.name} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-gray-700">{rail.name}</span>
                    <span className="text-gray-600">{rail.usage}%</span>
                  </div>
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className={`h-full ${rail.color}`} style={{ width: `${rail.usage}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Regional Distribution</h3>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              {[
                { region: 'US', transactions: 1247, color: 'bg-indigo-100', text: 'text-indigo-700' },
                { region: 'UK', transactions: 834, color: 'bg-blue-100', text: 'text-blue-700' },
                { region: 'SA', transactions: 512, color: 'bg-green-100', text: 'text-green-700' },
                { region: 'EUR', transactions: 254, color: 'bg-purple-100', text: 'text-purple-700' },
              ].map(item => (
                <div key={item.region} className={`${item.color} rounded-lg p-3`}>
                  <div className="flex justify-between items-center">
                    <span className={`font-semibold ${item.text}`}>{item.region}</span>
                    <span className={`text-sm font-bold ${item.text}`}>{item.transactions}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

interface MetricCardProps {
  icon: any
  label: string
  value: string
  change: string
  positive: boolean
}

function MetricCard({ icon: Icon, label, value, change, positive }: MetricCardProps) {
  return (
    <div className="card">
      <div className="card-body">
        <div className="flex items-start justify-between mb-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
            <Icon size={20} className="text-indigo-600" />
          </div>
          <span className={`text-xs font-semibold ${positive ? 'text-green-600' : 'text-red-600'}`}>
            {change}
          </span>
        </div>
        <p className="text-sm text-gray-600 mb-1">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  )
}
