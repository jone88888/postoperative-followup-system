from rest_framework import serializers
from .models import FollowupTask, TaskSubmission


class FollowupTaskSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.real_name', read_only=True)
    patient_name = serializers.CharField(source='patient.real_name', read_only=True)

    class Meta:
        model = FollowupTask
        fields = ['id', 'doctor', 'doctor_name', 'patient', 'patient_name',
                  'title', 'content', 'task_types', 'deadline', 'status', 'created_at']


class TaskSubmissionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.real_name', read_only=True)

    class Meta:
        model = TaskSubmission
        fields = ['id', 'task', 'patient', 'patient_name', 'submission_data',
                  'images', 'notes', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']
