import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue')
    },
    {
      path: '/patient',
      name: 'Patient',
      component: () => import('../views/patient/Dashboard.vue')
    },
    {
      path: '/doctor',
      name: 'Doctor',
      component: () => import('../views/doctor/Dashboard.vue')
    },
    {
      path: '/doctor/patient/:id',
      name: 'PatientDetail',
      component: () => import('../views/doctor/PatientDetail.vue')
    },
    {
      path: '/doctor/tasks',
      name: 'DoctorTasks',
      component: () => import('../views/doctor/TaskManagement.vue')
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('../views/admin/Dashboard.vue')
    },
    {
      path: '/admin/doctor/:id',
      name: 'AdminDoctorDetail',
      component: () => import('../views/admin/DoctorDetail.vue')
    },
    {
      path: '/admin/patient/:id',
      name: 'AdminPatientDetail',
      component: () => import('../views/admin/PatientDetail.vue')
    }
  ]
})

export default router
