from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from doctors.models import Doctor
from patients.models import Patient
from bindings.models import Binding
from tasks.models import FollowupTask
from users.models import User
from .serializers import AdminDoctorSerializer, AdminPatientSerializer, AdminBindingSerializer


@api_view(['GET'])
def get_pending_doctors(request):
    """获取待审核的医生列表"""
    doctors = Doctor.objects.filter(audit_status='pending').order_by('-created_at')
    serializer = AdminDoctorSerializer(doctors, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def approve_doctor(request, doctor_id):
    """批准医生注册"""
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if doctor.audit_status != 'pending':
        return Response({'error': '该医生已审核'}, status=status.HTTP_400_BAD_REQUEST)

    doctor.audit_status = 'approved'
    doctor.save()

    return Response({'message': '医生审核通过'})


@api_view(['POST'])
def reject_doctor(request, doctor_id):
    """拒绝医生注册"""
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if doctor.audit_status != 'pending':
        return Response({'error': '该医生已审核'}, status=status.HTTP_400_BAD_REQUEST)

    doctor.audit_status = 'rejected'
    doctor.save()

    # 可选：禁用该用户账号
    doctor.user.is_active = False
    doctor.user.save()

    return Response({'message': '医生审核已拒绝'})


@api_view(['GET'])
def get_all_doctors(request):
    """获取所有医生列表"""
    doctors = Doctor.objects.all().order_by('-created_at')
    serializer = AdminDoctorSerializer(doctors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_all_patients(request):
    """获取所有患者列表"""
    patients = Patient.objects.all().order_by('-created_at')
    serializer = AdminPatientSerializer(patients, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_all_bindings(request):
    """获取所有医患绑定关系"""
    bindings = Binding.objects.all().order_by('-created_at')
    serializer = AdminBindingSerializer(bindings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_statistics(request):
    """获取系统统计数据"""
    stats = {
        'total_doctors': Doctor.objects.count(),
        'approved_doctors': Doctor.objects.filter(audit_status='approved').count(),
        'pending_doctors': Doctor.objects.filter(audit_status='pending').count(),
        'total_patients': Patient.objects.count(),
        'total_bindings': Binding.objects.count(),
        'approved_bindings': Binding.objects.filter(status='approved').count(),
        'pending_bindings': Binding.objects.filter(status='pending').count(),
        'total_tasks': FollowupTask.objects.count(),
        'completed_tasks': FollowupTask.objects.filter(status='completed').count(),
        'in_progress_tasks': FollowupTask.objects.filter(status='in_progress').count(),
    }

    return Response(stats)


@api_view(['POST'])
def toggle_user_status(request, user_id):
    """切换用户激活状态"""
    user = get_object_or_404(User, id=user_id)

    user.is_active = not user.is_active
    user.save()

    status_text = '激活' if user.is_active else '禁用'
    return Response({'message': f'用户已{status_text}'})


@api_view(['GET'])
def get_doctor_detail(request, doctor_id):
    """获取医生详细信息（管理员端）"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    serializer = AdminDoctorSerializer(doctor)
    return Response(serializer.data)


@api_view(['PUT'])
def update_doctor_info(request, doctor_id):
    """更新医生信息（管理员端）"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    serializer = AdminDoctorSerializer(doctor, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': '医生信息更新成功', 'data': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_patient_detail(request, patient_id):
    """获取患者详细信息（管理员端）"""
    patient = get_object_or_404(Patient, id=patient_id)
    serializer = AdminPatientSerializer(patient)
    return Response(serializer.data)


@api_view(['PUT'])
def update_patient_info(request, patient_id):
    """更新患者信息（管理员端）"""
    patient = get_object_or_404(Patient, id=patient_id)
    serializer = AdminPatientSerializer(patient, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': '患者信息更新成功', 'data': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_patient_submissions(request, patient_id):
    """获取患者的所有随访提交记录（管理员端）"""
    patient = get_object_or_404(Patient, id=patient_id)

    from tasks.models import TaskSubmission
    submissions = TaskSubmission.objects.filter(
        patient=patient
    ).select_related('task').order_by('-submitted_at')

    from tasks.serializers import TaskSubmissionSerializer
    serializer = TaskSubmissionSerializer(submissions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def unbind_relationship(request, binding_id):
    """解除医患绑定关系（管理员端）"""
    binding = get_object_or_404(Binding, id=binding_id)

    if binding.status != 'approved':
        return Response({'error': '只能解除已绑定的关系'}, status=status.HTTP_400_BAD_REQUEST)

    binding.status = 'unbound'
    binding.save()

    return Response({'message': '绑定关系已解除'})


@api_view(['POST'])
def reset_doctor_password(request, doctor_id):
    """重置医生密码（管理员端）"""
    new_password = request.data.get('new_password')

    if not new_password:
        return Response({'error': '请提供新密码'}, status=status.HTTP_400_BAD_REQUEST)

    if len(new_password) < 6:
        return Response({'error': '密码长度不能少于6位'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    user = doctor.user

    # 使用Django的set_password方法，会自动进行哈希加密
    user.set_password(new_password)
    user.save()

    return Response({'message': f'医生 {doctor.real_name} 的密码已重置'})


@api_view(['POST'])
def reset_patient_password(request, patient_id):
    """重置患者密码（管理员端）"""
    new_password = request.data.get('new_password')

    if not new_password:
        return Response({'error': '请提供新密码'}, status=status.HTTP_400_BAD_REQUEST)

    if len(new_password) < 6:
        return Response({'error': '密码长度不能少于6位'}, status=status.HTTP_400_BAD_REQUEST)

    patient = get_object_or_404(Patient, id=patient_id)
    user = patient.user

    # 使用Django的set_password方法，会自动进行哈希加密
    user.set_password(new_password)
    user.save()

    return Response({'message': f'患者 {patient.real_name} 的密码已重置'})
