from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from doctors.models import Doctor
from patients.models import Patient
from bindings.models import Binding


@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # 创建用户
    user = User.objects.create_user(
        username=data['username'],
        password=data['password'],
        phone=data['phone'],
        role=data['role']
    )

    # 根据角色创建对应的profile
    if data['role'] == 'patient':
        patient = Patient.objects.create(
            user=user,
            real_name=data['real_name'],
            id_card=data['id_card'],
            gender=data['gender'],
            age=data['age'],
            surgery_type=data['surgery_type'],
            surgery_date=timezone.now().date()
        )

        # 创建医患绑定申请
        try:
            doctor = Doctor.objects.get(id=data['doctor_id'])
            Binding.objects.create(
                doctor=doctor,
                patient=patient,
                status='pending'
            )
        except Doctor.DoesNotExist:
            pass

    elif data['role'] == 'doctor':
        Doctor.objects.create(
            user=user,
            real_name=data['real_name'],
            hospital=data['hospital'],
            department=data['department'],
            title=data['title'],
            audit_status='pending'
        )

    return Response({
        'message': '注册成功',
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    role = serializer.validated_data['role']

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.role != role:
        return Response({'error': '角色不匹配'}, status=status.HTTP_403_FORBIDDEN)

    if not user.is_active:
        return Response({'error': '账号未激活'}, status=status.HTTP_403_FORBIDDEN)

    # 检查医生审核状态
    if role == 'doctor':
        try:
            doctor = user.doctor_profile
            if doctor.audit_status != 'approved':
                return Response({'error': '医生账号待审核'}, status=status.HTTP_403_FORBIDDEN)
        except Doctor.DoesNotExist:
            return Response({'error': '医生信息不存在'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'message': '登录成功',
        'user': UserSerializer(user).data
    })


@api_view(['GET'])
def get_current_user(request):
    # 简化版本，实际应该使用JWT认证
    return Response(UserSerializer(request.user).data)

