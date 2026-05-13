import { create } from 'zustand'
import { PaymentResponse } from '../types'

interface PaymentStore {
  currentPayment: PaymentResponse | null
  loading: boolean
  setCurrentPayment: (payment: PaymentResponse | null) => void
  setLoading: (loading: boolean) => void
}

export const usePaymentStore = create<PaymentStore>((set) => ({
  currentPayment: null,
  loading: false,
  setCurrentPayment: (payment) => set({ currentPayment: payment }),
  setLoading: (loading) => set({ loading }),
}))
