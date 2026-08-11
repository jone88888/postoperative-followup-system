from django.db import models
from users.models import User


class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    real_name = models.CharField('真实姓名', max_length=50)
    id_card = models.CharField('身份证号', max_length=18, unique=True, null=True, blank=True)
    gender = models.CharField('性别', max_length=10, choices=GENDER_CHOICES)
    age = models.IntegerField('年龄')
    surgery_type = models.CharField('手术类型', max_length=100)
    surgery_date = models.DateField('手术日期', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'patients'
        verbose_name = '患者'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.real_name} - {self.surgery_type}'

