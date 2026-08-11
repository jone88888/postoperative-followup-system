from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Patient
from tasks.models import FollowupTask, TaskSubmission
from .serializers import FollowupTaskSerializer, TaskSubmissionSerializer, PatientSerializer
from django.utils import timezone


@api_view(['GET'])
def get_patient_info(request):
    """获取患者详细信息"""
    patient_id = request.GET.get('patient_id')
    if not patient_id:
        return Response({'error': '缺少患者ID'}, status=status.HTTP_400_BAD_REQUEST)

    patient = get_object_or_404(Patient, id=patient_id)
    serializer = PatientSerializer(patient)
    return Response(serializer.data)


@api_view(['GET'])
def get_patient_tasks(request):
    """获取患者的随访任务列表"""
    patient_id = request.GET.get('patient_id')
    if not patient_id:
        return Response({'error': '缺少患者ID'}, status=status.HTTP_400_BAD_REQUEST)

    patient = get_object_or_404(Patient, id=patient_id)
    tasks = FollowupTask.objects.filter(patient=patient).order_by('deadline')

    # 更新任务状态
    today = timezone.now().date()
    for task in tasks:
        if task.status == 'not_started' and task.deadline.date() <= today:
            task.status = 'in_progress'
            task.save()

    serializer = FollowupTaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_patient_task_detail(request, task_id):
    """获取任务详情���患者���）"""
    patient_id = request.GET.get('patient_id')
    if not patient_id:
        return Response({'error': '���少患者ID'}, status=status.HTTP_400_BAD_REQUEST)

    task = get_object_or_404(FollowupTask, id=task_id)
    patient = get_object_or_404(Patient, id=patient_id)

    # 验证任���属于该患者
    if task.patient.id != patient.id:
        return Response({'error': '无权访问此任���'}, status=status.HTTP_403_FORBIDDEN)

    serializer = FollowupTaskSerializer(task)
    task_data = serializer.data

    # ���取任务的提交记录
    from tasks.serializers import TaskSubmissionSerializer
    submissions = TaskSubmission.objects.filter(task=task).order_by('-submitted_at')
    submissions_data = TaskSubmissionSerializer(submissions, many=True).data
    task_data['submissions'] = submissions_data

    return Response(task_data)


@api_view(['POST'])
def submit_task(request, task_id):
    """提交任务完成"""
    task = get_object_or_404(FollowupTask, id=task_id)

    if task.status == 'completed':
        return Response({'error': '任务已完成'}, status=status.HTTP_400_BAD_REQUEST)

    # 创建任务提交记录
    submission_data = {}
    if 'text_response' in request.data:
        submission_data['text_response'] = request.data['text_response']
    if 'number_values' in request.data:
        submission_data['number_values'] = request.data['number_values']
    if 'image_urls' in request.data:
        submission_data['image_urls'] = request.data['image_urls']
    images = request.data.get('images', [])
    notes = request.data.get('notes', '')

    submission = TaskSubmission.objects.create(
        task=task,
        patient=task.patient,
        submission_data=submission_data,
        images=images,
        notes=notes
    )

    # 更新任务状态为已完成
    task.status = 'completed'
    task.save()

    return Response({
        'message': '任务提交成功',
        'submission': TaskSubmissionSerializer(submission).data
    }, status=status.HTTP_201_CREATED)
