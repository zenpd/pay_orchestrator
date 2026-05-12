import React from 'react'
import axios from 'axios'

interface PaymentFormProps {
  onPaymentCreated: (paymentId: string) => void
}

export function PaymentForm({ onPaymentCreated }: PaymentFormProps) {
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [formData, setFormData] = React.useState({
    amount: 5000,
    currency_from: 'ZAR',
    currency_to: 'USD',
    sender_country: 'ZA',
    receiver_country: 'US',
    sender_name: 'Acme Corp',
    receiver_name: 'Global Supplier Inc',
    payment_purpose: 'Invoice settlement',
    routing_preference: 'balanced',
    urgency: 5,
    risk_tolerance: 5,
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: isNaN(Number(value)) ? value : Number(value),
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const response = await axios.post('/api/v1/payment/process', formData)
      onPaymentCreated(response.data.payment_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process payment')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="form-container">
      <h2>Process Payment</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Amount</label>
          <input
            type="number"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            min="1"
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>From Currency</label>
            <input
              type="text"
              name="currency_from"
              value={formData.currency_from}
              onChange={handleChange}
              maxLength={3}
            />
          </div>
          <div className="form-group">
            <label>To Currency</label>
            <input
              type="text"
              name="currency_to"
              value={formData.currency_to}
              onChange={handleChange}
              maxLength={3}
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Sender Country</label>
            <input
              type="text"
              name="sender_country"
              value={formData.sender_country}
              onChange={handleChange}
              maxLength={2}
            />
          </div>
          <div className="form-group">
            <label>Receiver Country</label>
            <input
              type="text"
              name="receiver_country"
              value={formData.receiver_country}
              onChange={handleChange}
              maxLength={2}
            />
          </div>
        </div>
        <div className="form-group">
          <label>Sender Name</label>
          <input
            type="text"
            name="sender_name"
            value={formData.sender_name}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Receiver Name</label>
          <input
            type="text"
            name="receiver_name"
            value={formData.receiver_name}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Payment Purpose</label>
          <input
            type="text"
            name="payment_purpose"
            value={formData.payment_purpose}
            onChange={handleChange}
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Routing Preference</label>
            <select name="routing_preference" value={formData.routing_preference} onChange={handleChange}>
              <option value="fastest">Fastest</option>
              <option value="cheapest">Cheapest</option>
              <option value="balanced">Balanced</option>
            </select>
          </div>
          <div className="form-group">
            <label>Urgency (1-10)</label>
            <input
              type="number"
              name="urgency"
              value={formData.urgency}
              onChange={handleChange}
              min="1"
              max="10"
            />
          </div>
          <div className="form-group">
            <label>Risk Tolerance (1-10)</label>
            <input
              type="number"
              name="risk_tolerance"
              value={formData.risk_tolerance}
              onChange={handleChange}
              min="1"
              max="10"
            />
          </div>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit Payment'}
        </button>
      </form>
    </div>
  )
}
