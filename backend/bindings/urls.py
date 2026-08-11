from django.urls import path
from . import views

urlpatterns = [
    path('doctor/<int:doctor_id>/', views.get_doctor_bindings, name='doctor_bindings'),
    path('patient/<int:patient_id>/', views.get_patient_bindings, name='patient_bindings'),
    path('create/', views.create_binding_request, name='create_binding_request'),
    path('<int:binding_id>/approve/', views.approve_binding, name='approve_binding'),
    path('<int:binding_id>/reject/', views.reject_binding, name='reject_binding'),
    path('all/', views.get_all_bindings, name='all_bindings'),
]
