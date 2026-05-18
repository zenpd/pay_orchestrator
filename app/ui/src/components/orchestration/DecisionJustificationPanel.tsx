import { AlertCircle, CheckCircle2, TrendingUp, DollarSign, Clock, Shield, ChevronDown } from 'lucide-react'
import { useState } from 'react'

interface ComplianceValidation {
  status: string
  risk_score: number
  checks_passed: string[]
  warnings: string[]
}

interface ComparativeAnalysis {
  [key: string]: {
    composite_score: number
    vs_selected: number
    reason: string
  }
}

interface DecisionJustification {
  selected_rail: string
  decision_reasoning: string
  cost_analysis: string
  speed_analysis: string
  reliability_analysis: string
  business_rules_applied: string[]
  comparative_analysis: ComparativeAnalysis
}

interface DecisionJustificationPanelProps {
  selectedRail: string
  amount: number
  currency: string
  justification: DecisionJustification
  compliance: ComplianceValidation
}

export default function DecisionJustificationPanel({
  selectedRail,
  amount,
  currency,
  justification,
  compliance,
}: DecisionJustificationPanelProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>('reasoning')

  const comparisonRails = Object.entries(justification.comparative_analysis || {})

  return (
    <div className="space-y-4 mt-6">
      {/* Main Decision Card */}
      <div className="card bg-gradient-to-br from-indigo-50 to-white border border-indigo-200">
        <div className="card-body">
          <div className="flex items-start gap-3 mb-4">
            <CheckCircle2 size={24} className="text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-lg font-bold text-gray-900">Decision Justification</h3>
              <p className="text-sm text-gray-600 mt-1">
                {justification.selected_rail} selected after analyzing {Object.keys(justification.comparative_analysis || {}).length + 1} payment options
              </p>
            </div>
          </div>

          {/* Primary Reasoning */}
          <div className="bg-white rounded-lg p-4 border border-indigo-100 mb-4">
            <p className="text-sm font-semibold text-gray-900 mb-2">Primary Reasoning</p>
            <p className="text-sm text-gray-700 leading-relaxed">{justification.decision_reasoning}</p>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            {/* Speed Section */}
            <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <div className="flex items-center gap-2 mb-1">
                <Clock size={16} className="text-blue-600" />
                <p className="text-xs font-semibold text-blue-900 uppercase">Speed</p>
              </div>
              <p className="text-sm text-gray-700">{justification.speed_analysis}</p>
            </div>

            {/* Cost Section */}
            <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-100">
              <div className="flex items-center gap-2 mb-1">
                <DollarSign size={16} className="text-emerald-600" />
                <p className="text-xs font-semibold text-emerald-900 uppercase">Cost</p>
              </div>
              <p className="text-sm text-gray-700">{justification.cost_analysis}</p>
            </div>

            {/* Reliability Section */}
            <div className="bg-purple-50 rounded-lg p-3 border border-purple-100">
              <div className="flex items-center gap-2 mb-1">
                <Shield size={16} className="text-purple-600" />
                <p className="text-xs font-semibold text-purple-900 uppercase">Reliability</p>
              </div>
              <p className="text-sm text-gray-700">{justification.reliability_analysis}</p>
            </div>
          </div>

          {/* Business Rules Applied */}
          {justification.business_rules_applied && justification.business_rules_applied.length > 0 && (
            <div className="bg-amber-50 rounded-lg p-3 border border-amber-100 mb-4">
              <p className="text-xs font-semibold text-amber-900 uppercase mb-2">Business Rules Applied</p>
              <ul className="space-y-1">
                {justification.business_rules_applied.map((rule, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-600" />
                    {rule}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Expandable Sections */}
          <div className="space-y-2">
            {/* Comparative Analysis */}
            {comparisonRails.length > 0 && (
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <button
                  onClick={() => setExpandedSection(expandedSection === 'comparison' ? null : 'comparison')}
                  className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <TrendingUp size={16} className="text-gray-600" />
                    <span className="font-semibold text-gray-900">Comparative Analysis</span>
                  </div>
                  <ChevronDown
                    size={18}
                    className={`text-gray-600 transition-transform ${expandedSection === 'comparison' ? 'rotate-180' : ''}`}
                  />
                </button>

                {expandedSection === 'comparison' && (
                  <div className="bg-gray-50 border-t border-gray-200 p-4 space-y-3">
                    {comparisonRails.map(([railName, analysis]) => (
                      <div key={railName} className="bg-white rounded-lg p-3 border border-gray-100">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-semibold text-gray-900">{railName}</p>
                            <p className="text-xs text-gray-500 mt-1">{analysis.reason}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-lg font-bold text-gray-900">{(analysis.composite_score ?? 0).toFixed(1)}</p>
                            <p className={`text-xs font-semibold ${(analysis.vs_selected ?? 0) < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                              {(analysis.vs_selected ?? 0) > 0 ? '+' : ''}{(analysis.vs_selected ?? 0).toFixed(1)} pts
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Compliance Validation */}
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setExpandedSection(expandedSection === 'compliance' ? null : 'compliance')}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Shield size={16} className="text-gray-600" />
                  <span className="font-semibold text-gray-900">Compliance Validation</span>
                </div>
                <ChevronDown
                  size={18}
                  className={`text-gray-600 transition-transform ${expandedSection === 'compliance' ? 'rotate-180' : ''}`}
                />
              </button>

              {expandedSection === 'compliance' && (
                <div className="bg-gray-50 border-t border-gray-200 p-4 space-y-3">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-semibold text-gray-900">Status</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      compliance.status === 'APPROVED' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-amber-100 text-amber-700'
                    }`}>
                      {compliance.status}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Risk Score</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 rounded-full bg-gray-200 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-green-500 to-red-500"
                          style={{ width: `${(compliance.risk_score ?? 0) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-semibold text-gray-900 w-12">
                        {((compliance.risk_score ?? 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  {compliance.checks_passed.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-gray-700 mb-2 uppercase">Checks Passed</p>
                      <ul className="space-y-1">
                        {compliance.checks_passed.map((check) => (
                          <li key={check} className="text-sm text-gray-700 flex items-center gap-2">
                            <CheckCircle2 size={14} className="text-green-600" />
                            {check.replace(/_/g, ' ')}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {compliance.warnings.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-amber-800 mb-2 uppercase">Warnings</p>
                      <ul className="space-y-1">
                        {compliance.warnings.map((warning) => (
                          <li key={warning} className="text-sm text-amber-700 flex items-center gap-2">
                            <AlertCircle size={14} className="text-amber-600" />
                            {warning}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
