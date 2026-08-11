from django.urls import path
from . import views

urlpatterns = [
    path('doctors/pending/', views.get_pending_doctors, name='get_pending_doctors'),
    path('doctors/<int:doctor_id>/approve/', views.approve_doctor, name='approve_doctor'),
    path('doctors/<int:doctor_id>/reject/', views.reject_doctor, name='reject_doctor'),
    path('doctors/<int:doctor_id>/', views.get_doctor_detail, name='get_doctor_detail'),
    path('doctors/<int:doctor_id>/update/', views.update_doctor_info, name='update_doctor_info'),
    path('doctors/<int:doctor_id>/reset-password/', views.reset_doctor_password, name='reset_doctor_password'),
    path('doctors/', views.get_all_doctors, name='get_all_doctors'),
    path('patients/<int:patient_id>/', views.get_patient_detail, name='get_patient_detail'),
    path('patients/<int:patient_id>/update/', views.update_patient_info, name='update_patient_info'),
    path('patients/<int:patient_id>/reset-password/', views.reset_patient_password, name='reset_patient_password'),
    path('patients/<int:patient_id>/submissions/', views.get_patient_submissions, name='get_patient_submissions'),
    path('patients/', views.get_all_patients, name='get_all_patients'),
    path('bindings/', views.get_all_bindings, name='get_all_bindings'),
    path('bindings/<int:binding_id>/unbind/', views.unbind_relationship, name='unbind_relationship'),
    path('statistics/', views.get_statistics, name='get_statistics'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
]
