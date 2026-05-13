import React, { useState } from 'react'
import { PaymentRequest } from '../types'
import { usePaymentOrchestration } from '../hooks/usePayment'
import { RailScoresTable } from '../components/RailScoresTable'
import { PaymentResult } from '../components/PaymentResult'

export const OrchestratorPage: React.FC = () => {
  const { orchestrate, loading, error, result } = usePaymentOrchestration()
  const [formData, setFormData] = useState<PaymentRequest>({
    amount: 50000,
    currency: 'USD',
    sender_id: 'ACC-001',
    receiver_id: 'ACC-002',
    corridor: 'ZA_US',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await orchestrate(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'amount' ? parseFloat(value) : value,
    }))
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Payment Orchestrator</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">New Payment</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Amount</label>
              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                className="w-full border rounded px-3 py-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Currency</label>
              <select
                name="currency"
                value={formData.currency}
                onChange={handleChange}
                className="w-full border rounded px-3 py-2"
              >
                <option>USD</option>
                <option>EUR</option>
                <option>ZAR</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Sender ID</label>
              <input
                type="text"
                name="sender_id"
                value={formData.sender_id}
                onChange={handleChange}
                className="w-full border rounded px-3 py-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Receiver ID</label>
              <input
                type="text"
                name="receiver_id"
                value={formData.receiver_id}
                onChange={handleChange}
                className="w-full border rounded px-3 py-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Corridor</label>
              <select
                name="corridor"
                value={formData.corridor}
                onChange={handleChange}
                className="w-full border rounded px-3 py-2"
              >
                <option>ZA_US</option>
                <option>ZA_GB</option>
                <option>US_GB</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white rounded py-2 font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Orchestrate Payment'}
            </button>
          </form>

          {error && <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded">{error}</div>}
        </div>

        {/* Results */}
        <div>
          {result ? (
            <>
              <PaymentResult result={result} />
              <div className="mt-6 bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold mb-4">Rail Evaluation Scores</h3>
                <RailScoresTable scores={result.rail_scores} selectedRail={result.selected_rail} />
              </div>
            </>
          ) : (
            <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-500">
              <p>Submit a payment to see orchestration results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
