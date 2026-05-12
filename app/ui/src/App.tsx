import React from 'react'
import { PaymentForm } from './components/PaymentForm'
import { PaymentStatus } from './components/PaymentStatus'
import './App.css'

export function App() {
  const [paymentId, setPaymentId] = React.useState<string | null>(null)

  return (
    <div className="app">
      <header>
        <h1>Payment Orchestrator</h1>
        <p>AI-powered cross-border payment routing with left-shifted compliance</p>
      </header>
      <main>
        {!paymentId ? (
          <PaymentForm onPaymentCreated={setPaymentId} />
        ) : (
          <PaymentStatus paymentId={paymentId} onReset={() => setPaymentId(null)} />
        )}
      </main>
    </div>
  )
}
