from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_doctors, name='list_doctors'),
    path('info/', views.get_doctor_info, name='get_doctor_info'),
    path('patients/', views.get_doctor_patients, name='get_doctor_patients'),
    path('patients/<int:patient_id>/', views.get_patient_detail, name='get_patient_detail'),
    path('patients/<int:patient_id>/update/', views.update_patient_info, name='update_patient_info'),
    path('patients/<int:patient_id>/submissions/', views.get_patient_submissions, name='get_patient_submissions'),
    path('bindings/pending/', views.get_pending_bindings, name='get_pending_bindings'),
    path('bindings/<int:binding_id>/approve/', views.approve_binding, name='approve_binding'),
    path('bindings/<int:binding_id>/reject/', views.reject_binding, name='reject_binding'),
    path('tasks/create/', views.create_followup_tasks, name='create_followup_tasks'),
    path('tasks/', views.get_doctor_tasks, name='get_doctor_tasks'),
    path('tasks/<int:task_id>/', views.get_task_detail, name='get_task_detail'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
]
