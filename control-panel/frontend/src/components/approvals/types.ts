export interface ApprovalPayload {
  description?: string
  action_type?: string
  [key: string]: unknown
}

export interface Approval {
  id: string
  openclaw_session_id: string
  agent_id: string
  payload: ApprovalPayload
  rubric_scores: Record<string, number> | null
  status: "pending" | "approved" | "rejected"
  created_at: string
  decided_at?: string | null
  justification?: string | null
}
