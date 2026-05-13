import { Zap, DollarSign, Clock, Shield } from 'lucide-react'

export interface RailScore {
  name: string
  compositeScore: number
  costScore: number
  speedScore: number
  reliabilityScore: number
  estimatedTime: string
  estimatedCost: number
  isOptimal?: boolean
}

interface RailScoresTableProps {
  rails: RailScore[]
  selectedRail?: string
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'bg-emerald-50'
  if (score >= 60) return 'bg-amber-50'
  return 'bg-red-50'
}

function getScoreBadgeColor(score: number): string {
  if (score >= 80) return 'text-emerald-700 bg-emerald-100'
  if (score >= 60) return 'text-amber-700 bg-amber-100'
  return 'text-red-700 bg-red-100'
}

export default function RailScoresTable({ rails, selectedRail }: RailScoresTableProps) {
  const sortedRails = [...rails].sort((a, b) => b.compositeScore - a.compositeScore)

  return (
    <div className="card overflow-hidden">
      <div className="card-header">
        <h3 className="text-sm font-semibold text-gray-900">Payment Rail Evaluation</h3>
        <p className="text-xs text-gray-500 mt-1">AI-optimized routing recommendations</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50/50">
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Rail</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Score</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Cost</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Speed</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Reliability</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">ETA</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Fee</th>
            </tr>
          </thead>
          <tbody>
            {sortedRails.map((rail, idx) => (
              <tr
                key={rail.name}
                className={`border-b border-gray-100 transition-colors ${
                  rail.isOptimal ? 'bg-indigo-50/50 hover:bg-indigo-50' : 'hover:bg-gray-50'
                }`}
              >
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    {rail.isOptimal && (
                      <Zap size={16} className="text-indigo-600 flex-shrink-0" />
                    )}
                    <span className="font-medium text-gray-900">{rail.name}</span>
                    {idx === 0 && (
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-600 text-white">
                        Optimal
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg font-bold ${getScoreColor(rail.compositeScore)}`}>
                    <span className={`${getScoreBadgeColor(rail.compositeScore)} px-2 py-1 rounded font-semibold`}>
                      {Math.round(rail.compositeScore)}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center">
                      <span className="text-xs font-semibold text-gray-700">{Math.round(rail.costScore)}</span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center">
                      <span className="text-xs font-semibold text-gray-700">{Math.round(rail.speedScore)}</span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center">
                      <span className="text-xs font-semibold text-gray-700">{Math.round(rail.reliabilityScore)}</span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Clock size={14} />
                    <span className="text-xs">{rail.estimatedTime}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2 text-gray-600">
                    <DollarSign size={14} />
                    <span className="text-xs font-medium">${rail.estimatedCost.toFixed(2)}</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card-footer text-xs text-gray-500">
        <p>Scores calculated using composite algorithm: Cost (30%) + Speed (40%) + Reliability (30%)</p>
      </div>
    </div>
  )
}
