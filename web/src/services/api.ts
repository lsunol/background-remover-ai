import axios from 'axios'

// In development: use Vite proxy at '/api' -> backend:8080
// In production: use same origin (FastAPI serves static files) and API is mounted under /api
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export interface ModelInfo {
  name: string
  full_name: string
  description: string
  authors: string[]
  year: number
  journal: string
  huggingface: string
  citation: string
  license: string
  attribution_required: boolean
  is_loaded?: boolean
}

export interface RemoveBackgroundResponse {
  success: boolean
  result_image: string
  mask?: string
  metadata?: {
    model_used: string
    original_size: [number, number]
    processed_size: [number, number]
    device_used: string
  }
}

class ApiService {
  async getModelInfo(modelName: string): Promise<ModelInfo> {
    const response = await axios.get(`${API_BASE_URL}/models/${modelName}/info`)
    return response.data
  }

  async removeBackground(
    file: File,
    modelName: string = 'rmbg-2.0',
    includeMask: boolean = false
  ): Promise<RemoveBackgroundResponse> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('model_name', modelName)
    formData.append('include_mask', includeMask.toString())
    formData.append('return_metadata', 'true')

    const response = await axios.post(`${API_BASE_URL}/remove-background`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  }

  async listModels() {
    const response = await axios.get(`${API_BASE_URL}/models`)
    return response.data
  }
}

export default new ApiService()
