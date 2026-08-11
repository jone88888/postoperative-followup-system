<template>
  <div class="register-container">
    <el-card class="register-card">
      <h2 class="title">用户注册</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="注册身份" prop="role">
          <el-radio-group v-model="form.role" size="large">
            <el-radio-button label="patient">患者</el-radio-button>
            <el-radio-button label="doctor">医生</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" placeholder="请输入账号（字母或数字组合）" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>

        <el-form-item label="姓名" prop="realName">
          <el-input v-model="form.realName" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="身份证号" prop="idCard">
          <el-input v-model="form.idCard" placeholder="请输入身份证号" maxlength="18" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>

        <!-- 患者专属字段 -->
        <template v-if="form.role === 'patient'">
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="form.gender">
              <el-radio label="male">男</el-radio>
              <el-radio label="female">女</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="年龄" prop="age">
            <el-input-number v-model="form.age" :min="1" :max="120" />
          </el-form-item>

          <el-form-item label="手术类型" prop="surgeryType">
            <el-input v-model="form.surgeryType" placeholder="请输入手术类型" />
          </el-form-item>

          <el-form-item label="选择医生" prop="doctorId">
            <el-select v-model="form.doctorId" placeholder="请选择您的主治医生" style="width: 100%">
              <el-option
                v-for="doctor in doctors"
                :key="doctor.id"
                :label="`${doctor.real_name} - ${doctor.hospital} ${doctor.department}`"
                :value="doctor.id"
              />
            </el-select>
          </el-form-item>
        </template>

        <!-- 医生专属字段 -->
        <template v-if="form.role === 'doctor'">
          <el-form-item label="医院" prop="hospital">
            <el-input v-model="form.hospital" placeholder="请输入所在医院" />
          </el-form-item>

          <el-form-item label="科室" prop="department">
            <el-input v-model="form.department" placeholder="请输入所在科室" />
          </el-form-item>

          <el-form-item label="职称" prop="title">
            <el-select v-model="form.title" placeholder="请选择职称">
              <el-option label="主任医师" value="chief" />
              <el-option label="副主任医师" value="associate_chief" />
              <el-option label="主治医师" value="attending" />
              <el-option label="住院医师" value="resident" />
            </el-select>
          </el-form-item>
        </template>

        <el-form-item>
          <el-button type="primary" size="large" @click="handleRegister" :loading="loading" style="width: 100%">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-link">
        已有账号？<router-link to="/login">立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI, doctorAPI } from '@/api'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  role: 'patient',
  username: '',
  password: '',
  confirmPassword: '',
  realName: '',
  idCard: '',
  phone: '',
  gender: 'male',
  age: null,
  surgeryType: '',
  doctorId: '',
  hospital: '',
  department: '',
  title: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  role: [{ required: true, message: '请选择注册身份', trigger: 'change' }],
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]+$/, message: '账号只能包含字母和数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  idCard: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/, message: '请输入正确的身份证号', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  doctorId: [{ required: true, message: '请选择医生', trigger: 'change' }],
  hospital: [{ required: true, message: '请输入所在医院', trigger: 'blur' }],
  department: [{ required: true, message: '请输入所在科室', trigger: 'blur' }],
  title: [{ required: true, message: '请选择职称', trigger: 'change' }]
}

// 模拟医生列表
const doctors = ref([])

const loadDoctors = async () => {
  try {
    const data = await doctorAPI.list()
    doctors.value = data
  } catch (error) {
    console.error('加载医生列表失败:', error)
  }
}

onMounted(() => {
  loadDoctors()
})

watch(() => form.role, () => {
  formRef.value?.clearValidate()
})

const handleRegister = async () => {
  await formRef.value.validate()
  loading.value = true

  try {
    const registerData = {
      username: form.username,
      password: form.password,
      phone: form.phone,
      role: form.role,
      real_name: form.realName,
      id_card: form.idCard
    }

    if (form.role === 'patient') {
      Object.assign(registerData, {
        gender: form.gender,
        age: form.age,
        surgery_type: form.surgeryType,
        doctor_id: form.doctorId
      })
    } else {
      Object.assign(registerData, {
        hospital: form.hospital,
        department: form.department,
        title: form.title
      })
    }

    await authAPI.register(registerData)

    if (form.role === 'patient') {
      ElMessage.success('注册成功！请等待医生确认绑定关系')
    } else {
      ElMessage.success('注册成功！请等待管理员审核')
    }
    router.push('/login')
  } catch (error) {
    console.error('注册失败:', error)
    const errorMsg = error.response?.data?.username?.[0] || 
                     error.response?.data?.id_card?.[0] || 
                     '注册失败，请检查输入信息'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  width: 500px;
  max-width: 100%;
  padding: 20px;
}

.title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #606266;
}

.login-link a {
  color: #409eff;
  text-decoration: none;
}
</style>
