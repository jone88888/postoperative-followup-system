from django.urls import path
from . import views

urlpatterns = [
    path('info/', views.get_patient_info, name='get_patient_info'),
    path('tasks/', views.get_patient_tasks, name='get_patient_tasks'),
    path('tasks/<int:task_id>/', views.get_patient_task_detail, name='get_patient_task_detail'),
    path('tasks/<int:task_id>/submit/', views.submit_task, name='submit_task'),
]
