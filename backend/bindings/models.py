from django.db import models
from doctors.models import Doctor
from patients.models import Patient


class Binding(models.Model):
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('approved', '已绑定'),
        ('rejected', '已拒绝'),
        ('unbound', '已解除'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bindings')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bindings')
    status = models.CharField('绑定状态', max_length=10, choices=STATUS_CHOICES, default='pending')
    apply_time = models.DateTimeField('申请时间', auto_now_add=True)
    approve_time = models.DateTimeField('审核时间', null=True, blank=True)

    class Meta:
        db_table = 'bindings'
        verbose_name = '医患绑定'
        verbose_name_plural = verbose_name
        unique_together = ['doctor', 'patient']

    def __str__(self):
        return f'{self.patient.real_name} - {self.doctor.real_name}'

