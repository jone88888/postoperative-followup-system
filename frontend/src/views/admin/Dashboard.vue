<template>
  <div class="dashboard">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>管理员控制台</h2>
          <div>
            <span style="margin-right: 20px">管理员</span>
            <el-button @click="handleLogout">退出登录</el-button>
          </div>
        </div>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="总用户数" :value="statistics.totalUsers" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="医生数" :value="statistics.doctorCount" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="患者数" :value="statistics.patientCount" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="医患绑定数" :value="statistics.bindingCount" />
            </el-card>
          </el-col>
        </el-row>

        <el-tabs v-model="activeTab" style="margin-top: 20px">
          <el-tab-pane label="医生审核" name="doctorAudit">
            <el-card>
              <el-table :data="pendingDoctors" style="width: 100%">
                <el-table-column prop="username" label="账号" />
                <el-table-column prop="realName" label="姓名" />
                <el-table-column prop="hospital" label="医院" />
                <el-table-column prop="department" label="科室" />
                <el-table-column prop="title" label="职称">
                  <template #default="{ row }">
                    {{ getTitleText(row.title) }}
                  </template>
                </el-table-column>
                <el-table-column prop="phone" label="手机号" />
                <el-table-column prop="registerTime" label="注册时间" />
                <el-table-column prop="status" label="状态">
                  <template #default="{ row }">
                    <el-tag :type="getAuditStatusType(row.status)">
                      {{ getAuditStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180">
                  <template #default="{ row }">
                    <template v-if="row.status === DOCTOR_AUDIT_STATUS.PENDING">
                      <el-button link type="success" size="small" @click="handleApproveDoctor(row)">
                        通过
                      </el-button>
                      <el-button link type="danger" size="small" @click="handleRejectDoctor(row)">
                        拒绝
                      </el-button>
                    </template>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="医生管理" name="doctors">
            <el-card>
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center">
                  <span>医生列表</span>
                  <el-input
                    v-model="doctorSearch"
                    placeholder="搜索医生姓名或医院"
                    style="width: 250px"
                    clearable
                  />
                </div>
              </template>
              <el-table :data="filteredDoctors" style="width: 100%">
                <el-table-column prop="username" label="账号" width="120" />
                <el-table-column prop="realName" label="姓名" width="100" />
                <el-table-column prop="hospital" label="医院" />
                <el-table-column prop="department" label="科室" width="100" />
                <el-table-column prop="patientCount" label="患者数" width="80" />
                <el-table-column prop="taskCount" label="任务数" width="80" />
                <el-table-column prop="lastLoginTime" label="最近登录" width="160" />
                <el-table-column label="操作" width="200">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="handleViewDoctor(row)">
                      详情
                    </el-button>
                    <el-button link type="warning" size="small" @click="handleResetDoctorPassword(row)">
                      改密码
                    </el-button>
                    <el-button link type="danger" size="small" @click="handleDeleteDoctor(row)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="患者管理" name="patients">
            <el-card>
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center">
                  <span>患者列表</span>
                  <el-input
                    v-model="patientSearch"
                    placeholder="搜索患者姓名"
                    style="width: 250px"
                    clearable
                  />
                </div>
              </template>
              <el-table :data="filteredPatients" style="width: 100%">
                <el-table-column prop="username" label="账号" width="120" />
                <el-table-column prop="realName" label="姓名" width="100" />
                <el-table-column prop="age" label="年龄" width="60" />
                <el-table-column prop="phone" label="手机号" width="120" />
                <el-table-column prop="doctorName" label="绑定医生" />
                <el-table-column prop="surgeryType" label="手术类型" />
                <el-table-column prop="bindDate" label="绑定时间" width="160" />
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="handleViewPatient(row)">
                      详情
                    </el-button>
                    <el-button link type="warning" size="small" @click="handleResetPatientPassword(row)">
                      改密码
                    </el-button>
                    <el-button link type="danger" size="small" @click="handleDeletePatient(row)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="医患关系管理" name="bindings">
            <el-card>
              <el-table :data="allBindings" style="width: 100%">
                <el-table-column prop="patientName" label="患者" />
                <el-table-column prop="doctorName" label="医生" />
                <el-table-column prop="hospital" label="医院" />
                <el-table-column prop="applyTime" label="申请时间" />
                <el-table-column prop="approveTime" label="审核时间" />
                <el-table-column prop="status" label="状态">
                  <template #default="{ row }">
                    <el-tag :type="getBindingStatusType(row.status)">
                      {{ getBindingStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120">
                  <template #default="{ row }">
                    <el-button
                      v-if="row.status === BINDING_STATUS.APPROVED"
                      link
                      type="warning"
                      size="small"
                      @click="handleUnbind(row)"
                    >
                      解除绑定
                    </el-button>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="系统统计" name="statistics">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>用户增长趋势</span>
                  </template>
                  <div style="height: 300px; display: flex; align-items: center; justify-content: center">
                    <el-text type="info">图表功能待实现</el-text>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>任务完成情况</span>
                  </template>
                  <div style="height: 300px; display: flex; align-items: center; justify-content: center">
                    <el-text type="info">图表功能待实现</el-text>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-card style="margin-top: 20px">
              <template #header>
                <span>系统活跃度统计</span>
              </template>
              <el-descriptions :column="3" border>
                <el-descriptions-item label="待审核医生">{{ pendingDoctors.length }}</el-descriptions-item>
                <el-descriptions-item label="待审核绑定">{{ allBindings.filter(b => b.status === BINDING_STATUS.PENDING).length }}</el-descriptions-item>
                <el-descriptions-item label="已批准绑定">{{ allBindings.filter(b => b.status === BINDING_STATUS.APPROVED).length }}</el-descriptions-item>
                <el-descriptions-item label="已批准医生">{{ allDoctors.filter(d => d.status === DOCTOR_AUDIT_STATUS.APPROVED).length }}</el-descriptions-item>
                <el-descriptions-item label="活跃医生">{{ allDoctors.length }}</el-descriptions-item>
                <el-descriptions-item label="活跃患者">{{ allPatients.length }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>

    <!-- 重���密码对话��� -->
    <el-dialog v-model="resetPasswordDialogVisible" :title="resetPasswordTitle" width="400px">
      <el-form :model="resetPasswordForm" label-width="100px">
        <el-form-item label="用户">
          <el-text>{{ resetPasswordForm.userName }}</el-text>
        </el-form-item>
        <el-form-item label="���密码">
          <el-input
            v-model="resetPasswordForm.newPassword"
            type="password"
            placeholder="���输入新密码（���少6位���"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="resetPasswordForm.confirmPassword"
            type="password"
            placeholder="请���次输入新密���"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPasswordDialogVisible = false">取���</el-button>
        <el-button type="primary" @click="handleConfirmResetPassword">确认���置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  BINDING_STATUS,
  BINDING_STATUS_TEXT,
  BINDING_STATUS_TYPE,
  DOCTOR_AUDIT_STATUS,
  DOCTOR_AUDIT_STATUS_TEXT,
  DOCTOR_AUDIT_STATUS_TYPE
} from '@/utils/enum'
import { adminAPI } from '@/api'

const router = useRouter()
const activeTab = ref('doctorAudit')
const doctorSearch = ref('')
const patientSearch = ref('')

// 重置���码相关
const resetPasswordDialogVisible = ref(false)
const resetPasswordTitle = ref('')
const resetPasswordForm = ref({
  userId: null,
  userName: '',
  userType: '', // 'doctor' 或 'patient'
  newPassword: '',
  confirmPassword: ''
})

onMounted(async () => {
  try {
    // 获取待审核医生
    const pendingDocs = await adminAPI.getPendingDoctors()
    pendingDoctors.value = pendingDocs.map(d => ({
      id: d.id,
      username: d.username,
      realName: d.real_name,
      hospital: d.hospital,
      department: d.department,
      title: d.title,
      phone: d.phone,
      registerTime: d.created_at,
      status: d.audit_status
    }))

    // 获取所有医生
    const doctors = await adminAPI.getAllDoctors()
    allDoctors.value = doctors.map(d => ({
      id: d.id,
      username: d.username,
      realName: d.real_name,
      hospital: d.hospital,
      department: d.department,
      patientCount: d.patient_count || 0,
      taskCount: d.task_count || 0,
      lastLoginTime: d.last_login || '-',
      status: d.audit_status
    }))

    // 获取所有患者数据
    const patients = await adminAPI.getAllPatients()
    console.log('患者数据:', patients)

    // 获取所有绑定关系
    const bindings = await adminAPI.getAllBindings()
    console.log('绑定关系数据:', bindings)

    allBindings.value = bindings.map(b => ({
      id: b.id,
      patientName: b.patient_name,
      doctorName: b.doctor_name,
      hospital: b.hospital || '-',
      applyTime: b.apply_time,
      approveTime: b.approve_time || '-',
      status: b.status
    }))

    // 为患者匹配医生信息
    allPatients.value = patients.map(p => {
      // 查找该患者的已绑定医生
      const approvedBinding = bindings.find(
        b => b.patient_id === p.id && b.status === 'approved'
      )

      console.log(`患者 ${p.id} (${p.real_name}) 的绑定:`, approvedBinding)

      return {
        id: p.id,
        username: p.username,
        realName: p.real_name,
        age: p.age,
        phone: p.phone,
        doctorName: approvedBinding ? approvedBinding.doctor_name : '未绑定',
        surgeryType: p.surgery_type,
        bindDate: approvedBinding ? approvedBinding.apply_time : p.created_at
      }
    })
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  }
})

const statistics = computed(() => ({
  totalUsers: allDoctors.value.length + allPatients.value.length,
  doctorCount: allDoctors.value.length,
  patientCount: allPatients.value.length,
  bindingCount: allBindings.value.length
}))

const pendingDoctors = ref([])

const allDoctors = ref([])

const allPatients = ref([])
const allBindings = ref([])

const filteredDoctors = computed(() => {
  if (!doctorSearch.value) return allDoctors.value
  return allDoctors.value.filter(
    d =>
      d.realName.includes(doctorSearch.value) ||
      d.hospital.includes(doctorSearch.value)
  )
})

const filteredPatients = computed(() => {
  if (!patientSearch.value) return allPatients.value
  return allPatients.value.filter(p =>
    p.realName.includes(patientSearch.value)
  )
})

const getTitleText = (title) => {
  const map = {
    chief: '主任医师',
    associate_chief: '副主任医师',
    attending: '主治医师',
    resident: '住院医师'
  }
  return map[title] || title
}

const getAuditStatusText = (status) => DOCTOR_AUDIT_STATUS_TEXT[status]
const getAuditStatusType = (status) => DOCTOR_AUDIT_STATUS_TYPE[status]
const getBindingStatusText = (status) => BINDING_STATUS_TEXT[status]
const getBindingStatusType = (status) => BINDING_STATUS_TYPE[status]

const handleApproveDoctor = async (row) => {
  try {
    await adminAPI.approveDoctor(row.id)
    ElMessage.success(`已通过医生 ${row.realName} 的注册申请`)
    row.status = DOCTOR_AUDIT_STATUS.APPROVED

    // 从待审核列表中移除
    const index = pendingDoctors.value.findIndex(d => d.id === row.id)
    if (index !== -1) {
      pendingDoctors.value.splice(index, 1)
    }

    // 添加到医生列表
    allDoctors.value.unshift({
      id: row.id,
      username: row.username,
      realName: row.realName,
      hospital: row.hospital,
      department: row.department,
      patientCount: 0,
      taskCount: 0,
      lastLoginTime: '-',
      status: DOCTOR_AUDIT_STATUS.APPROVED
    })
  } catch (error) {
    console.error('审核失败:', error)
    ElMessage.error(typeof error === 'string' ? error : '审核失败')
  }
}

const handleRejectDoctor = async (row) => {
  try {
    await adminAPI.rejectDoctor(row.id)
    ElMessage.warning(`已拒绝医生 ${row.realName} 的注册申请`)
    row.status = DOCTOR_AUDIT_STATUS.REJECTED

    // 从待审核列表中移除
    const index = pendingDoctors.value.findIndex(d => d.id === row.id)
    if (index !== -1) {
      pendingDoctors.value.splice(index, 1)
    }
  } catch (error) {
    console.error('审核失败:', error)
    ElMessage.error(typeof error === 'string' ? error : '审核失败')
  }
}

const handleViewDoctor = (row) => {
  router.push(`/admin/doctor/${row.id}`)
}

const handleDeleteDoctor = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除医生 ${row.realName} 吗？删除后该医生的所有数据将无法恢复。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const handleViewPatient = (row) => {
  router.push(`/admin/patient/${row.id}`)
}

const handleDeletePatient = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除患者 ${row.realName} 吗？删除后该患者的所有数据将无法恢复。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const handleUnbind = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要解除 ${row.patientName} 和 ${row.doctorName} 的绑定关系吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await adminAPI.unbindRelationship(row.id)
    ElMessage.success('解除绑定成功')
    row.status = BINDING_STATUS.UNBOUND
  } catch (error) {
    if (error !== 'cancel') {
      console.error('解除绑定失败:', error)
      ElMessage.error(typeof error === 'string' ? error : '解除绑定失败')
    }
  }
}

const handleResetDoctorPassword = (row) => {
  resetPasswordForm.value = {
    userId: row.id,
    userName: row.realName,
    userType: 'doctor',
    newPassword: '',
    confirmPassword: ''
  }
  resetPasswordTitle.value = `重���医生密码 - ${row.realName}`
  resetPasswordDialogVisible.value = true
}

const handleResetPatientPassword = (row) => {
  resetPasswordForm.value = {
    userId: row.id,
    userName: row.realName,
    userType: 'patient',
    newPassword: '',
    confirmPassword: ''
  }
  resetPasswordTitle.value = `重置患者���码 - ${row.realName}`
  resetPasswordDialogVisible.value = true
}

const handleConfirmResetPassword = async () => {
  const { newPassword, confirmPassword, userId, userName, userType } = resetPasswordForm.value

  if (!newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }

  if (newPassword.length < 6) {
    ElMessage.warning('密码长���不能少于6位')
    return
  }

  if (newPassword !== confirmPassword) {
    ElMessage.warning('两次���入的���码不一致')
    return
  }

  try {
    if (userType === 'doctor') {
      await adminAPI.resetDoctorPassword(userId, { new_password: newPassword })
      ElMessage.success(`���生 ${userName} 的密���已重置`)
    } else {
      await adminAPI.resetPatientPassword(userId, { new_password: newPassword })
      ElMessage.success(`患者 ${userName} 的密码���重置`)
    }

    resetPasswordDialogVisible.value = false
    resetPasswordForm.value = {
      userId: null,
      userName: '',
      userType: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    console.error('重���密码���败:', error)
    ElMessage.error(typeof error === 'string' ? error : '���置密码失���')
  }
}

const handleLogout = () => {
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
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

.stat-card {
  text-align: center;
}
</style>
