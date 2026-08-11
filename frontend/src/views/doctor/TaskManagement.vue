<template>
  <div class="task-management">
    <el-card v-loading="loading">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>任务管理</span>
          <div>
            <el-button
              v-if="selectedTasks.length > 0"
              type="danger"
              @click="handleBatchDelete"
              style="margin-right: 10px"
            >
              删除选中 ({{ selectedTasks.length }})
            </el-button>
            <el-button type="primary" @click="$router.push('/doctor/dashboard')">
              返回
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="tasks"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="patient_name" label="患者" width="120" />
        <el-table-column prop="title" label="任务标题" />
        <el-table-column prop="deadline" label="截止时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.deadline) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleViewTask(row)">
              查看
            </el-button>
            <el-button
              v-if="row.status !== 'completed'"
              link
              type="warning"
              size="small"
              @click="handleEditTask(row)"
            >
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 查看任务详情对话框 -->
    <el-dialog v-model="showViewDialog" title="任务详情" width="600px">
      <el-descriptions v-if="currentTask" :column="1" border>
        <el-descriptions-item label="患者">{{ currentTask.patient_name }}</el-descriptions-item>
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

      <!-- 显示患者���交记录 -->
      <div v-if="currentTask && currentTask.submissions && currentTask.submissions.length > 0" style="margin-top: 20px">
        <el-divider>患者提提交记录</el-divider>
        <el-card v-for="submission in currentTask.submissions" :key="submission.id" style="margin-bottom: 15px">
          <template #header>
            <div style="display: flex; justify-content: space-between">
              <span>提交人: {{ submission.patient_name }}</span>
              <span>提交时间: {{ formatDateTime(submission.submitted_at) }}</span>
            </div>
          </template>
          <div v-if="submission.submission_data">
            <div v-if="submission.submission_data.text_response" style="margin-bottom: 10px">
              <strong>文字描述：</strong>
              <p style="margin: 5px 0">{{ submission.submission_data.text_response }}</p>
            </div>
            <div v-if="submission.submission_data.number_values" style="margin-bottom: 10px">
              <strong>数值填写：</strong>
              <div v-for="(value, key) in submission.submission_data.number_values" :key="key" style="margin: 5px 0">
                <span>{{ key }}: </span>
                <el-tag type="info">{{ value }}</el-tag>
              </div>
            </div>
            <div v-if="submission.submission_data.image_urls && submission.submission_data.image_urls.length > 0" style="margin-bottom: 10px">
              <strong>图片：</strong>
              <div style="margin-top: 5px">
                <el-image
                  v-for="(img, idx) in submission.submission_data.image_urls"
                  :key="idx"
                  :src="img"
                  :preview-src-list="submission.submission_data.image_urls"
                  fit="cover"
                  style="width: 100px; height: 100px; margin-right: 10px; border-radius: 4px"
                />
              </div>
            </div>
            <div v-if="submission.notes" style="margin-bottom: 10px">
              <strong>注释：</strong>
              <p style="margin: 5px 0">{{ submission.notes }}</p>
            </div>
          </div>
        </el-card>
      </div>
      <el-empty v-else-if="currentTask && currentTask.status === 'completed'" description="���无提交记录" />
    </el-dialog>

    <!-- 编辑任务对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑任务" width="700px">
      <el-form v-if="editForm" :model="editForm" label-width="100px">
        <el-form-item label="患者">
          <el-text>{{ editForm.patient_name }}</el-text>
        </el-form-item>
        <el-form-item label="任务标题">
          <el-input v-model="editForm.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务内容">
          <el-input
            v-model="editForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入任务内容说明"
          />
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="editForm.deadline"
            type="datetime"
            placeholder="选择截止时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-checkbox-group v-model="editForm.types">
            <el-checkbox value="text">文字描述</el-checkbox>
            <el-checkbox value="image">图片上传</el-checkbox>
            <el-checkbox value="number">数值填写</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <!-- 数值填写的自定义字段 -->
        <el-form-item v-if="editForm.types.includes('number')" label="数值项配置">
          <div style="width: 100%">
            <div style="margin-bottom: 10px">
              <el-input
                v-model="newNumberField"
                placeholder="输入数值项名称，如：疼痛评分、止痛药剂量"
                style="width: 300px; margin-right: 10px"
                @keyup.enter="addNumberField"
              />
              <el-button type="primary" size="small" @click="addNumberField">添加</el-button>
            </div>
            <el-space wrap>
              <el-tag
                v-for="(field, index) in editForm.numberFields"
                :key="index"
                closable
                @close="removeNumberField(index)"
                style="margin-bottom: 5px"
              >
                {{ field }}
              </el-tag>
            </el-space>
            <el-text v-if="editForm.numberFields.length === 0" type="info" size="small">
              请添加至少一个数值项，患者将填写对应的数值
            </el-text>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTask">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { doctorAPI } from '@/api'

const router = useRouter()
const loading = ref(false)
const tasks = ref([])
const showViewDialog = ref(false)
const showEditDialog = ref(false)
const currentTask = ref(null)
const editForm = ref(null)
const selectedTasks = ref([])
const newNumberField = ref('')

const statusMap = {
  not_started: { text: '未开始', type: 'info' },
  in_progress: { text: '进行中', type: 'warning' },
  completed: { text: '已完成', type: 'success' }
}

const taskTypeMap = {
  text: '文字描述',
  image: '图片上传',
  number: '数值填写'
}

onMounted(async () => {
  await loadTasks()
})

const loadTasks = async () => {
  loading.value = true
  try {
    const userStr = localStorage.getItem('userInfo')
    if (!userStr) {
      ElMessage.error('请重新登录')
      router.push('/login')
      return
    }

    const user = JSON.parse(userStr)
    const data = await doctorAPI.getTasks(user.profile_id)
    tasks.value = data
  } catch (error) {
    console.error('获取任务列表失败:', error)
    ElMessage.error(typeof error === 'string' ? error : '获取任务列表失败')
  } finally {
    loading.value = false
  }
}

const handleViewTask = async (row) => {
  try {
    const userStr = localStorage.getItem('userInfo')
    const user = JSON.parse(userStr)
    const data = await doctorAPI.getTaskDetail(row.id, user.profile_id)
    currentTask.value = data
    showViewDialog.value = true
  } catch (error) {
    console.error('获取任务详情失败:', error)
    ElMessage.error(typeof error === 'string' ? error : '获取任务详情失败')
  }
}

const handleEditTask = async (row) => {
  try {
    const userStr = localStorage.getItem('userInfo')
    const user = JSON.parse(userStr)
    const data = await doctorAPI.getTaskDetail(row.id, user.profile_id)

    const taskTypes = getTaskTypes(data.task_types)
    const numberFields = getNumberFields(data.task_types)

    editForm.value = {
      id: data.id,
      patient_name: data.patient_name,
      title: data.title,
      content: data.content,
      deadline: new Date(data.deadline),
      types: taskTypes,
      numberFields: [...numberFields]
    }
    showEditDialog.value = true
  } catch (error) {
    console.error('获取任务详情失败:', error)
    ElMessage.error(typeof error === 'string' ? error : '获取任务详情失败')
  }
}

const handleSaveTask = async () => {
  if (!editForm.value.title) {
    ElMessage.warning('请输入任务标题')
    return
  }

  if (!editForm.value.content) {
    ElMessage.warning('请输入任务内容')
    return
  }

  if (editForm.value.types.length === 0) {
    ElMessage.warning('请至少选择一种任务类型')
    return
  }

  if (editForm.value.types.includes('number') && editForm.value.numberFields.length === 0) {
    ElMessage.warning('请为数值填写添加至少一个数值项')
    return
  }

  try {
    const userStr = localStorage.getItem('userInfo')
    const user = JSON.parse(userStr)

    const taskTypesData = {
      types: editForm.value.types,
      numberFields: editForm.value.types.includes('number') ? editForm.value.numberFields : []
    }

    await doctorAPI.updateTask(editForm.value.id, {
      title: editForm.value.title,
      content: editForm.value.content,
      deadline: editForm.value.deadline.toISOString(),
      task_types: taskTypesData,
      doctor_id: user.profile_id
    })

    ElMessage.success('任务更新成功')
    showEditDialog.value = false
    await loadTasks()
  } catch (error) {
    console.error('更新任务失败:', error)
    ElMessage.error(typeof error === 'string' ? error : '更新任务失败')
  }
}

const addNumberField = () => {
  if (!newNumberField.value.trim()) {
    ElMessage.warning('请输入数值项名称')
    return
  }

  if (editForm.value.numberFields.includes(newNumberField.value.trim())) {
    ElMessage.warning('该数值项已存在')
    return
  }

  editForm.value.numberFields.push(newNumberField.value.trim())
  newNumberField.value = ''
}

const removeNumberField = (index) => {
  editForm.value.numberFields.splice(index, 1)
}

const handleSelectionChange = (selection) => {
  selectedTasks.value = selection
}

const handleBatchDelete = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请选择要删除的任务')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTasks.value.length} 个任务吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const userStr = localStorage.getItem('userInfo')
    const user = JSON.parse(userStr)

    for (const task of selectedTasks.value) {
      await doctorAPI.deleteTask(task.id, user.profile_id)
    }

    ElMessage.success(`成功删除 ${selectedTasks.value.length} 个任务`)
    selectedTasks.value = []
    await loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除任务失败:', error)
      ElMessage.error(typeof error === 'string' ? error : '批量删除任务失败')
    }
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getStatusText = (status) => {
  return statusMap[status]?.text || status
}

const getStatusType = (status) => {
  return statusMap[status]?.type || 'info'
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
</script>

<style scoped>
.task-management {
  padding: 20px;
}
</style>
