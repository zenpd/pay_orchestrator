export interface PaymentRequest {
  amount: number
  currency: string
  sender_id: string
  receiver_id: string
  corridor: string
  region?: string
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

export interface DecisionJustification {
  selected_rail: string
  decision_reasoning: string
  cost_analysis: string
  speed_analysis: string
  reliability_analysis: string
  business_rules_applied: string[]
  comparative_analysis: Record<string, {
    composite_score: number
    vs_selected: number
    reason: string
  }>
}

export interface ComplianceValidation {
  status: string
  risk_score: number
  checks_passed: string[]
  warnings: string[]
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
  decision_justification?: DecisionJustification
  compliance_validation?: ComplianceValidation
}
