import React from 'react'
import { RailScore } from '../types'
import clsx from 'clsx'

interface RailScoresTableProps {
  scores: Record<string, RailScore>
  selectedRail?: string
}

export const RailScoresTable: React.FC<RailScoresTableProps> = ({ scores, selectedRail }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-100 border-b">
          <tr>
            <th className="px-4 py-2 text-left">Rail</th>
            <th className="px-4 py-2 text-right">Score</th>
            <th className="px-4 py-2 text-right">Cost ($)</th>
            <th className="px-4 py-2 text-right">Speed</th>
            <th className="px-4 py-2 text-center">Status</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(scores).map(([railType, score]) => (
            <tr
              key={railType}
              className={clsx(
                'border-b hover:bg-gray-50',
                selectedRail === railType && 'bg-blue-50 font-semibold'
              )}
            >
              <td className="px-4 py-2">{railType}</td>
              <td className={clsx('px-4 py-2 text-right', getScoreColor(score.composite_score))}>
                {score.composite_score.toFixed(1)}
              </td>
              <td className="px-4 py-2 text-right">${score.estimated_cost_usd.toFixed(2)}</td>
              <td className="px-4 py-2 text-right">{score.estimated_time_hours}h</td>
              <td className="px-4 py-2 text-center">
                {selectedRail === railType ? (
                  <span className="inline-block bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                    Selected
                  </span>
                ) : (
                  <span className="text-gray-500">·</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
