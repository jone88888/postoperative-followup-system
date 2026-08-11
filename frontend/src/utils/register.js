// 注册页面辅助函数
export const handleRegisterSubmit = async (formData, authAPI) => {
  const registerData = {
    username: formData.username,
    password: formData.password,
    phone: formData.phone,
    role: formData.role,
    real_name: formData.realName
  }

  if (formData.role === 'patient') {
    Object.assign(registerData, {
      gender: formData.gender,
      age: formData.age,
      surgery_type: formData.surgeryType,
      doctor_id: formData.doctorId
    })
  } else if (formData.role === 'doctor') {
    Object.assign(registerData, {
      hospital: formData.hospital,
      department: formData.department,
      title: formData.title
    })
  }

  return await authAPI.register(registerData)
}
