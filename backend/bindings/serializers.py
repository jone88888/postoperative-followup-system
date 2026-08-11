from rest_framework import serializers
from .models import Binding
from patients.models import Patient
from doctors.models import Doctor


class BindingSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)
    patient_name = serializers.CharField(source='patient.real_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.user.phone', read_only=True)
    surgery_type = serializers.CharField(source='patient.surgery_type', read_only=True)
    doctor_id = serializers.IntegerField(source='doctor.id', read_only=True)
    doctor_name = serializers.CharField(source='doctor.real_name', read_only=True)
    hospital = serializers.CharField(source='doctor.hospital', read_only=True)

    class Meta:
        model = Binding
        fields = [
            'id', 'patient_id', 'patient_name', 'patient_phone', 'surgery_type',
            'doctor_id', 'doctor_name', 'hospital', 'status', 'apply_time', 'approve_time'
        ]
