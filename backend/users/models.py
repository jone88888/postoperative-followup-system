from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名不能为空')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('patient', '患者'),
        ('doctor', '医生'),
        ('admin', '管理员'),
    ]

    username = models.CharField('用户名', max_length=150, unique=True)
    phone = models.CharField('手机号', max_length=11)
    role = models.CharField('角色', max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField('是否激活', default=True)
    is_staff = models.BooleanField('是否员工', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

