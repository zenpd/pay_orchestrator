import React from 'react'
import axios from 'axios'

interface PaymentStatusProps {
  paymentId: string
  onReset: () => void
}

export function PaymentStatus({ paymentId, onReset }: PaymentStatusProps) {
  const [payment, setPayment] = React.useState<any>(null)
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const fetchPayment = async () => {
      try {
        const response = await axios.get(`/api/v1/payment/${paymentId}`)
        setPayment(response.data)
      } catch (err) {
        console.error('Failed to fetch payment:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchPayment()
  }, [paymentId])

  if (loading) {
    return <div className="status-container">Loading payment details...</div>
  }

  if (!payment) {
    return <div className="status-container">Payment not found</div>
  }

  return (
    <div className="status-container">
      <h2>Payment Status</h2>
      <div className="status-grid">
        <div className="status-item">
          <label>Payment ID</label>
          <span>{payment.payment_id}</span>
        </div>
        <div className="status-item">
          <label>Compliance Status</label>
          <span className={`status-badge status-${payment.compliance_status?.toLowerCase()}`}>
            {payment.compliance_status}
          </span>
        </div>
        <div className="status-item">
          <label>Risk Score</label>
          <span>{(payment.risk_score || 0).toFixed(3)}</span>
        </div>
        <div className="status-item">
          <label>Selected Rail</label>
          <span>{payment.selected_rail}</span>
        </div>
        <div className="status-item">
          <label>Execution Status</label>
          <span className={`status-badge status-${payment.execution_status?.toLowerCase()}`}>
            {payment.execution_status}
          </span>
        </div>
        {payment.actual_cost && (
          <div className="status-item">
            <label>Actual Cost (USD)</label>
            <span>${payment.actual_cost.toFixed(2)}</span>
          </div>
        )}
      </div>
      <button onClick={onReset} className="button-secondary">
        Process Another Payment
      </button>
    </div>
  )
}
