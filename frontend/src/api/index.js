import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
      return Promise.reject(data.error || data.message || '请求失败')
    }
    return Promise.reject(error.message || '网络错误')
  }
)

// 用户认证相关
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  getCurrentUser: () => api.get('/auth/user/')
}

// 医生相关
export const doctorAPI = {
  list: () => api.get('/doctors/list/'),
  getInfo: (doctorId) => api.get('/doctors/info/', { params: { doctor_id: doctorId } }),
  getPatients: (doctorId) => api.get('/doctors/patients/', { params: { doctor_id: doctorId } }),
  getPatientDetail: (patientId, doctorId) => api.get(`/doctors/patients/${patientId}/`, { params: { doctor_id: doctorId } }),
  updatePatient: (patientId, data) => api.put(`/doctors/patients/${patientId}/update/`, data),
  getPatientSubmissions: (patientId, doctorId) => api.get(`/doctors/patients/${patientId}/submissions/`, { params: { doctor_id: doctorId } }),
  getPendingBindings: (doctorId) => api.get(`/bindings/doctor/${doctorId}/`),
  approveBinding: (bindingId) => api.post(`/bindings/${bindingId}/approve/`),
  rejectBinding: (bindingId) => api.post(`/bindings/${bindingId}/reject/`),
  createTasks: (data) => api.post('/doctors/tasks/create/', data),
  getTasks: (doctorId) => api.get('/doctors/tasks/', { params: { doctor_id: doctorId } }),
  getTaskDetail: (taskId, doctorId) => api.get(`/doctors/tasks/${taskId}/`, { params: { doctor_id: doctorId } }),
  updateTask: (taskId, data) => api.put(`/doctors/tasks/${taskId}/update/`, data),
  deleteTask: (taskId, doctorId) => api.delete(`/doctors/tasks/${taskId}/delete/`, { params: { doctor_id: doctorId } })
}

// 患者相关
export const patientAPI = {
  getInfo: (patientId) => api.get('/patients/info/', { params: { patient_id: patientId } }),
  getTasks: (patientId) => api.get('/patients/tasks/', { params: { patient_id: patientId } }),
  getTaskDetail: (taskId, patientId) => api.get(`/patients/tasks/${taskId}/`, { params: { patient_id: patientId } }),
  submitTask: (taskId, data) => api.post(`/patients/tasks/${taskId}/submit/`, data),
  getBindings: (patientId) => api.get(`/bindings/patient/${patientId}/`),
  createBinding: (data) => api.post('/bindings/create/', data)
}

// 管理员相关
export const adminAPI = {
  getPendingDoctors: () => api.get('/admin/doctors/pending/'),
  approveDoctor: (doctorId) => api.post(`/admin/doctors/${doctorId}/approve/`),
  rejectDoctor: (doctorId) => api.post(`/admin/doctors/${doctorId}/reject/`),
  getAllDoctors: () => api.get('/admin/doctors/'),
  getDoctorDetail: (doctorId) => api.get(`/admin/doctors/${doctorId}/`),
  updateDoctor: (doctorId, data) => api.put(`/admin/doctors/${doctorId}/update/`, data),
  resetDoctorPassword: (doctorId, data) => api.post(`/admin/doctors/${doctorId}/reset-password/`, data),
  getAllPatients: () => api.get('/admin/patients/'),
  getPatientDetail: (patientId) => api.get(`/admin/patients/${patientId}/`),
  updatePatient: (patientId, data) => api.put(`/admin/patients/${patientId}/update/`, data),
  resetPatientPassword: (patientId, data) => api.post(`/admin/patients/${patientId}/reset-password/`, data),
  getPatientSubmissions: (patientId) => api.get(`/admin/patients/${patientId}/submissions/`),
  getAllBindings: () => api.get('/bindings/all/'),
  unbindRelationship: (bindingId) => api.post(`/admin/bindings/${bindingId}/unbind/`),
  getStatistics: () => api.get('/admin/statistics/'),
  toggleUserStatus: (userId) => api.post(`/admin/users/${userId}/toggle/`)
}

export default api
