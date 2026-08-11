from django.db import models
from doctors.models import Doctor
from patients.models import Patient


class FollowupTask(models.Model):
    STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('in_progress', '待完成'),
        ('completed', '已完成'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='tasks')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField('任务标���', max_length=200)
    content = models.TextField('任���内���')
    task_types = models.JSONField('任务类型', default=list)
    deadline = models.DateTimeField('截止时���')
    status = models.CharField('任务���态', max_length=15, choices=STATUS_CHOICES, default='not_started')
    created_at = models.DateTimeField('创建时���', auto_now_add=True)

    class Meta:
        db_table = 'followup_tasks'
        verbose_name = '随���任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.patient.real_name}'


class TaskSubmission(models.Model):
    task = models.ForeignKey(FollowupTask, on_delete=models.CASCADE, related_name='submissions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    submission_data = models.JSONField('���交数据', default=dict, blank=True)
    images = models.JSONField('图片���件', default=list, blank=True)
    notes = models.TextField('备注���明', blank=True, default='')
    submitted_at = models.DateTimeField('���交���间', auto_now_add=True)

    class Meta:
        db_table = 'task_submissions'
        verbose_name = '任务提交'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.task.title} - 提���'
