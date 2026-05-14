import React, { useState, useEffect } from 'react'
import { Sparkles, RefreshCw } from 'lucide-react'
import { PaymentRequest } from '../types'
import { usePaymentOrchestration } from '../hooks/usePayment'
import AgentOrchestrationFlow from '../components/orchestration/AgentOrchestrationFlow'
import RailScoresTable, { type RailScore } from '../components/orchestration/RailScoresTable'
import PaymentResult from '../components/orchestration/PaymentResult'
import DecisionJustificationPanel from '../components/orchestration/DecisionJustificationPanel'
import { AvailableRails } from '../components/orchestration/AvailableRails'
import { RegionFilter } from '../components/orchestration/RegionFilter'

const MOCK_RAILS: RailScore[] = [
  {
    name: 'SWIFT_GPI',
    compositeScore: 92,
    costScore: 70,
    speedScore: 95,
    reliabilityScore: 95,
    estimatedTime: '2-4 hours',
    estimatedCost: 15.50,
    isOptimal: true,
  },
  {
    name: 'NAMPAY',
    compositeScore: 78,
    costScore: 85,
    speedScore: 75,
    reliabilityScore: 78,
    estimatedTime: '1-2 days',
    estimatedCost: 8.00,
  },
  {
    name: 'PARTNER_NETWORK',
    compositeScore: 65,
    costScore: 95,
    speedScore: 60,
    reliabilityScore: 65,
    estimatedTime: '3-5 days',
    estimatedCost: 2.50,
  },
  {
    name: 'RTGS_BULK',
    compositeScore: 72,
    costScore: 65,
    speedScore: 85,
    reliabilityScore: 70,
    estimatedTime: 'Same day',
    estimatedCost: 12.00,
  },
  {
    name: 'BATCH_ACH',
    compositeScore: 68,
    costScore: 90,
    speedScore: 70,
    reliabilityScore: 68,
    estimatedTime: '1-3 days',
    estimatedCost: 0.50,
  },
  {
    name: 'SLOW_BATCH',
    compositeScore: 55,
    costScore: 100,
    speedScore: 50,
    reliabilityScore: 55,
    estimatedTime: '5-7 days',
    estimatedCost: 0.25,
  },
]

const WORKFLOW_STEPS: Array<{ id: string; name: string; label: string; status: 'pending' | 'active' | 'complete'; icon: null }> = [
  { id: 'analyze', name: 'analyze_payment', label: 'Analyze Payment Parameters', status: 'pending', icon: null },
  { id: 'score', name: 'score_rails', label: 'Evaluate Payment Rails', status: 'pending', icon: null },
  { id: 'select', name: 'select_rail', label: 'Select Optimal Route', status: 'pending', icon: null },
  { id: 'execute', name: 'execute_payment', label: 'Execute Payment', status: 'pending', icon: null },
]

export const OrchestratorPage: React.FC = () => {
  const { orchestrate, loading, error, result } = usePaymentOrchestration()
  const [region, setRegion] = useState('US')
  const [corridors, setCorridors] = useState<Record<string, string>>({ 'US_UK': 'USA → UK' })
  const [currencies, setCurrencies] = useState<string[]>(['USD'])
  const [formData, setFormData] = useState<PaymentRequest>({
    amount: 50000,
    currency: 'USD',
    sender_id: 'ACC-001',
    receiver_id: 'ACC-002',
    corridor: 'US_UK',
    region: 'US',
  })
  const [workflowSteps, setWorkflowSteps] = useState(WORKFLOW_STEPS)
  const [hasSubmitted, setHasSubmitted] = useState(false)

  // Load regional data on region change
  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL ?? ''}/api/v1/payment/regions/${region}/rails`)
      .then(res => res.json())
      .then(data => {
        if (data.corridors) setCorridors(data.corridors)
        if (data.currencies) setCurrencies(data.currencies)
        setFormData(prev => ({
          ...prev,
          region,
          corridor: Object.keys(data.corridors || {})[0] || 'US_UK',
          currency: data.currencies?.[0] || 'USD',
        }))
      })
      .catch(err => console.error('Error loading regional data:', err))
  }, [region])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setHasSubmitted(true)
    
    // Simulate workflow step updates
    const steps = [...WORKFLOW_STEPS]
    steps[0].status = 'active'
    setWorkflowSteps(steps)

    setTimeout(() => {
      steps[0].status = 'complete'
      steps[1].status = 'active'
      setWorkflowSteps([...steps])

      setTimeout(() => {
        steps[1].status = 'complete'
        steps[2].status = 'active'
        setWorkflowSteps([...steps])

        setTimeout(() => {
          steps[2].status = 'complete'
          steps[3].status = 'active'
          setWorkflowSteps([...steps])

          setTimeout(() => {
            steps[3].status = 'complete'
            setWorkflowSteps([...steps])
          }, 800)
        }, 800)
      }, 800)
    }, 600)

    setTimeout(async () => {
      await orchestrate(formData)
    }, 3000)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'amount' ? parseFloat(value) : value,
    }))
    setHasSubmitted(false)
  }

  return (
    <>
      {/* Page Header */}
      <div className="page-header mb-8">
        <div>
          <h1 className="page-title flex items-center gap-3">
            <Sparkles size={28} className="text-indigo-600" />
            Payment Orchestration
          </h1>
          <p className="page-subtitle">AI-powered payment routing with optimal rail selection</p>
        </div>
        <button className="btn btn-secondary btn-sm">
          <RefreshCw size={16} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Form & Flow */}
        <div className="lg:col-span-1 space-y-6">
          {/* Region Filter */}
          <RegionFilter selectedRegion={region} onRegionChange={setRegion} />

          {/* Available Rails */}
          <AvailableRails region={region} />

          {/* Payment Form */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-sm font-semibold">New Payment ({region})</h3>
            </div>
            <form onSubmit={handleSubmit} className="card-body space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase">Amount</label>
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleChange}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase">Currency</label>
                <select
                  name="currency"
                  value={formData.currency}
                  onChange={handleChange}
                  className="input"
                >
                  {currencies.map(curr => (
                    <option key={curr} value={curr}>{curr}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase">Sender ID</label>
                <input
                  type="text"
                  name="sender_id"
                  value={formData.sender_id}
                  onChange={handleChange}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase">Receiver ID</label>
                <input
                  type="text"
                  name="receiver_id"
                  value={formData.receiver_id}
                  onChange={handleChange}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase">Corridor</label>
                <select
                  name="corridor"
                  value={formData.corridor}
                  onChange={handleChange}
                  className="input"
                >
                  {Object.entries(corridors).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full btn btn-primary mt-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                    Orchestrating...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    Orchestrate Payment
                  </>
                )}
              </button>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-xs font-medium text-red-700">{error}</p>
                </div>
              )}
            </form>
          </div>

          {/* Agent Flow */}
          {hasSubmitted && (
            <AgentOrchestrationFlow steps={workflowSteps} />
          )}
        </div>

        {/* Right Column: Results */}
        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <>
              {/* Payment Result */}
              <PaymentResult
                transactionId={result.execution_result?.transaction_id || 'TXN-' + Date.now()}
                amount={formData.amount}
                currency={formData.currency}
                selectedRail={result.selected_rail || 'SWIFT_GPI'}
                estimatedTime="2-4 hours"
                estimatedCost={15.5}
                compositeScore={92}
              />

              {/* Decision Justification */}
              {result.decision_justification && (
                <DecisionJustificationPanel
                  selectedRail={result.selected_rail || 'UNKNOWN'}
                  amount={formData.amount}
                  currency={formData.currency}
                  justification={result.decision_justification}
                  compliance={result.compliance_validation || { status: 'UNKNOWN', risk_score: 0, checks_passed: [], warnings: [] }}
                />
              )}

              {/* Rail Scores */}
              {result.rail_scores && (
                <RailScoresTable
                  rails={Object.entries(result.rail_scores).map(([key, r]) => {
                    return {
                      name: key,
                      compositeScore: r.composite_score,
                      costScore: r.cost_score,
                      speedScore: r.speed_score,
                      reliabilityScore: r.reliability_score,
                      estimatedTime: r.estimated_time_hours ? `${r.estimated_time_hours} hours` : '2-4 hours',
                      estimatedCost: r.estimated_cost_usd,
                      isOptimal: key === result.selected_rail,
                    }
                  })}
                  selectedRail={result.selected_rail}
                />
              )}
            </>
          ) : (
            <div className="card">
              <div className="card-body text-center py-12">
                <div className="w-16 h-16 rounded-full bg-indigo-50 flex items-center justify-center mx-auto mb-4">
                  <Sparkles size={24} className="text-indigo-600" />
                </div>
                <p className="text-sm text-gray-600">Submit a payment to see orchestration results</p>
                <p className="text-xs text-gray-500 mt-2">Our AI agents will analyze and select the optimal payment route</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
