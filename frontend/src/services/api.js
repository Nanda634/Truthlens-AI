import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('truthlens_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const authApi = {
  register: (name, email, password) => api.post('/auth/register', { name, email, password }),
  login: (email, password) => api.post('/auth/login', { email, password }),
}

export const filesApi = {
  upload: (file, onProgress) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/files/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => onProgress && onProgress(Math.round((e.loaded * 100) / e.total)),
    })
  },
  delete: (fileId) => api.delete(`/files/${fileId}`),
}

export const analysisApi = {
  start: (fileId) => api.post(`/analysis/${fileId}`),
  status: (analysisId) => api.get(`/analysis/${analysisId}/status`),
  result: (analysisId) => api.get(`/analysis/${analysisId}/result`),
  evidence: (analysisId) => api.get(`/analysis/${analysisId}/evidence`),
  reportUrl: (analysisId) => `/api/analysis/${analysisId}/report`,
  history: () => api.get('/analysis/history'),
}

export default api
