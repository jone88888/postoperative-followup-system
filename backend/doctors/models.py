from django.db import models
from users.models import User


class Doctor(models.Model):
    TITLE_CHOICES = [
        ('chief', '主任医师'),
        ('associate_chief', '副主任医师'),
        ('attending', '主治医师'),
        ('resident', '住院医师'),
    ]

    AUDIT_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    real_name = models.CharField('真实姓名', max_length=50)
    hospital = models.CharField('医院', max_length=100)
    department = models.CharField('科室', max_length=50)
    title = models.CharField('职称', max_length=20, choices=TITLE_CHOICES)
    audit_status = models.CharField('审核状态', max_length=10, choices=AUDIT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'doctors'
        verbose_name = '医生'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.real_name} - {self.hospital}'

