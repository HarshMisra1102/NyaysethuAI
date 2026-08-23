export interface User { id: number; name: string; email: string; state: string | null; district: string | null }
export interface AuthResponse { access_token: string; token_type: string; user: User }
export interface Case { id: number; user_id: number; title: string; category: string; description: string; status: string; created_at: string; updated_at: string }
export interface Citation { title: string; url: string | null; source_type: string | null; document_id: number | null; page_number: number | null }
export interface Evidence { content: string; document_id: number | null; chunk_id: number | null; page_number: number | null; score: number | null; source: Citation | null }
export interface ActionStep { step: number; title: string; description: string }
export interface ChatAIResponse { issue: string | null; category: string | null; summary: string; possible_rights: string[]; evidence: Evidence[]; action_plan: ActionStep[]; required_documents: string[]; sources: Citation[]; disclaimer: string }
export interface ChatResponse { conversation_id: number; message_id: number; response: ChatAIResponse; created_at: string }
export interface Document { id: number; title: string; document_type: string | null; department: string | null; language: string | null; source_url: string | null; storage_url: string | null; created_at: string; updated_at: string }
export interface DocumentUploadResponse { document: Document; processing_status: string }
export interface RightsResponse { category: string; summary: string; rights: { title: string; explanation: string; legal_basis: string | null }[]; action_plan: string[]; required_documents: string[]; sources: string[]; disclaimer: string }
export interface RTIDraft { department: string; public_information_officer: string | null; subject: string; application_text: string; required_documents: string[]; submission_method: string | null; submission_url: string | null; sources: string[]; disclaimer: string }
export interface SchemeResponse { scheme_name: string; eligible: boolean | null; confidence: number | null; explanation: string; eligibility_conditions: string[]; missing_information: string[]; application_url: string | null; sources: string[]; disclaimer: string }
