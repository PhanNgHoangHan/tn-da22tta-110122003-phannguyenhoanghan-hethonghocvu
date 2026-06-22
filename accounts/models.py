from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Quản trị viên'),
        ('giaovu', 'Giáo vụ'),
        ('covan', 'Cố vấn học tập'),
        ('sinhvien', 'Sinh viên'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sinhvien', verbose_name='Vai trò')
    full_name = models.CharField(max_length=200, blank=True, verbose_name='Họ và tên')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Số điện thoại')

    class Meta:
        db_table = 'customuser'
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return f"{self.full_name or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_giaovu(self):
        return self.role == 'giaovu'

    @property
    def is_covan(self):
        return self.role == 'covan'

    @property
    def is_sinhvien(self):
        return self.role == 'sinhvien'
