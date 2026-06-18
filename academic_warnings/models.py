from django.db import models
from django.conf import settings
from students.models import SinhVien, HocKy


class CanhBaoHocVu(models.Model):
    MUC_CHOICES = [
        ('canh_bao', 'Cảnh báo học vụ'),
        ('buoc_thoi_hoc', 'Buộc thôi học'),
    ]
    TRANG_THAI_CHOICES = [
        ('chua_xu_ly', 'Chưa thông báo'),
        ('da_xu_ly', 'Đã thông báo'),
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
        ordering = ['trang_thai', '-ngay_tao']

    def __str__(self):
        return f"{self.sinh_vien.mssv} - {self.get_muc_canh_bao_display()} lần {self.so_lan_canh_bao} - {self.hoc_ky}"

    @property
    def mau_canh_bao(self):
        return {'canh_bao': 'warning', 'buoc_thoi_hoc': 'danger'}.get(self.muc_canh_bao, 'secondary')


class LichSuGuiEmailBaoCao(models.Model):
    lop = models.ForeignKey('students.Lop', on_delete=models.CASCADE, verbose_name='Lớp')
    hoc_ky = models.ForeignKey('students.HocKy', on_delete=models.CASCADE, verbose_name='Học kỳ báo cáo')
    ngay_gui = models.DateTimeField(auto_now_add=True, verbose_name='Ngày gửi')

    class Meta:
        verbose_name = 'Lịch sử gửi báo cáo lớp'
        verbose_name_plural = 'Lịch sử gửi báo cáo lớp'
        unique_together = ['lop', 'hoc_ky']

    def __str__(self):
        return f"Báo cáo {self.lop} - {self.hoc_ky} - Gửi ngày {self.ngay_gui.date()}"


class LichSuGuiCanhBaoSom(models.Model):
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name='lich_su_gui_canh_bao_som', verbose_name='Sinh viên')
    hoc_ky = models.ForeignKey(HocKy, on_delete=models.CASCADE, related_name='lich_su_gui_canh_bao_som', verbose_name='Học kỳ')
    ngay_gui = models.DateTimeField(auto_now_add=True, verbose_name='Ngày gửi')
    muc_nguy_co = models.CharField(max_length=50, verbose_name='Mức nguy cơ')
    gpa_he4 = models.FloatField(verbose_name='GPA tích lũy hệ 4')

    class Meta:
        verbose_name = 'Lịch sử gửi cảnh báo sớm'
        verbose_name_plural = 'Lịch sử gửi cảnh báo sớm'
        ordering = ['-ngay_gui']

    def __str__(self):
        return f"Cảnh báo sớm {self.sinh_vien.mssv} - Mức {self.muc_nguy_co} - Gửi ngày {self.ngay_gui.date()}"


