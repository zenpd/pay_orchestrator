import { Zap, DollarSign, Clock, TrendingUp } from 'lucide-react'
import { useState, useEffect } from 'react'

interface Rail {
  name: string
  speed: number
  cost: number
  reliability: number
  cost_usd: number
  time_hours: number
}

interface AvailableRailsProps {
  region: string
}

export function AvailableRails({ region }: AvailableRailsProps) {
  const [rails, setRails] = useState<{ [key: string]: Rail }>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetch(`http://localhost:8005/api/v1/payment/regions/${region}/rails`)
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
                    <p className="text-sm font-bold text-indigo-600">${rail.cost_usd.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">per transaction</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  {/* Speed */}
                  <div className="flex items-center gap-2">
                    <Clock size={16} className={getSpeedColor(rail.speed)} />
                    <div>
                      <p className="text-xs text-gray-500">Speed</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {rail.time_hours < 1 ? `${(rail.time_hours * 60).toFixed(0)}m` : `${rail.time_hours}h`}
                      </p>
                      <div className="w-16 h-1.5 bg-gray-200 rounded-full mt-1 overflow-hidden">
                        <div
                          className={`h-full ${rail.speed >= 90 ? 'bg-green-500' : rail.speed >= 75 ? 'bg-blue-500' : 'bg-amber-500'}`}
                          style={{ width: `${rail.speed}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Cost Efficiency */}
                  <div className="flex items-center gap-2">
                    <DollarSign size={16} className={getCostColor(rail.cost)} />
                    <div>
                      <p className="text-xs text-gray-500">Cost</p>
                      <p className="text-sm font-semibold text-gray-900">{rail.cost}/100</p>
                      <div className="w-16 h-1.5 bg-gray-200 rounded-full mt-1 overflow-hidden">
                        <div
                          className={`h-full ${rail.cost >= 85 ? 'bg-green-500' : rail.cost >= 60 ? 'bg-blue-500' : 'bg-red-500'}`}
                          style={{ width: `${rail.cost}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Reliability */}
                  <div className="flex items-center gap-2">
                    <TrendingUp size={16} className="text-purple-600" />
                    <div>
                      <p className="text-xs text-gray-500">Reliability</p>
                      <p className="text-sm font-semibold text-gray-900">{rail.reliability}%</p>
                      <div className="w-16 h-1.5 bg-gray-200 rounded-full mt-1 overflow-hidden">
                        <div
                          className="h-full bg-purple-500"
                          style={{ width: `${rail.reliability}%` }}
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
