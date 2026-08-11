# 术后随访联网管理系统 - 后端数据库设计

## 数据表结构

### 1. 用户表 (User)
```python
- id: 主键
- username: 用户名（唯一）
- password: 密码（哈希存储）
- phone: 手机号
- role: 角色（patient/doctor/admin）
- is_active: 是否激活
- created_at: 创建时间
- updated_at: 更新时间
```

### 2. 医生信息表 (Doctor)
```python
- id: 主键
- user: 外键关联User
- real_name: 真实姓名
- hospital: 医院
- department: 科室
- title: 职称（chief/associate_chief/attending/resident）
- audit_status: 审核状态（pending/approved/rejected）
- created_at: 创建时间
```

### 3. 患者信息表 (Patient)
```python
- id: 主键
- user: 外键关联User
- real_name: 真实姓名
- gender: 性别
- age: 年龄
- surgery_type: 手术类型
- surgery_date: 手术日期
- created_at: 创建时间
```

### 4. 医患绑定表 (Binding)
```python
- id: 主键
- doctor: 外键关联Doctor
- patient: 外键关联Patient
- status: 绑定状态（pending/approved/rejected/unbound）
- apply_time: 申请时间
- approve_time: 审核时间
```

### 5. 随访任务表 (FollowupTask)
```python
- id: 主键
- doctor: 外键关联Doctor
- patient: 外键关联Patient
- title: 任务标题
- content: 任务内容
- task_types: 任务类型（JSON: text/image/number）
- deadline: 截止时间
- status: 任务状态（not_started/in_progress/completed）
- created_at: 创建时间
```

### 6. 任务提交表 (TaskSubmission)
```python
- id: 主键
- task: 外键关联FollowupTask
- patient: 外键关联Patient
- content: 提交内容
- images: 图片附件（JSON数组）
- submitted_at: 提交时间
```

### 7. 通知表 (Notification)
```python
- id: 主键
- receiver: 外键关联User
- title: 通知标题
- content: 通知内容
- is_read: 是否已读
- created_at: 创建时间
```

## API接口设计

### 认证相关
- POST /api/auth/register/ - 用户注册
- POST /api/auth/login/ - 用户登录
- POST /api/auth/logout/ - 用户退出
- GET /api/auth/user/ - 获取当前用户信息

### 医生相关
- GET /api/doctors/ - 获取医生列表
- GET /api/doctors/{id}/ - 获取医生详情
- GET /api/doctors/patients/ - 医生查看自己的患者列表
- POST /api/doctors/tasks/ - 医生发布任务

### 患者相关
- GET /api/patients/tasks/ - 患者查看任务列表
- POST /api/patients/tasks/{id}/submit/ - 患者提交任务

### 医患绑定相关
- POST /api/bindings/ - 创建绑定申请
- GET /api/bindings/pending/ - 获取待审核绑定列表
- POST /api/bindings/{id}/approve/ - 医生通过绑定
- POST /api/bindings/{id}/reject/ - 医生拒绝绑定

### 管理员相关
- GET /api/admin/doctors/pending/ - 获取待审核医生列表
- POST /api/admin/doctors/{id}/approve/ - 审核通过医生
- POST /api/admin/doctors/{id}/reject/ - 拒绝医生注册
- GET /api/admin/statistics/ - 获取系统统计数据
