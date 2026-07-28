import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const presentationApi = {
  generate: async (data: {
    prompt: string
    slide_count?: number
    audience?: string
    tone?: string
  }) => {
    const response = await api.post('/presentations/generate', data)
    return response.data
  },

  getStatus: async (jobId: string) => {
    const response = await api.get(/presentations//status)
    return response.data
  },

  getAll: async () => {
    const response = await api.get('/presentations/')
    return response.data
  },

  getOne: async (id: string) => {
    const response = await api.get(/presentations/)
    return response.data
  },

  delete: async (id: string) => {
    const response = await api.delete(/presentations/)
    return response.data
  },

  download: async (jobId: string, fileType: string) => {
    const response = await api.get(/presentations//download/, {
      responseType: 'blob',
    })
    return response.data
  },
}

export const llmApi = {
  getProviders: async () => {
    const response = await api.get('/llm/providers')
    return response.data
  },

  generate: async (data: {
    prompt: string
    provider?: string
    temperature?: number
    max_tokens?: number
  }) => {
    const response = await api.post('/llm/generate', data)
    return response.data
  },
}

export const mcpApi = {
  getServers: async () => {
    const response = await api.get('/mcp/servers')
    return response.data
  },

  getHistory: async () => {
    const response = await api.get('/mcp/history')
    return response.data
  },

  callTool: async (data: {
    server: string
    tool: string
    params: Record<string, any>
  }) => {
    const response = await api.post('/mcp/call', data)
    return response.data
  },
}

export const healthApi = {
  check: async () => {
    const response = await api.get('/health')
    return response.data
  },
}

export default api
