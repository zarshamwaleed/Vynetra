export interface Presentation {
  id: string
  title: string
  topic: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  slides: number
  created_at: string
  updated_at: string
  file_paths?: {
    pptx?: string
    pdf?: string
    markdown?: string
    json?: string
  }
}

export interface GenerateRequest {
  prompt: string
  slide_count?: number
  audience?: 'beginner' | 'intermediate' | 'expert' | 'mixed'
  tone?: 'professional' | 'educational' | 'casual' | 'persuasive'
}

export interface GenerateResponse {
  job_id: string
  status: string
  message: string
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export type Theme = 'light' | 'dark' | 'system'
export type LLMProvider = 'groq' | 'gemini' | 'openrouter' | 'ollama'
