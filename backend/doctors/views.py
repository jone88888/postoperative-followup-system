from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Doctor
from patients.models import Patient
from bindings.models import Binding
from tasks.models import FollowupTask, TaskSubmission
from .serializers import (
    DoctorSerializer, PatientSerializer, BindingSerializer,
    CreateFollowupTaskSerializer, FollowupTaskSerializer
)


@api_view(['GET'])
def list_doctors(request):
    """获取所有已审核通过的医生列表（供患者注册时选择）"""
    doctors = Doctor.objects.filter(audit_status='approved')
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_doctor_info(request):
    """获取医生详细信息"""
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    serializer = DoctorSerializer(doctor)
    return Response(serializer.data)


@api_view(['GET'])
def get_doctor_patients(request):
    """获取医生的患者列表（已绑定的患者）"""
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    bindings = Binding.objects.filter(doctor=doctor, status='approved')
    patients = [binding.patient for binding in bindings]

    serializer = PatientSerializer(patients, many=True, context={'request': request, 'doctor': doctor})
    return Response(serializer.data)


@api_view(['GET'])
def get_pending_bindings(request):
    """获取待审核的医患绑定申请"""
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    bindings = Binding.objects.filter(doctor=doctor, status='pending').order_by('-created_at')

    serializer = BindingSerializer(bindings, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def approve_binding(request, binding_id):
    """批准医患绑定"""
    binding = get_object_or_404(Binding, id=binding_id)

    if binding.status != 'pending':
        return Response({'error': '该申请已处理'}, status=status.HTTP_400_BAD_REQUEST)

    binding.status = 'approved'
    binding.save()

    return Response({'message': '绑定已批准'})


@api_view(['POST'])
def reject_binding(request, binding_id):
    """拒绝医患绑定"""
    binding = get_object_or_404(Binding, id=binding_id)

    if binding.status != 'pending':
        return Response({'error': '该申请已处理'}, status=status.HTTP_400_BAD_REQUEST)

    binding.status = 'rejected'
    binding.save()

    return Response({'message': '绑定已拒绝'})


@api_view(['POST'])
def create_followup_tasks(request):
    """创建随访任务"""
    serializer = CreateFollowupTaskSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    doctor_id = request.data.get('doctor_id')

    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    patient = get_object_or_404(Patient, id=data['patient_id'])

    # 检查医患绑定关系
    try:
        binding = Binding.objects.get(doctor=doctor, patient=patient, status='approved')
    except Binding.DoesNotExist:
        return Response({'error': '该患者未与您绑定'}, status=status.HTTP_403_FORBIDDEN)

    # 创建任务
    task = FollowupTask.objects.create(
        doctor=doctor,
        patient=patient,
        title=data['title'],
        content=data['content'],
        task_types=data['task_types'],
        deadline=data['deadline'],
        status='in_progress'
    )

    serializer = FollowupTaskSerializer(task)
    return Response({
        'message': '任务创建成功',
        'task': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_doctor_tasks(request):
    """获取医生发布的所有任务"""
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    tasks = FollowupTask.objects.filter(doctor=doctor).select_related('patient').order_by('-created_at')

    serializer = FollowupTaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_task_detail(request, task_id):
    """获取任务详情（医生端）"""
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    task = get_object_or_404(FollowupTask, id=task_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # 验证任务属于该医生
    if task.doctor.id != doctor.id:
        return Response({'error': '无权访问此任务'}, status=status.HTTP_403_FORBIDDEN)

    serializer = FollowupTaskSerializer(task)
    task_data = serializer.data

    # ���取任���的提交���录
    from tasks.serializers import TaskSubmissionSerializer
    submissions = TaskSubmission.objects.filter(task=task).order_by('-submitted_at')
    submissions_data = TaskSubmissionSerializer(submissions, many=True).data
    task_data['submissions'] = submissions_data

    return Response(task_data)


@api_view(['PUT'])
def update_task(request, task_id):
    """更新任务信息（医生端）"""
    doctor_id = request.data.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    task = get_object_or_404(FollowupTask, id=task_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # 验证任务属于该医生
    if task.doctor.id != doctor.id:
        return Response({'error': '无权修改此任务'}, status=status.HTTP_403_FORBIDDEN)

    # 不允许修改已完成的任务
    if task.status == 'completed':
        return Response({'error': '已完成的任务不能修改'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = FollowupTaskSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': '任务更新成功', 'data': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_task(request, task_id):
    """删除任务（医生端）"""
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    task = get_object_or_404(FollowupTask, id=task_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # 验证任务属于该医生
    if task.doctor.id != doctor.id:
        return Response({'error': '无权删除此任务'}, status=status.HTTP_403_FORBIDDEN)

    task.delete()
    return Response({'message': '任务删除成功'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_patient_detail(request, patient_id):
    """获取患者详细信息（医生端）"""
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    patient = get_object_or_404(Patient, id=patient_id)

    # 验证医患绑定关系
    try:
        Binding.objects.get(doctor=doctor, patient=patient, status='approved')
    except Binding.DoesNotExist:
        return Response({'error': '您没有权限查看该患者信息'}, status=status.HTTP_403_FORBIDDEN)

    serializer = PatientSerializer(patient)
    return Response(serializer.data)


@api_view(['PUT'])
def update_patient_info(request, patient_id):
    """更新患者信息（医生端）"""
    doctor_id = request.data.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    patient = get_object_or_404(Patient, id=patient_id)

    # 验证医患绑定关系
    try:
        Binding.objects.get(doctor=doctor, patient=patient, status='approved')
    except Binding.DoesNotExist:
        return Response({'error': '您没有权限修改该患者信息'}, status=status.HTTP_403_FORBIDDEN)

    # 更新患者信息
    serializer = PatientSerializer(patient, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': '患者信息更新成功', 'data': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_patient_submissions(request, patient_id):
    """获取患者的所有随访提交记录"""
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return Response({'error': '缺少医生ID'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    patient = get_object_or_404(Patient, id=patient_id)

    # 验证医患绑定关系
    try:
        Binding.objects.get(doctor=doctor, patient=patient, status='approved')
    except Binding.DoesNotExist:
        return Response({'error': '您没有权限查看该患者的随访记录'}, status=status.HTTP_403_FORBIDDEN)

    # 获取该患者所有的任务提交记录
    from tasks.models import TaskSubmission
    submissions = TaskSubmission.objects.filter(
        patient=patient,
        task__doctor=doctor
    ).select_related('task').order_by('-submitted_at')

    from tasks.serializers import TaskSubmissionSerializer
    serializer = TaskSubmissionSerializer(submissions, many=True)
    return Response(serializer.data)
