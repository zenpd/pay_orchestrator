export interface PaymentRequest {
  amount: number
  currency: string
  sender_id: string
  receiver_id: string
  corridor: string
  deadline_minutes?: number
  metadata?: Record<string, any>
}

export interface RailScore {
  rail_type: string
  composite_score: number
  cost_score: number
  speed_score: number
  reliability_score: number
  estimated_cost_usd: number
  estimated_time_hours: number
  feasibility: string
}

export interface PaymentResponse {
  session_id: string
  stage: string
  selected_rail?: string
  rail_scores: Record<string, RailScore>
  execution_result?: Record<string, any>
  messages: string[]
  errors: string[]
  created_at?: string
}
