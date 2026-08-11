<template>
  <div class="dashboard">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>医生工作台</h2>
          <div>
            <el-button type="primary" @click="$router.push('/doctor/tasks')" style="margin-right: 10px">
              任务管理
            </el-button>
            <span style="margin-right: 20px">{{ doctorInfo?.real_name || '医生' }}</span>
            <el-button @click="handleLogout">退出登录</el-button>
          </div>
        </div>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card>
              <el-statistic title="我的患者" :value="statistics.patientCount" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card>
              <el-statistic title="待审核绑定" :value="statistics.pendingBindings" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card>
              <el-statistic title="待处理反馈" :value="statistics.pendingFeedbacks" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card>
              <el-statistic title="未完成任务" :value="statistics.incompleteTasks" />
            </el-card>
          </el-col>
        </el-row>

        <el-tabs v-model="activeTab" style="margin-top: 20px">
          <el-tab-pane label="患者绑定审核" name="bindings">
            <el-card>
              <el-table :data="bindingRequests" style="width: 100%">
                <el-table-column prop="patientName" label="患者姓名" />
                <el-table-column prop="phone" label="手机号" />
                <el-table-column prop="surgeryType" label="手术类型" />
                <el-table-column prop="applyTime" label="申请时间" />
                <el-table-column prop="status" label="状态">
                  <template #default="{ row }">
                    <el-tag :type="getBindingStatusType(row.status)">
                      {{ getBindingStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180">
                  <template #default="{ row }">
                    <template v-if="row.status === BINDING_STATUS.PENDING">
                      <el-button link type="success" size="small" @click="handleApproveBinding(row)">
                        通过
                      </el-button>
                      <el-button link type="danger" size="small" @click="handleRejectBinding(row)">
                        拒绝
                      </el-button>
                    </template>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="我的患者" name="patients">
            <el-card>
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center">
                  <span>患者列表</span>
                  <el-input
                    v-model="searchKeyword"
                    placeholder="搜索患者姓名"
                    style="width: 200px"
                    clearable
                  />
                </div>
              </template>
              <el-table :data="filteredPatients" style="width: 100%">
                <el-table-column prop="name" label="患者姓名" />
                <el-table-column prop="gender" label="性别">
                  <template #default="{ row }">
                    {{ row.gender === 'male' ? '男' : '女' }}
                  </template>
                </el-table-column>
                <el-table-column prop="age" label="年龄" />
                <el-table-column prop="surgery" label="手术类型" />
                <el-table-column prop="bindDate" label="绑定时间" />
                <el-table-column label="任务完成率">
                  <template #default="{ row }">
                    <el-progress
                      :percentage="row.completionRate"
                      :color="getProgressColor(row.completionRate)"
                    />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="handleViewPatient(row)">
                      查看详情
                    </el-button>
                    <el-button link type="primary" size="small" @click="handleCreateTask(row)">
                      发布任务
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="任务管理" name="tasks">
            <el-card>
              <el-table :data="allTasks" style="width: 100%">
                <el-table-column prop="patientName" label="患者" />
                <el-table-column prop="taskTitle" label="任务名称" />
                <el-table-column prop="deadline" label="截止时间" />
                <el-table-column prop="status" label="状态">
                  <template #default="{ row }">
                    <el-tag :type="getTaskStatusType(row.status)">
                      {{ getTaskStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="submitTime" label="提交时间" />
                <el-table-column label="操作">
                  <template #default="{ row }">
                    <el-button
                      link
                      type="primary"
                      size="small"
                      @click="handleViewFeedback(row)"
                      :disabled="row.status === TASK_STATUS.NOT_STARTED"
                    >
                      查看反馈
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>

    <!-- 发布任务对话框 -->
    <el-dialog v-model="taskDialogVisible" title="发布随访任务" width="700px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="患者">
          <el-text>{{ currentPatient?.name }}</el-text>
        </el-form-item>
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务内容">
          <el-input
            v-model="taskForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入任务内容说明"
          />
        </el-form-item>
        <el-form-item label="随访类型">
          <el-radio-group v-model="taskForm.followupType">
            <el-radio value="single">单次随��</el-radio>
            <el-radio value="multiple">多次随访</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 单次随访 -->
        <el-form-item v-if="taskForm.followupType === 'single'" label="截止时间">
          <el-date-picker
            v-model="taskForm.singleDeadline"
            type="datetime"
            placeholder="选择截止时间"
            style="width: 100%"
          />
        </el-form-item>

        <!-- 多次随访 -->
        <el-form-item v-if="taskForm.followupType === 'multiple'" label="随访日期">
          <div style="width: 100%">
            <div style="margin-bottom: 10px">
              <el-space wrap>
                <el-button size="small" @click="addQuickDate(7)">术后第7天</el-button>
                <el-button size="small" @click="addQuickDate(14)">术后第14天</el-button>
                <el-button size="small" @click="addQuickDate(30)">术后第1个月</el-button>
                <el-button size="small" @click="addQuickDate(90)">术后第3个月</el-button>
                <el-button size="small" @click="addQuickDate(180)">术后第6个月</el-button>
              </el-space>
            </div>
            <el-date-picker
              v-model="taskForm.followupDates"
              type="dates"
              placeholder="选择多个随访日期"
              style="width: 100%; margin-bottom: 10px"
            />
            <el-tag
              v-for="(date, index) in sortedFollowupDates"
              :key="index"
              closable
              @close="removeDate(date)"
              style="margin-right: 5px; margin-bottom: 5px"
            >
              {{ formatDate(date) }}
            </el-tag>
          </div>
        </el-form-item>

        <el-form-item label="任务类型">
          <el-checkbox-group v-model="taskForm.types">
            <el-checkbox value="text">文字描述</el-checkbox>
            <el-checkbox value="image">图片上传</el-checkbox>
            <el-checkbox value="number">数值填写</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <!-- 数值填写的自定义字段 -->
        <el-form-item v-if="taskForm.types.includes('number')" label="数值项配置">
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
                v-for="(field, index) in taskForm.numberFields"
                :key="index"
                closable
                @close="removeNumberField(index)"
                style="margin-bottom: 5px"
              >
                {{ field }}
              </el-tag>
            </el-space>
            <el-text v-if="taskForm.numberFields.length === 0" type="info" size="small">
              请添加至少一个数值项，患者将填写对应的数值
            </el-text>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitTask">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  BINDING_STATUS,
  BINDING_STATUS_TEXT,
  BINDING_STATUS_TYPE,
  TASK_STATUS,
  TASK_STATUS_TEXT,
  TASK_STATUS_TYPE
} from '@/utils/enum'
import { doctorAPI } from '@/api'

const router = useRouter()
const activeTab = ref('bindings')
const searchKeyword = ref('')
const taskDialogVisible = ref(false)
const currentPatient = ref(null)
const doctorInfo = ref(null)

onMounted(async () => {
  const userStr = localStorage.getItem('userInfo')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)

      // 使用profile_id获取医生的绑定请求列表和患者列表
      if (user.profile_id) {
        // 获取医生详细信息
        try {
          const doctorDetail = await doctorAPI.getInfo(user.profile_id)
          doctorInfo.value = doctorDetail
        } catch (error) {
          console.log('获取医生详细信息失败，使用基本信息:', error)
          doctorInfo.value = user
        }

        // 获取绑定请求
        const bindings = await doctorAPI.getPendingBindings(user.profile_id)
        bindingRequests.value = bindings.map(b => ({
          id: b.id,
          patientName: b.patient_name,
          phone: b.patient_phone,
          surgeryType: b.surgery_type,
          applyTime: b.apply_time,
          status: b.status
        }))

        // 获取已绑定的患者列表
        const patientData = await doctorAPI.getPatients(user.profile_id)
        patients.value = patientData.map(p => ({
          id: p.id,
          name: p.real_name,
          gender: p.gender,
          age: p.age,
          surgery: p.surgery_type,
          bindDate: p.bind_date || p.created_at,
          completionRate: p.completion_rate || 0
        }))

        // 获取医生的所有任务
        const tasks = await doctorAPI.getTasks(user.profile_id)
        allTasks.value = tasks
      }
    } catch (error) {
      console.error('获取数据失败:', error)
      ElMessage.error('获取数据失败')
    }
  }
})

const statistics = computed(() => ({
  patientCount: patients.value.length,
  pendingBindings: bindingRequests.value.filter(b => b.status === BINDING_STATUS.PENDING).length,
  pendingFeedbacks: 0,  // 待处理反馈暂无功能
  incompleteTasks: allTasks.value.filter(t => t.status !== 'completed').length
}))

const bindingRequests = ref([])

const patients = ref([])

const allTasks = ref([])

const taskForm = reactive({
  title: '',
  content: '',
  followupType: 'single',
  singleDeadline: '',
  followupDates: [],
  types: [],
  numberFields: [] // 数值填写的自定义字段
})

const surgeryDate = ref(new Date()) // 模拟手术日期，实际应该从患者数据中获取
const newNumberField = ref('') // 新数值项输入

const filteredPatients = computed(() => {
  if (!searchKeyword.value) return patients.value
  return patients.value.filter(p =>
    p.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const getBindingStatusText = (status) => BINDING_STATUS_TEXT[status]
const getBindingStatusType = (status) => BINDING_STATUS_TYPE[status]
const getTaskStatusText = (status) => TASK_STATUS_TEXT[status]
const getTaskStatusType = (status) => TASK_STATUS_TYPE[status]

const getProgressColor = (percentage) => {
  if (percentage < 60) return '#F56C6C'
  if (percentage < 80) return '#E6A23C'
  return '#67C23A'
}

const handleApproveBinding = async (row) => {
  try {
    await doctorAPI.approveBinding(row.id)
    ElMessage.success(`已通过患者 ${row.patientName} 的绑定申请`)
    row.status = BINDING_STATUS.APPROVED
  } catch (error) {
    console.error('批准绑定失败:', error)
    ElMessage.error('操作失败')
  }
}

const handleRejectBinding = async (row) => {
  try {
    await doctorAPI.rejectBinding(row.id)
    ElMessage.warning(`已拒绝患者 ${row.patientName} 的绑定申请`)
    row.status = BINDING_STATUS.REJECTED
  } catch (error) {
    console.error('拒绝绑定失败:', error)
    ElMessage.error('操作失败')
  }
}

const handleViewPatient = (row) => {
  router.push(`/doctor/patient/${row.id}`)
}

const sortedFollowupDates = computed(() => {
  return [...taskForm.followupDates].sort((a, b) => new Date(a) - new Date(b))
})

const handleCreateTask = (row) => {
  currentPatient.value = row
  // 重置表单
  Object.assign(taskForm, {
    title: '',
    content: '',
    followupType: 'single',
    singleDeadline: '',
    followupDates: [],
    types: [],
    numberFields: []
  })
  taskDialogVisible.value = true
}

const addQuickDate = (days) => {
  const targetDate = new Date(surgeryDate.value)
  targetDate.setDate(targetDate.getDate() + days)

  // 检查日期是否已存在
  const dateStr = targetDate.toISOString().split('T')[0]
  const exists = taskForm.followupDates.some(d => {
    const existingDateStr = new Date(d).toISOString().split('T')[0]
    return existingDateStr === dateStr
  })

  if (!exists) {
    taskForm.followupDates.push(targetDate)
  } else {
    ElMessage.warning('该日期已添加')
  }
}

const removeDate = (date) => {
  const index = taskForm.followupDates.findIndex(d => d.getTime() === date.getTime())
  if (index > -1) {
    taskForm.followupDates.splice(index, 1)
  }
}

const formatDate = (date) => {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const addNumberField = () => {
  if (!newNumberField.value.trim()) {
    ElMessage.warning('请输入数值项名称')
    return
  }

  if (taskForm.numberFields.includes(newNumberField.value.trim())) {
    ElMessage.warning('该数值项已存在')
    return
  }

  taskForm.numberFields.push(newNumberField.value.trim())
  newNumberField.value = ''
}

const removeNumberField = (index) => {
  taskForm.numberFields.splice(index, 1)
}

const handleSubmitTask = async () => {
  if (!taskForm.title) {
    ElMessage.warning('请输入任务标题')
    return
  }

  if (!taskForm.content) {
    ElMessage.warning('请输入任务内容')
    return
  }

  if (taskForm.types.length === 0) {
    ElMessage.warning('请至少选择一种任务类型')
    return
  }

  // 如果选择了数值填写，必须配置至少一个数值项
  if (taskForm.types.includes('number') && taskForm.numberFields.length === 0) {
    ElMessage.warning('请为数值填写添加至少一个数值项')
    return
  }

  try {
    // 构建任务类型数据，包含数值字段配置
    const taskTypesData = {
      types: taskForm.types,
      numberFields: taskForm.types.includes('number') ? taskForm.numberFields : []
    }

    if (taskForm.followupType === 'single') {
      if (!taskForm.singleDeadline) {
        ElMessage.warning('请选择截止时间')
        return
      }

      // 创建单次任务
      await doctorAPI.createTasks({
        doctor_id: JSON.parse(localStorage.getItem('userInfo')).profile_id,
        patient_id: currentPatient.value.id,
        title: taskForm.title,
        content: taskForm.content,
        task_types: taskTypesData,
        deadline: new Date(taskForm.singleDeadline).toISOString()
      })

      ElMessage.success('单次随访任务发布成功')
    } else {
      if (taskForm.followupDates.length === 0) {
        ElMessage.warning('请至少选择一个随访日期')
        return
      }

      // 创建多次任务
      for (const date of taskForm.followupDates) {
        await doctorAPI.createTasks({
          doctor_id: JSON.parse(localStorage.getItem('userInfo')).profile_id,
          patient_id: currentPatient.value.id,
          title: taskForm.title,
          content: taskForm.content,
          task_types: taskTypesData,
          deadline: new Date(date).toISOString()
        })
      }

      ElMessage.success(`已发布 ${taskForm.followupDates.length} 次随访任务`)
    }

    taskDialogVisible.value = false
  } catch (error) {
    console.error('发布任务失败:', error)
    ElMessage.error(typeof error === 'string' ? error : '发布任务失败')
  }
}

const handleViewFeedback = (row) => {
  ElMessage.info(`查看 ${row.patientName} 的任务反馈`)
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
