<template>
  <div class="binding-management">
    <el-card v-loading="loading">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>医患绑定管理</span>
          <el-button
            v-if="canRequestBinding"
            type="primary"
            @click="showDoctorSelection = true"
          >
            申请绑定医生
          </el-button>
        </div>
      </template>

      <el-alert
        v-if="currentBinding"
        :title="`当前绑定医生：${currentBinding.doctor_name}（${currentBinding.hospital}）`"
        type="success"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-alert
        v-else-if="hasRejectedBinding"
        title="您的绑定申请已被拒绝，可以重新选择医生申请绑定"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-table :data="bindings" style="width: 100%">
        <el-table-column prop="doctor_name" label="医生姓名" />
        <el-table-column prop="hospital" label="医院" />
        <el-table-column prop="apply_time" label="申请时间">
          <template #default="{ row }">
            {{ formatDateTime(row.apply_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approve_time" label="审核时间">
          <template #default="{ row }">
            {{ row.approve_time ? formatDateTime(row.approve_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'rejected'"
              link
              type="primary"
              size="small"
              @click="handleReapply(row)"
            >
              重新申请
            </el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 选择医生对话框 -->
    <el-dialog v-model="showDoctorSelection" title="选择要绑定的医生" width="800px">
      <el-input
        v-model="doctorSearch"
        placeholder="搜索医生姓名或医院"
        style="margin-bottom: 15px"
        clearable
      />
      <el-table
        :data="filteredDoctors"
        style="width: 100%"
        @row-click="handleSelectDoctor"
        highlight-current-row
      >
        <el-table-column prop="real_name" label="医生姓名" />
        <el-table-column prop="hospital" label="医院" />
        <el-table-column prop="department" label="科室" />
        <el-table-column prop="title" label="职称">
          <template #default="{ row }">
            {{ getTitleText(row.title) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleSelectDoctor(row)">
              选择
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { doctorAPI, patientAPI } from '@/api'

const props = defineProps({
  patientId: {
    type: Number,
    required: true
  }
})

const loading = ref(false)
const bindings = ref([])
const doctors = ref([])
const showDoctorSelection = ref(false)
const doctorSearch = ref('')

const statusMap = {
  pending: { text: '待审核', type: 'warning' },
  approved: { text: '已绑定', type: 'success' },
  rejected: { text: '已拒绝', type: 'danger' },
  unbound: { text: '已解除', type: 'info' }
}

const titleMap = {
  chief: '主任医师',
  associate_chief: '副主任医师',
  attending: '主治医师',
  resident: '住院医师'
}

const currentBinding = computed(() => {
  return bindings.value.find(b => b.status === 'approved')
})

const hasRejectedBinding = computed(() => {
  return bindings.value.some(b => b.status === 'rejected')
})

const canRequestBinding = computed(() => {
  return !currentBinding.value && !bindings.value.some(b => b.status === 'pending')
})

const filteredDoctors = computed(() => {
  if (!doctorSearch.value) return doctors.value
  return doctors.value.filter(
    d =>
      d.real_name.includes(doctorSearch.value) ||
      d.hospital.includes(doctorSearch.value)
  )
})

onMounted(async () => {
  await loadBindings()
  await loadDoctors()
})

const loadBindings = async () => {
  loading.value = true
  try {
    const data = await patientAPI.getBindings(props.patientId)
    bindings.value = data
  } catch (error) {
    console.error('获取绑定记录失败:', error)
    ElMessage.error('获取绑定记录失败')
  } finally {
    loading.value = false
  }
}

const loadDoctors = async () => {
  try {
    const data = await doctorAPI.list()
    console.log('获取到的医生列表:', data)
    doctors.value = data
    console.log('已设置doctors.value:', doctors.value)
  } catch (error) {
    console.error('获取医生列表失败:', error)
    ElMessage.error('获取医生列表失败')
  }
}

const handleSelectDoctor = async (doctor) => {
  try {
    await ElMessageBox.confirm(
      `确定要向 ${doctor.real_name} 医生（${doctor.hospital}）发起绑定申请吗？`,
      '确认绑定',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    await patientAPI.createBinding({
      patient_id: props.patientId,
      doctor_id: doctor.id
    })

    ElMessage.success('绑定申请已提交，请等待医生审核')
    showDoctorSelection.value = false
    await loadBindings()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('申请绑定失败:', error)
      ElMessage.error(typeof error === 'string' ? error : '申请绑定失败')
    }
  }
}

const handleReapply = async (binding) => {
  try {
    await ElMessageBox.confirm(
      `确定要向 ${binding.doctor_name} 医生重新发起绑定申请吗？`,
      '重新申请',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    // 获取医生ID（需要从医生列表中查找）
    const doctor = doctors.value.find(d => d.real_name === binding.doctor_name)
    if (!doctor) {
      ElMessage.error('找不到该医生信息')
      return
    }

    await patientAPI.createBinding({
      patient_id: props.patientId,
      doctor_id: doctor.id
    })

    ElMessage.success('重新申请成功，请等待医生审核')
    await loadBindings()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重新申请失败:', error)
      ElMessage.error(typeof error === 'string' ? error : '重新申请失败')
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

const getTitleText = (title) => {
  return titleMap[title] || title
}
</script>

<style scoped>
.binding-management {
  width: 100%;
}

.el-table {
  cursor: default;
}

.el-table :deep(.el-table__row) {
  cursor: pointer;
}
</style>
