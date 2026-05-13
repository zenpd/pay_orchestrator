import { CheckCircle2, ArrowRight, DollarSign, Clock, Shield } from 'lucide-react'

interface PaymentResultProps {
  transactionId: string
  amount: number
  currency: string
  selectedRail: string
  estimatedTime: string
  estimatedCost: number
  compositeScore: number
}

export default function PaymentResult({
  transactionId,
  amount,
  currency,
  selectedRail,
  estimatedTime,
  estimatedCost,
  compositeScore,
}: PaymentResultProps) {
  return (
    <div className="card overflow-hidden border-emerald-200 bg-gradient-to-br from-emerald-50/50 to-white">
      <div className="card-body space-y-6">
        {/* Success Header */}
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
            <CheckCircle2 size={28} className="text-emerald-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Payment Orchestrated Successfully</h3>
            <p className="text-sm text-gray-500 mt-1">Your payment has been optimized and routed</p>
          </div>
        </div>

        {/* Transaction Details */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <p className="text-xs font-semibold text-gray-400 uppercase mb-1">Transaction ID</p>
            <p className="text-sm font-mono text-gray-900 break-all">{transactionId}</p>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <p className="text-xs font-semibold text-gray-400 uppercase mb-1">Payment Amount</p>
            <p className="text-lg font-bold text-gray-900">
              {currency} {amount.toLocaleString()}
            </p>
          </div>
        </div>

        {/* Payment Flow */}
        <div className="bg-white rounded-lg p-4 border border-gray-100">
          <p className="text-xs font-semibold text-gray-400 uppercase mb-4">Execution Path</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-10 rounded-lg bg-indigo-50 flex items-center justify-center font-medium text-sm text-indigo-700">
              Payment Request
            </div>
            <ArrowRight size={20} className="text-gray-400 flex-shrink-0" />
            <div className="flex-1 h-10 rounded-lg bg-indigo-50 flex items-center justify-center font-medium text-sm text-indigo-700">
              AI Analysis
            </div>
            <ArrowRight size={20} className="text-gray-400 flex-shrink-0" />
            <div className="flex-1 h-10 rounded-lg bg-emerald-50 flex items-center justify-center font-bold text-sm text-emerald-700">
              {selectedRail}
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <Clock size={16} className="text-gray-400" />
              <p className="text-xs font-semibold text-gray-400 uppercase">Est. Time</p>
            </div>
            <p className="text-sm font-bold text-gray-900">{estimatedTime}</p>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign size={16} className="text-gray-400" />
              <p className="text-xs font-semibold text-gray-400 uppercase">Processing Fee</p>
            </div>
            <p className="text-sm font-bold text-gray-900">${estimatedCost.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <Shield size={16} className="text-gray-400" />
              <p className="text-xs font-semibold text-gray-400 uppercase">AI Score</p>
            </div>
            <p className={`text-sm font-bold ${
              compositeScore >= 80 ? 'text-emerald-600' :
              compositeScore >= 60 ? 'text-amber-600' :
              'text-red-600'
            }`}>
              {Math.round(compositeScore)}/100
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          <button className="flex-1 btn btn-primary">View Details</button>
          <button className="flex-1 btn btn-secondary">New Payment</button>
        </div>
      </div>
    </div>
  )
}
