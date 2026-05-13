import { useState } from 'react'
import { PaymentRequest, PaymentResponse } from '../types'
import { orchestratePayment } from '../services/api'

export const usePaymentOrchestration = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<PaymentResponse | null>(null)

  const orchestrate = async (request: PaymentRequest) => {
    setLoading(true)
    setError(null)
    try {
      const response = await orchestratePayment(request)
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Orchestration failed')
    } finally {
      setLoading(false)
    }
  }

  return { orchestrate, loading, error, result }
}
