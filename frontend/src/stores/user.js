import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
  const token = ref(localStorage.getItem('token') || '')

  const setUser = (user) => {
    userInfo.value = user
    localStorage.setItem('userInfo', JSON.stringify(user))
  }

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const logout = () => {
    userInfo.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  const isLoggedIn = () => {
    return !!token.value && !!userInfo.value
  }

  const getUserProfileId = () => {
    if (!userInfo.value) return null
    // 根据角色返回对应的profile ID
    if (userInfo.value.role === 'doctor' && userInfo.value.doctor_profile) {
      return userInfo.value.doctor_profile.id
    }
    if (userInfo.value.role === 'patient' && userInfo.value.patient_profile) {
      return userInfo.value.patient_profile.id
    }
    return userInfo.value.id
  }

  return {
    userInfo,
    token,
    setUser,
    setToken,
    logout,
    isLoggedIn,
    getUserProfileId
  }
})
