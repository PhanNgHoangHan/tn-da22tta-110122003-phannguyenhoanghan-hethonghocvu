from django.db import models
from django.conf import settings
from students.models import SinhVien, HocKy


class CanhBaoHocVu(models.Model):
    MUC_CHOICES = [
        ('canh_bao', 'Cảnh báo học vụ'),
        ('buoc_thoi_hoc', 'Buộc thôi học'),
    ]
    TRANG_THAI_CHOICES = [
        ('chua_xu_ly', 'Chưa xử lý'),
        ('da_xu_ly', 'Đã xử lý'),
    ]
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE,
                                   related_name='canh_bao', verbose_name='Sinh viên')
    hoc_ky = models.ForeignKey(HocKy, on_delete=models.CASCADE,
                                related_name='canh_bao', verbose_name='Học kỳ')
    muc_canh_bao = models.CharField(max_length=20, choices=MUC_CHOICES, verbose_name='Mức cảnh báo')
    ly_do = models.TextField(verbose_name='Lý do cảnh báo')
    so_lan_canh_bao = models.PositiveSmallIntegerField(default=1, verbose_name='Lần cảnh báo thứ')
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES,
                                   default='chua_xu_ly', verbose_name='Trạng thái')
    ghi_chu = models.TextField(blank=True, verbose_name='Ghi chú xử lý')
    da_an = models.BooleanField(default=False, verbose_name='Đã ẩn khỏi danh sách')
    nguoi_dung_an = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='canh_bao_da_an',
        verbose_name='Người dùng đã ẩn'
    )

    class Meta:
        verbose_name = 'Cảnh báo học vụ'
        verbose_name_plural = 'Cảnh báo học vụ'
        unique_together = ['sinh_vien', 'hoc_ky']
        ordering = ['-ngay_tao']

    def __str__(self):
        return f"{self.sinh_vien.mssv} - {self.get_muc_canh_bao_display()} lần {self.so_lan_canh_bao} - {self.hoc_ky}"

    @property
    def mau_canh_bao(self):
        return {'canh_bao': 'warning', 'buoc_thoi_hoc': 'danger'}.get(self.muc_canh_bao, 'secondary')
