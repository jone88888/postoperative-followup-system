from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Binding
from .serializers import BindingSerializer
from doctors.models import Doctor
from patients.models import Patient


@api_view(['GET'])
def get_doctor_bindings(request, doctor_id):
    """获取医生的患者绑定请求列表"""
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        bindings = Binding.objects.filter(doctor=doctor).select_related('patient', 'patient__user')
        serializer = BindingSerializer(bindings, many=True)
        return Response(serializer.data)
    except Doctor.DoesNotExist:
        return Response({'error': '医生不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def approve_binding(request, binding_id):
    """批准患者绑定请求"""
    try:
        binding = Binding.objects.get(id=binding_id)
        binding.status = 'approved'
        binding.approve_time = timezone.now()
        binding.save()
        return Response({'message': '已批准绑定'})
    except Binding.DoesNotExist:
        return Response({'error': '绑定记录不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def reject_binding(request, binding_id):
    """拒绝患者绑定请求"""
    try:
        binding = Binding.objects.get(id=binding_id)
        binding.status = 'rejected'
        binding.approve_time = timezone.now()
        binding.save()
        return Response({'message': '已拒绝绑定'})
    except Binding.DoesNotExist:
        return Response({'error': '绑定记录不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_all_bindings(request):
    """获取所有绑定记录（管理员使用）"""
    bindings = Binding.objects.all().select_related('doctor', 'patient', 'patient__user', 'doctor__user')
    serializer = BindingSerializer(bindings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_patient_bindings(request, patient_id):
    """获取患者的绑定记录"""
    try:
        patient = Patient.objects.get(id=patient_id)
        bindings = Binding.objects.filter(patient=patient).select_related('doctor', 'doctor__user').order_by('-apply_time')
        serializer = BindingSerializer(bindings, many=True)
        return Response(serializer.data)
    except Patient.DoesNotExist:
        return Response({'error': '患者不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_binding_request(request):
    """患者创建新的绑定请求"""
    patient_id = request.data.get('patient_id')
    doctor_id = request.data.get('doctor_id')

    if not patient_id or not doctor_id:
        return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        patient = Patient.objects.get(id=patient_id)
        doctor = Doctor.objects.get(id=doctor_id)

        # 检查是否已有待审核的绑定
        existing_pending = Binding.objects.filter(
            patient=patient,
            doctor=doctor,
            status='pending'
        ).exists()

        if existing_pending:
            return Response({'error': '您已向该医生发起过绑定申请，请等待审核'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查是否已有通过的绑定
        existing_approved = Binding.objects.filter(
            patient=patient,
            status='approved'
        ).exists()

        if existing_approved:
            return Response({'error': '您已有绑定的医生，如需更换请先解除当前绑定'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查是否之前被拒绝过，如果是则更新记录状态为pending
        try:
            old_binding = Binding.objects.get(patient=patient, doctor=doctor)
            if old_binding.status == 'rejected':
                old_binding.status = 'pending'
                old_binding.apply_time = timezone.now()
                old_binding.approve_time = None
                old_binding.save()
                return Response({
                    'message': '重新申请成功，请等待医生审核',
                    'binding': BindingSerializer(old_binding).data
                }, status=status.HTTP_201_CREATED)
        except Binding.DoesNotExist:
            pass

        # 创建新的绑定记录
        binding = Binding.objects.create(
            patient=patient,
            doctor=doctor,
            status='pending'
        )

        return Response({
            'message': '绑定申请已提交，请等待医生审核',
            'binding': BindingSerializer(binding).data
        }, status=status.HTTP_201_CREATED)

    except Patient.DoesNotExist:
        return Response({'error': '患者不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Doctor.DoesNotExist:
        return Response({'error': '医生不存在'}, status=status.HTTP_404_NOT_FOUND)
