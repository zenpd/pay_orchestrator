import axios from 'axios'
import { PaymentRequest, PaymentResponse } from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const orchestratePayment = (request: PaymentRequest) =>
  api.post<PaymentResponse>('/payment/orchestrate', request)

export const listRails = () =>
  api.get('/payment/rails')

export const getHealth = () =>
  api.get('/health')

export default api
