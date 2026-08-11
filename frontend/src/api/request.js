import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from '@/utils/auth'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

// 请求拦截：带 token
request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截：统一错误处理
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 后端统一返回 { code, message, data }（见后端 response.py）
    if (res && typeof res === 'object' && 'code' in res) {
      if (res.code === 0 || res.code === 200) {
        return res.data !== undefined ? res.data : res
      }
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res
  },
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      ElMessage.error('登录已失效，请重新登录')
      removeToken()
      router.push('/login')
    } else {
      ElMessage.error(error.response?.data?.message || error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
