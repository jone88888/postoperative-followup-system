<template>
  <div class="dashboard">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>患者工作台</h2>
          <div>
            <span style="margin-right: 20px">{{ patientName }}</span>
            <el-button @click="handleLogout">退出登录</el-button>
          </div>
        </div>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card>
              <el-statistic title="待完成任务" :value="statistics.pendingTasks" />
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <el-statistic title="已完成任务" :value="statistics.completedTasks" />
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <el-statistic title="逾期任务" :value="statistics.overdueTasks" />
            </el-card>
          </el-col>
        </el-row>

        <PatientBindingManagement
          v-if="patientId"
          :patient-id="patientId"
          style="margin-top: 20px"
        />

        <el-card style="margin-top: 20px">
          <template #header>
            <span>我的随访任务</span>
          </template>
          <el-table :data="tasks" style="width: 100%">
            <el-table-column prop="title" label="任务名称" />
            <el-table-column prop="doctor_name" label="医生" />
            <el-table-column prop="deadline" label="截止时间" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleViewTask(row)">
                  查看详情
                </el-button>
                <el-button
                  v-if="row.status !== 'completed'"
                  link
                  type="success"
                  size="small"
                  @click="handleAnswerTask(row)"
                >
                  回答任务
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>

    <!-- 查看任务详情对话框 -->
    <el-dialog v-model="showViewDialog" title="任务详情" width="600px">
      <el-descriptions v-if="currentTask" :column="1" border>
        <el-descriptions-item label="医生">{{ currentTask.doctor_name }}</el-descriptions-item>
        <el-descriptions-item label="任务标题">{{ currentTask.title }}</el-descriptions-item>
        <el-descriptions-item label="任务内容">{{ currentTask.content }}</el-descriptions-item>
        <el-descriptions-item label="截止时间">{{ formatDateTime(currentTask.deadline) }}</el-descriptions-item>
        <el-descriptions-item label="任务状态">
          <el-tag :type="getStatusType(currentTask.status)">
            {{ getStatusText(currentTask.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="任务类型">
          <el-space wrap>
            <el-tag
              v-for="type in getTaskTypes(currentTask.task_types)"
              :key="type"
            >
              {{ getTaskTypeText(type) }}
            </el-tag>
          </el-space>
        </el-descriptions-item>
        <el-descriptions-item v-if="getNumberFields(currentTask.task_types).length > 0" label="数值项">
          <el-space wrap>
            <el-tag
              v-for="field in getNumberFields(currentTask.task_types)"
              :key="field"
              type="info"
            >
              {{ field }}
            </el-tag>
          </el-space>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 回答任务对话框 -->
    <el-dialog v-model="showAnswerDialog" title="回答任务" width="700px">
      <el-form v-if="answerForm" :model="answerForm" label-width="100px">
        <el-form-item label="任务标题">
          <el-text>{{ answerForm.title }}</el-text>
        </el-form-item>
        <el-form-item label="任务内容">
          <el-text>{{ answerForm.content }}</el-text>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-text>{{ answerForm.deadline }}</el-text>
        </el-form-item>

        <!-- 文字描述 -->
        <el-form-item v-if="answerForm.taskTypes.includes('text')" label="文字描述">
          <el-input
            v-model="answerForm.textResponse"
            type="textarea"
            :rows="4"
            placeholder="请输入您的文字描述"
          />
        </el-form-item>

        <!-- 图片上传 -->
        <el-form-item v-if="answerForm.taskTypes.includes('image')" label="图片上传">
          <el-upload
            v-model:file-list="answerForm.imageFiles"
            action="#"
            list-type="picture-card"
            :auto-upload="false"
            :limit="5"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <!-- 数值填写 -->
        <el-form-item v-if="answerForm.taskTypes.includes('number')" label="数值填写">
          <div style="width: 100%">
            <div
              v-for="field in answerForm.numberFields"
              :key="field"
              style="margin-bottom: 10px; display: flex; align-items: center"
            >
              <span style="width: 150px">{{ field }}：</span>
              <el-input-number
                v-model="answerForm.numberValues[field]"
                :controls="false"
                style="width: 200px"
              />
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAnswerDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitAnswer">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { TASK_STATUS, TASK_STATUS_TEXT, TASK_STATUS_TYPE } from '@/utils/enum'
import { patientAPI } from '@/api'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PatientBindingManagement from '@/components/PatientBindingManagement.vue'

const router = useRouter()
const patientName = ref('患者')
const patientId = ref(null)
const tasks = ref([])
const showViewDialog = ref(false)
const showAnswerDialog = ref(false)
const currentTask = ref(null)
const answerForm = ref(null)

onMounted(async () => {
  const userStr = localStorage.getItem('userInfo')
  console.log('localStorage中的userInfo数据:', userStr)

  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      console.log('解析后的user对象:', user)
      console.log('profile_id:', user.profile_id)

      // 使用profile_id获取患者详细信息
      if (user.profile_id) {
        patientId.value = user.profile_id
        console.log('开始调用patientAPI.getInfo，patient_id=', user.profile_id)
        const patientInfo = await patientAPI.getInfo(user.profile_id)
        console.log('获取到的患者信息:', patientInfo)
        patientName.value = patientInfo.real_name
        console.log('设置patientName为:', patientName.value)

        // 获取患者任务列表
        const tasksData = await patientAPI.getTasks(user.profile_id)
        console.log('获取到的任务列表:', tasksData)
        tasks.value = tasksData
      } else {
        console.error('user对象中没有profile_id字段')
        ElMessage.warning('请重新登录以获取完整用户信息')
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      ElMessage.error('获取用户信息失败: ' + error)
    }
  }
})

const statistics = computed(() => ({
  pendingTasks: tasks.value.filter(t => t.status === TASK_STATUS.IN_PROGRESS).length,
  completedTasks: tasks.value.filter(t => t.status === TASK_STATUS.COMPLETED).length,
  overdueTasks: 0
}))

const getStatusType = (status) => {
  return TASK_STATUS_TYPE[status]
}

const getStatusText = (status) => {
  return TASK_STATUS_TEXT[status]
}

const handleViewTask = async (row) => {
  try {
    const data = await patientAPI.getTaskDetail(row.id, patientId.value)
    currentTask.value = data
    showViewDialog.value = true
  } catch (error) {
    console.error('���取任���详情���败:', error)
    ElMessage.error(typeof error === 'string' ? error : '获取���务���情失败')
  }
}

const handleAnswerTask = (row) => {
  const taskTypes = getTaskTypes(row.task_types)
  const numberFields = getNumberFields(row.task_types)

  const numberValues = {}
  numberFields.forEach(field => {
    numberValues[field] = 0
  })

  answerForm.value = {
    id: row.id,
    title: row.title,
    content: row.content,
    deadline: row.deadline,
    taskTypes: taskTypes,
    numberFields: numberFields,
    textResponse: '',
    imageFiles: [],
    numberValues: numberValues
  }
  showAnswerDialog.value = true
}

const taskTypeMap = {
  text: '文字描述',
  image: '图片上传',
  number: '数值填写'
}

const getTaskTypeText = (type) => {
  return taskTypeMap[type] || type
}

const getTaskTypes = (taskTypes) => {
  if (Array.isArray(taskTypes)) {
    return taskTypes
  }
  if (taskTypes && typeof taskTypes === 'object' && taskTypes.types) {
    return taskTypes.types
  }
  return []
}

const getNumberFields = (taskTypes) => {
  if (taskTypes && typeof taskTypes === 'object' && taskTypes.numberFields) {
    return taskTypes.numberFields
  }
  return []
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const handleSubmitAnswer = async () => {
  if (!answerForm.value) return

  // 验证至少填写了一种类型的回答
  const hasText = answerForm.value.taskTypes.includes('text') && answerForm.value.textResponse.trim()
  const hasImage = answerForm.value.taskTypes.includes('image') && answerForm.value.imageFiles.length > 0
  const hasNumber = answerForm.value.taskTypes.includes('number') &&
    Object.keys(answerForm.value.numberValues).length > 0

  if (!hasText && !hasImage && !hasNumber) {
    ElMessage.warning('请至少完成一种类型的任务回答')
    return
  }

  try {
    const submitData = {
      patient_id: patientId.value
    }

    // 根据任务类型添加对应的数据
    if (answerForm.value.taskTypes.includes('text')) {
      submitData.text_response = answerForm.value.textResponse || ''
    }

    if (answerForm.value.taskTypes.includes('number')) {
      submitData.number_values = answerForm.value.numberValues
    }

    if (answerForm.value.taskTypes.includes('image') && answerForm.value.imageFiles.length > 0) {
      // 这里简化处理，实际应该上传图片并获取URL
      submitData.image_urls = answerForm.value.imageFiles.map(file => file.url || file.name)
    }

    await patientAPI.submitTask(answerForm.value.id, submitData)

    ElMessage.success('任务提交成功')
    showAnswerDialog.value = false

    // 重新加载任务列表
    const tasksData = await patientAPI.getTasks(patientId.value)
    tasks.value = tasksData
  } catch (error) {
    console.error('提交任务失败:', error)
    ElMessage.error(typeof error === 'string' ? error : '提交任务失败')
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
</style>
