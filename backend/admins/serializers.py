from rest_framework import serializers
from doctors.models import Doctor
from patients.models import Patient
from bindings.models import Binding
from tasks.models import FollowupTask


class AdminDoctorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user_id', 'username', 'phone', 'real_name', 'hospital', 'department',
                  'title', 'audit_status', 'is_active', 'created_at']


class AdminPatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user_id', 'username', 'phone', 'real_name', 'id_card', 'gender', 'age',
                  'surgery_type', 'surgery_date', 'is_active', 'created_at']


class AdminBindingSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.real_name', read_only=True)
    patient_name = serializers.CharField(source='patient.real_name', read_only=True)
    hospital = serializers.CharField(source='doctor.hospital', read_only=True)
    doctor_id = serializers.IntegerField(source='doctor.id', read_only=True)
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)

    class Meta:
        model = Binding
        fields = ['id', 'doctor_id', 'doctor_name', 'patient_id', 'patient_name',
                  'hospital', 'status', 'apply_time', 'approve_time']
