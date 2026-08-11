from rest_framework import serializers
from .models import Patient
from tasks.models import FollowupTask, TaskSubmission


class PatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'username', 'real_name', 'gender', 'age',
                  'surgery_type', 'surgery_date', 'phone', 'created_at']


class FollowupTaskSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.real_name', read_only=True)

    class Meta:
        model = FollowupTask
        fields = ['id', 'title', 'content', 'doctor', 'doctor_name', 'task_types',
                  'deadline', 'status', 'created_at']


class TaskSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSubmission
        fields = ['id', 'task', 'submission_data', 'images', 'notes', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']
