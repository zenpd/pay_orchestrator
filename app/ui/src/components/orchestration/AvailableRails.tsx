import { Zap, DollarSign, Clock, TrendingUp } from 'lucide-react'
import { useState, useEffect } from 'react'

interface Rail {
  name: string
  speed_score: number
  cost_score: number
  reliability_score: number
  estimated_cost_usd: number
  estimated_time_hours: number
}

interface AvailableRailsProps {
  region: string
}

export function AvailableRails({ region }: AvailableRailsProps) {
  const [rails, setRails] = useState<{ [key: string]: Rail }>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetch(`${import.meta.env.VITE_API_BASE_URL ?? ''}/api/v1/payment/regions/${region}/rails`)
      .then(res => res.json())
      .then(data => {
        if (data.rails) setRails(data.rails)
      })
      .catch(err => console.error('Error loading rails:', err))
      .finally(() => setLoading(false))
  }, [region])

  const railList = Object.entries(rails).map(([key, rail]) => ({
    key,
    ...rail,
  }))

  const getSpeedColor = (speed: number) => {
    if (speed >= 90) return 'text-green-600'
    if (speed >= 75) return 'text-blue-600'
    return 'text-amber-600'
  }

  const getCostColor = (cost: number) => {
    if (cost >= 85) return 'text-green-600'
    if (cost >= 60) return 'text-blue-600'
    return 'text-red-600'
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="flex items-center gap-2">
          <Zap size={18} className="text-indigo-600" />
          Available Payment Rails - {region}
        </h3>
      </div>
      <div className="card-body">
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin h-8 w-8 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto" />
          </div>
        ) : railList.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No rails available for this region</p>
        ) : (
          <div className="space-y-3">
            {railList.map(rail => (
              <div key={rail.key} className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 hover:bg-indigo-50/30 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">{rail.name}</h4>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-indigo-600">${(rail.estimated_cost_usd ?? 0).toFixed(2)}</p>
                    <p className="text-xs text-gray-500">per transaction</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  {/* Speed */}
                  <div className="flex items-center gap-2">
                    <Clock size={16} className={getSpeedColor(rail.speed_score)} />
                    <div>
                      <p className="text-xs text-gray-500">Speed</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {(rail.estimated_time_hours ?? 0) < 1 ? `${((rail.estimated_time_hours ?? 0) * 60).toFixed(0)}m` : `${rail.estimated_time_hours}h`}
                      </p>
                      <div className="w-16 h-1.5 bg-gray-200 rounded-full mt-1 overflow-hidden">
                        <div
                          className={`h-full ${rail.speed_score >= 90 ? 'bg-green-500' : rail.speed_score >= 75 ? 'bg-blue-500' : 'bg-amber-500'}`}
                          style={{ width: `${rail.speed_score}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Cost Efficiency */}
                  <div className="flex items-center gap-2">
                    <DollarSign size={16} className={getCostColor(rail.cost_score)} />
                    <div>
                      <p className="text-xs text-gray-500">Cost</p>
                      <p className="text-sm font-semibold text-gray-900">{rail.cost_score}/100</p>
                      <div className="w-16 h-1.5 bg-gray-200 rounded-full mt-1 overflow-hidden">
                        <div
                          className={`h-full ${rail.cost_score >= 85 ? 'bg-green-500' : rail.cost_score >= 60 ? 'bg-blue-500' : 'bg-red-500'}`}
                          style={{ width: `${rail.cost_score}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Reliability */}
                  <div className="flex items-center gap-2">
                    <TrendingUp size={16} className="text-purple-600" />
                    <div>
                      <p className="text-xs text-gray-500">Reliability</p>
                      <p className="text-sm font-semibold text-gray-900">{rail.reliability_score}%</p>
                      <div className="w-16 h-1.5 bg-gray-200 rounded-full mt-1 overflow-hidden">
                        <div
                          className="h-full bg-purple-500"
                          style={{ width: `${rail.reliability_score}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
