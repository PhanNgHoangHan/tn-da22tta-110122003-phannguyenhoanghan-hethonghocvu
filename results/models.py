from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import SinhVien, MonHoc, HocKy


class KetQuaHocTap(models.Model):
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE,
                                   related_name='ket_qua', verbose_name='Sinh viên')
    mon_hoc = models.ForeignKey(MonHoc, on_delete=models.CASCADE,
                                 related_name='ket_qua', verbose_name='Môn học')
    hoc_ky = models.ForeignKey(HocKy, on_delete=models.CASCADE,
                                related_name='ket_qua', verbose_name='Học kỳ')
    # ĐTBQT: Điểm trung bình quá trình
    diem_qt = models.FloatField(null=True, blank=True,
                                 validators=[MinValueValidator(0), MaxValueValidator(10)],
                                 verbose_name='Điểm QT (ĐTBQT)')
    # ĐKT: Điểm đánh giá kết thúc
    diem_thi = models.FloatField(null=True, blank=True,
                                  validators=[MinValueValidator(0), MaxValueValidator(10)],
                                  verbose_name='Điểm thi (ĐKT)')
    # ĐTgK = (ĐTBQT + ĐKT) / 2
    diem_tk = models.FloatField(null=True, blank=True,
                                 validators=[MinValueValidator(0), MaxValueValidator(10)],
                                 verbose_name='Điểm tổng kết (ĐTgK)')
    lan_hoc = models.PositiveSmallIntegerField(default=1, verbose_name='Lần học')
    ghi_chu = models.CharField(max_length=200, blank=True, verbose_name='Ghi chú')

    class Meta:
        verbose_name = 'Kết quả học tập'
        verbose_name_plural = 'Kết quả học tập'
        unique_together = ['sinh_vien', 'mon_hoc', 'hoc_ky', 'lan_hoc']
        ordering = ['-hoc_ky__nam_hoc', '-hoc_ky__ky']

    def __str__(self):
        return f"{self.sinh_vien.mssv} - {self.mon_hoc.ma_mh} - {self.hoc_ky}"

    def save(self, *args, **kwargs):
        # Công thức: ĐTgK = (ĐTBQT + ĐKT) / 2
        if self.diem_qt is not None and self.diem_thi is not None and self.diem_tk is None:
            self.diem_tk = round((self.diem_qt + self.diem_thi) / 2, 2)
        super().save(*args, **kwargs)

    @property
    def diem_chu(self):
        """
        Thang điểm chữ theo bảng quy chế TVU:
          A  : 9.0 - 10.0  (4.0)
          B+ : 8.0 -  8.9  (3.5)
          B  : 7.0 -  7.9  (3.0)
          C+ : 6.5 -  6.9  (2.5)
          C  : 5.5 -  6.4  (2.0)
          D+ : 5.0 -  5.4  (1.5)
          D  : 4.0 -  4.9  (1.0)
          F  : < 4.0        (0.0)
        """
        if self.diem_tk is None:
            return None
        d = self.diem_tk
        if d >= 9.0: return 'A'
        if d >= 8.0: return 'B+'
        if d >= 7.0: return 'B'
        if d >= 6.5: return 'C+'
        if d >= 5.5: return 'C'
        if d >= 5.0: return 'D+'
        if d >= 4.0: return 'D'
        return 'F'

    @property
    def diem_he4(self):
        """Điểm hệ 4 tương ứng."""
        if self.diem_tk is None:
            return None
        d = self.diem_tk
        if d >= 9.0: return 4.0
        if d >= 8.0: return 3.5
        if d >= 7.0: return 3.0
        if d >= 6.5: return 2.5
        if d >= 5.5: return 2.0
        if d >= 5.0: return 1.5
        if d >= 4.0: return 1.0
        return 0.0

    @property
    def xep_loai(self):
        """Xếp loại học lực."""
        return {
            'A': 'Xuất sắc', 'B+': 'Giỏi', 'B': 'Khá',
            'C+': 'Trung bình khá', 'C': 'Trung bình',
            'D+': 'Trung bình yếu', 'D': 'Yếu',
            'F': 'Kém'
        }.get(self.diem_chu, '')

    @property
    def dat(self):
        """Học phần đạt khi điểm >= 4.0 (từ D trở lên)."""
        return self.diem_tk is not None and self.diem_tk >= 4.0
