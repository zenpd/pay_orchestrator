import React from 'react'
import { PaymentResponse } from '../types'

interface PaymentResultProps {
  result: PaymentResponse
}

export const PaymentResult: React.FC<PaymentResultProps> = ({ result }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">Orchestration Result</h2>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-gray-600 text-sm">Session ID</p>
          <p className="font-mono text-xs">{result.session_id.substring(0, 12)}...</p>
        </div>
        <div>
          <p className="text-gray-600 text-sm">Status</p>
          <p className="font-semibold capitalize">{result.stage}</p>
        </div>
        <div>
          <p className="text-gray-600 text-sm">Selected Rail</p>
          <p className="font-semibold">{result.selected_rail || 'N/A'}</p>
        </div>
        <div>
          <p className="text-gray-600 text-sm">Total Cost</p>
          <p className="font-semibold">
            ${(result.rail_scores[result.selected_rail || '']?.estimated_cost_usd ?? 0).toFixed(2)}
          </p>
        </div>
      </div>

      {result.execution_result && (
        <div className="bg-green-50 border border-green-200 rounded p-4 mb-4">
          <p className="font-semibold text-green-800 mb-2">Transaction Submitted</p>
          <p className="text-sm text-gray-700">
            Transaction ID: <span className="font-mono">{result.execution_result.transaction_id}</span>
          </p>
        </div>
      )}

      {result.errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <p className="font-semibold text-red-800 mb-2">Errors</p>
          <ul className="text-sm text-red-700 list-disc list-inside">
            {result.errors.map((error, idx) => (
              <li key={idx}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4">
        <p className="text-gray-600 text-sm mb-2">Messages</p>
        <ul className="text-xs space-y-1 bg-gray-50 p-3 rounded">
          {result.messages.map((msg, idx) => (
            <li key={idx} className="text-gray-700">
              • {msg}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
