from rest_framework import serializers
from .models import User
from doctors.models import Doctor
from patients.models import Patient


class UserSerializer(serializers.ModelSerializer):
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'role', 'is_active', 'created_at', 'profile_id']
        read_only_fields = ['id', 'created_at']

    def get_profile_id(self, obj):
        """根据角色返回对应的profile ID"""
        if obj.role == 'patient':
            try:
                return obj.patient_profile.id
            except:
                return None
        elif obj.role == 'doctor':
            try:
                return obj.doctor_profile.id
            except:
                return None
        return None


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    phone = serializers.CharField(max_length=11)
    role = serializers.ChoiceField(choices=['patient', 'doctor'])

    # 患者专属字段
    real_name = serializers.CharField(max_length=50, required=False)
    id_card = serializers.CharField(max_length=18, required=False)
    gender = serializers.ChoiceField(choices=['male', 'female'], required=False)
    age = serializers.IntegerField(required=False)
    surgery_type = serializers.CharField(max_length=100, required=False)
    doctor_id = serializers.IntegerField(required=False)

    # 医生专属字段
    hospital = serializers.CharField(max_length=100, required=False)
    department = serializers.CharField(max_length=50, required=False)
    title = serializers.ChoiceField(
        choices=['chief', 'associate_chief', 'attending', 'resident'],
        required=False
    )

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': '用户名已存在'})

        role = data.get('role')
        if role == 'patient':
            required_fields = ['real_name', 'id_card', 'gender', 'age', 'surgery_type', 'doctor_id']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: '患者注册需要此字段'})

            # 检查身份证号是否已存在
            from patients.models import Patient
            if Patient.objects.filter(id_card=data.get('id_card')).exists():
                raise serializers.ValidationError({'id_card': '身份证号已被注册'})
        elif role == 'doctor':
            required_fields = ['real_name', 'hospital', 'department', 'title']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: '医生注册需要此字段'})

        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['patient', 'doctor', 'admin'])
