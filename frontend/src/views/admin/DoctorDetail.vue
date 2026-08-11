<template>
  <div class="detail-page">
    <el-container>
      <el-header>
        <div class="header-content">
          <div>
            <el-button @click="handleBack" link>
              <el-icon><ArrowLeft /></el-icon>
              返回医生列表
            </el-button>
          </div>
          <h2>医生详细信息</h2>
          <el-button @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <el-card v-loading="loading">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>基本信息</span>
              <div>
                <el-button v-if="!isEditing" type="primary" @click="handleEdit">
                  编辑信息
                </el-button>
                <template v-else>
                  <el-button @click="handleCancelEdit">取消</el-button>
                  <el-button type="primary" @click="handleSave">保存</el-button>
                </template>
              </div>
            </div>
          </template>

          <el-form :model="doctorForm" label-width="120px" :disabled="!isEditing">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="医生姓名">
                  <el-input v-model="doctorForm.real_name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="医院">
                  <el-input v-model="doctorForm.hospital" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="科室">
                  <el-input v-model="doctorForm.department" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="职称">
                  <el-select v-model="doctorForm.title" style="width: 100%">
                    <el-option label="主任医师" value="chief" />
                    <el-option label="副主任医师" value="associate_chief" />
                    <el-option label="主治医师" value="attending" />
                    <el-option label="住院医师" value="resident" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="审核状态">
                  <el-select v-model="doctorForm.audit_status" style="width: 100%">
                    <el-option label="待审核" value="pending" />
                    <el-option label="已通过" value="approved" />
                    <el-option label="已拒绝" value="rejected" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="账户状态">
                  <el-switch
                    v-model="doctorForm.is_active"
                    active-text="启用"
                    inactive-text="禁用"
                    @change="handleToggleStatus"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="联系电话">
                  <el-input v-model="doctorForm.phone" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="用户名">
                  <el-input v-model="doctorForm.username" disabled />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="注册时间">
                  <el-input :value="formatDateTime(doctorForm.created_at)" disabled />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { adminAPI } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const isEditing = ref(false)

const doctorForm = ref({
  real_name: '',
  hospital: '',
  department: '',
  title: '',
  audit_status: '',
  is_active: true,
  phone: '',
  username: '',
  user_id: null,
  created_at: ''
})

const originalDoctorData = ref({})

onMounted(async () => {
  await loadDoctorDetail()
})

const loadDoctorDetail = async () => {
  loading.value = true
  try {
    const doctorId = route.params.id || route.query.doctorId
    const data = await adminAPI.getDoctorDetail(doctorId)
    doctorForm.value = { ...data }
    originalDoctorData.value = { ...data }
  } catch (error) {
    console.error('获取医生信息失败:', error)
    ElMessage.error('获取医生信息失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = () => {
  isEditing.value = true
}

const handleCancelEdit = () => {
  isEditing.value = false
  doctorForm.value = { ...originalDoctorData.value }
}

const handleSave = async () => {
  try {
    const doctorId = route.params.id || route.query.doctorId
    const updateData = {
      real_name: doctorForm.value.real_name,
      hospital: doctorForm.value.hospital,
      department: doctorForm.value.department,
      title: doctorForm.value.title,
      audit_status: doctorForm.value.audit_status
    }
    await adminAPI.updateDoctor(doctorId, updateData)
    ElMessage.success('保存成功')
    isEditing.value = false
    originalDoctorData.value = { ...doctorForm.value }
  } catch (error) {
    console.error('保存失��:', error)
    ElMessage.error('保存失败')
  }
}

const handleToggleStatus = async (value) => {
  try {
    await ElMessageBox.confirm(
      `确定要${value ? '启用' : '禁用'}该医生账户吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await adminAPI.toggleUserStatus(doctorForm.value.user_id)
    ElMessage.success(value ? '账户已启用' : '账户已禁用')
    originalDoctorData.value.is_active = value
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换状态失败:', error)
      ElMessage.error('操作失败')
    }
    doctorForm.value.is_active = !value
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const handleBack = () => {
  router.push('/admin')
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  router.push('/login')
}
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #f0f2f5;
}

.el-header {
  background: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.el-main {
  padding: 20px;
}
</style>
