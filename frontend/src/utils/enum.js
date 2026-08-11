// 用户角色枚举
export const USER_ROLES = {
  PATIENT: 'patient',
  DOCTOR: 'doctor',
  ADMIN: 'admin'
}

// 任务状态枚举
export const TASK_STATUS = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed'
}

export const TASK_STATUS_TEXT = {
  [TASK_STATUS.NOT_STARTED]: '未开始',
  [TASK_STATUS.IN_PROGRESS]: '待完成',
  [TASK_STATUS.COMPLETED]: '已完成'
}

export const TASK_STATUS_TYPE = {
  [TASK_STATUS.NOT_STARTED]: 'info',
  [TASK_STATUS.IN_PROGRESS]: 'warning',
  [TASK_STATUS.COMPLETED]: 'success'
}

// 绑定状态枚举
export const BINDING_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  UNBOUND: 'unbound'
}

export const BINDING_STATUS_TEXT = {
  [BINDING_STATUS.PENDING]: '待确认',
  [BINDING_STATUS.APPROVED]: '已绑定',
  [BINDING_STATUS.REJECTED]: '已拒绝',
  [BINDING_STATUS.UNBOUND]: '已解除'
}

export const BINDING_STATUS_TYPE = {
  [BINDING_STATUS.PENDING]: 'warning',
  [BINDING_STATUS.APPROVED]: 'success',
  [BINDING_STATUS.REJECTED]: 'danger',
  [BINDING_STATUS.UNBOUND]: 'info'
}

// 医生审核状态
export const DOCTOR_AUDIT_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected'
}

export const DOCTOR_AUDIT_STATUS_TEXT = {
  [DOCTOR_AUDIT_STATUS.PENDING]: '待审核',
  [DOCTOR_AUDIT_STATUS.APPROVED]: '已通过',
  [DOCTOR_AUDIT_STATUS.REJECTED]: '已拒绝'
}

export const DOCTOR_AUDIT_STATUS_TYPE = {
  [DOCTOR_AUDIT_STATUS.PENDING]: 'warning',
  [DOCTOR_AUDIT_STATUS.APPROVED]: 'success',
  [DOCTOR_AUDIT_STATUS.REJECTED]: 'danger'
}
