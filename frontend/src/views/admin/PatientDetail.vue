<template>
  <div class="detail-page">
    <el-container>
      <el-header>
        <div class="header-content">
          <div>
            <el-button @click="handleBack" link>
              <el-icon><ArrowLeft /></el-icon>
              返回患者列表
            </el-button>
          </div>
          <h2>患者详细信息</h2>
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

          <el-form :model="patientForm" label-width="120px" :disabled="!isEditing">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="患者姓名">
                  <el-input v-model="patientForm.real_name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="身份证号">
                  <el-input v-model="patientForm.id_card" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="性别">
                  <el-radio-group v-model="patientForm.gender">
                    <el-radio label="male">男</el-radio>
                    <el-radio label="female">女</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="年龄">
                  <el-input-number v-model="patientForm.age" :min="1" :max="150" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="手术类型">
                  <el-input v-model="patientForm.surgery_type" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="手术日期">
                  <el-date-picker
                    v-model="patientForm.surgery_date"
                    type="date"
                    placeholder="选择日期"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="账户状态">
                  <el-switch
                    v-model="patientForm.is_active"
                    active-text="启用"
                    inactive-text="禁用"
                    @change="handleToggleStatus"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系电话">
                  <el-input v-model="patientForm.phone" disabled />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名">
                  <el-input v-model="patientForm.username" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="注册时间">
                  <el-input :value="formatDateTime(patientForm.created_at)" disabled />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>随访提交记录</span>
              <el-button type="primary" @click="handleViewSubmissions">
                查看患者填写的随访内容
              </el-button>
            </div>
          </template>

          <el-empty v-if="submissions.length === 0" description="暂无随访记录" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="submission in submissions"
              :key="submission.id"
              :timestamp="formatDateTime(submission.submitted_at)"
              placement="top"
            >
              <el-card>
                <h4>{{ submission.task_title }}</h4>
                <p style="color: #666; margin: 8px 0">{{ submission.task_content }}</p>
                <el-tag
                  v-for="type in submission.task_types"
                  :key="type"
                  size="small"
                  style="margin-right: 5px"
                >
                  {{ getTaskTypeText(type) }}
                </el-tag>
                <div v-if="submission.content" style="margin-top: 12px">
                  <strong>提交内容：</strong>{{ submission.content }}
                </div>
                <div v-if="submission.images && submission.images.length > 0" style="margin-top: 12px">
                  <strong>附件图片：</strong>
                  <el-image
                    v-for="(img, idx) in submission.images"
                    :key="idx"
                    :src="img"
                    :preview-src-list="submission.images"
                    style="width: 100px; height: 100px; margin-right: 8px"
                    fit="cover"
                  />
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-main>
    </el-container>

    <!-- 随访提交记录对话框 -->
    <el-dialog v-model="submissionsDialogVisible" title="患者随访提交记录" width="900px">
      <el-table :data="submissions" style="width: 100%">
        <el-table-column prop="task_title" label="任务名称" width="200" />
        <el-table-column prop="task_content" label="任务内容" show-overflow-tooltip />
        <el-table-column prop="submitted_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.submitted_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleViewSubmissionDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 提交详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="随访提交详情" width="700px">
      <div v-if="currentSubmission">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务标题">
            {{ currentSubmission.task_title }}
          </el-descriptions-item>
          <el-descriptions-item label="任务内容">
            {{ currentSubmission.task_content }}
          </el-descriptions-item>
          <el-descriptions-item label="任务类型">
            <el-tag
              v-for="type in currentSubmission.task_types"
              :key="type"
              size="small"
              style="margin-right: 5px"
            >
              {{ getTaskTypeText(type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="截止时间">
            {{ formatDateTime(currentSubmission.task_deadline) }}
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{ formatDateTime(currentSubmission.submitted_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="提交内容">
            {{ currentSubmission.content || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="附件图片">
            <el-image
              v-for="(img, idx) in currentSubmission.images"
              :key="idx"
              :src="img"
              :preview-src-list="currentSubmission.images"
              style="width: 100px; height: 100px; margin-right: 8px"
              fit="cover"
            />
            <span v-if="!currentSubmission.images || currentSubmission.images.length === 0">无</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
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
const submissionsDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentSubmission = ref(null)
const submissions = ref([])

const patientForm = ref({
  real_name: '',
  id_card: '',
  gender: 'male',
  age: 0,
  surgery_type: '',
  surgery_date: '',
  is_active: true,
  phone: '',
  username: '',
  user_id: null,
  created_at: ''
})

const originalPatientData = ref({})

const taskTypeMap = {
  text: '文字描述',
  image: '图片上传',
  number: '数值填写'
}

onMounted(async () => {
  await loadPatientDetail()
  await loadSubmissions()
})

const loadPatientDetail = async () => {
  loading.value = true
  try {
    const patientId = route.params.id || route.query.patientId
    const data = await adminAPI.getPatientDetail(patientId)
    patientForm.value = { ...data }
    originalPatientData.value = { ...data }
  } catch (error) {
    console.error('获取患者信息失败:', error)
    ElMessage.error('获取患者信息失败')
  } finally {
    loading.value = false
  }
}

const loadSubmissions = async () => {
  try {
    const patientId = route.params.id || route.query.patientId
    const data = await adminAPI.getPatientSubmissions(patientId)
    submissions.value = data
  } catch (error) {
    console.error('获取随访记录失败:', error)
    ElMessage.error('获取随访记录失败')
  }
}

const handleEdit = () => {
  isEditing.value = true
}

const handleCancelEdit = () => {
  isEditing.value = false
  patientForm.value = { ...originalPatientData.value }
}

const handleSave = async () => {
  try {
    const patientId = route.params.id || route.query.patientId
    const updateData = {
      real_name: patientForm.value.real_name,
      id_card: patientForm.value.id_card,
      gender: patientForm.value.gender,
      age: patientForm.value.age,
      surgery_type: patientForm.value.surgery_type,
      surgery_date: patientForm.value.surgery_date
    }
    await adminAPI.updatePatient(patientId, updateData)
    ElMessage.success('保存成功')
    isEditing.value = false
    originalPatientData.value = { ...patientForm.value }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

const handleToggleStatus = async (value) => {
  try {
    await ElMessageBox.confirm(
      `确定要${value ? '启用' : '禁用'}该患者账户吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await adminAPI.toggleUserStatus(patientForm.value.user_id)
    ElMessage.success(value ? '账户已启用' : '账户已禁用')
    originalPatientData.value.is_active = value
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换状态失败:', error)
      ElMessage.error('操作失败')
    }
    patientForm.value.is_active = !value
  }
}

const handleViewSubmissions = () => {
  submissionsDialogVisible.value = true
}

const handleViewSubmissionDetail = (row) => {
  currentSubmission.value = row
  detailDialogVisible.value = true
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getTaskTypeText = (type) => {
  return taskTypeMap[type] || type
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
