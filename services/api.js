import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const programsAPI = {
  getAll: () => api.get('/api/programs'),
  getOne: (id) => api.get(`/api/programs/${id}`),
  create: (data) => api.post('/api/programs', data),
  update: (id, data) => api.put(`/api/programs/${id}`, data),
  delete: (id) => api.delete(`/api/programs/${id}`),
}

export const facultyAPI = {
  getAll: () => api.get('/api/faculty'),
  getOne: (id) => api.get(`/api/faculty/${id}`),
  create: (data) => api.post('/api/faculty', data),
  update: (id, data) => api.put(`/api/faculty/${id}`, data),
  delete: (id) => api.delete(`/api/faculty/${id}`),
}

export const coursesAPI = {
  getAll: (params) => api.get('/api/courses', { params }),
  getOne: (id) => api.get(`/api/courses/${id}`),
  create: (data) => api.post('/api/courses', data),
  update: (id, data) => api.put(`/api/courses/${id}`, data),
  delete: (id) => api.delete(`/api/courses/${id}`),
}

export const roomsAPI = {
  getAll: (availableOnly = false) => api.get('/api/rooms', { params: { available_only: availableOnly } }),
  getOne: (id) => api.get(`/api/rooms/${id}`),
  create: (data) => api.post('/api/rooms', data),
  update: (id, data) => api.put(`/api/rooms/${id}`, data),
  delete: (id) => api.delete(`/api/rooms/${id}`),
}

export const studentsAPI = {
  getAll: (params) => api.get('/api/students', { params }),
  getOne: (id) => api.get(`/api/students/${id}`),
  create: (data) => api.post('/api/students', data),
  update: (id, data) => api.put(`/api/students/${id}`, data),
  delete: (id) => api.delete(`/api/students/${id}`),
}

export const timetableAPI = {
  generate: (data) => api.post('/api/generate-timetable', data),
  getEntries: (params) => api.get('/api/timetable-entries', { params }),
  exportExcel: (programId, semester, academicYear) => 
    api.get('/api/export/timetable/excel', { 
      params: { program_id: programId, semester, academic_year: academicYear },
      responseType: 'blob'
    }),
  exportPDF: (programId, semester, academicYear) => 
    api.get('/api/export/timetable/pdf', { 
      params: { program_id: programId, semester, academic_year: academicYear },
      responseType: 'blob'
    }),
}

export const constraintsAPI = {
  getAll: () => api.get('/api/constraints'),
  create: (data) => api.post('/api/constraints', data),
  delete: (id) => api.delete(`/api/constraints/${id}`),
}

export const timeSlotsAPI = {
  getAll: () => api.get('/api/time-slots'),
  create: (data) => api.post('/api/time-slots', data),
}

export const facultyAssignmentsAPI = {
  getAll: (params) => api.get('/api/faculty-assignments', { params }),
  create: (data) => api.post('/api/faculty-assignments', data),
}

export const fieldActivitiesAPI = {
  getAll: (courseId) => api.get('/api/field-activities', { params: { course_id: courseId } }),
  create: (data) => api.post('/api/field-activities', data),
}

export default api