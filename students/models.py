from django.db import models
from accounts.models import CustomUser


class Nganh(models.Model):
    ma_nganh = models.CharField(max_length=20, unique=True, verbose_name='Mã ngành')
    ten_nganh = models.CharField(max_length=200, verbose_name='Tên ngành')
    khoa = models.CharField(max_length=200, default='Khoa Công nghệ thông tin', verbose_name='Khoa')

    class Meta:
        verbose_name = 'Ngành học'
        verbose_name_plural = 'Ngành học'

    def __str__(self):
        return f"{self.ma_nganh} - {self.ten_nganh}"


class Lop(models.Model):
    """Mỗi lớp có đúng 1 cố vấn học tập phụ trách."""
    ten_lop = models.CharField(max_length=50, unique=True, verbose_name='Tên lớp')
    nganh = models.ForeignKey(Nganh, on_delete=models.SET_NULL, null=True, verbose_name='Ngành')
    khoa = models.CharField(max_length=10, verbose_name='Khóa học', help_text='VD: K2021')
    covan = models.OneToOneField(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='lop_phu_trach', verbose_name='Cố vấn học tập',
        limit_choices_to={'role': 'covan'}
    )

    class Meta:
        verbose_name = 'Lớp học'
        verbose_name_plural = 'Lớp học'
        ordering = ['ten_lop']

    def __str__(self):
        return self.ten_lop


class SinhVien(models.Model):
    TRANG_THAI_CHOICES = [
        ('dang_hoc', 'Đang học'),
        ('canh_bao', 'Cảnh báo học vụ'),
        ('dinh_chi', 'Đình chỉ'),
        ('tot_nghiep', 'Tốt nghiệp'),
        ('thoi_hoc', 'Thôi học'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='sinh_vien', verbose_name='Tài khoản')
    mssv = models.CharField(max_length=20, unique=True, verbose_name='Mã số sinh viên')
    ho_ten = models.CharField(max_length=200, verbose_name='Họ và tên')
    ngay_sinh = models.DateField(null=True, blank=True, verbose_name='Ngày sinh')
    gioi_tinh = models.CharField(max_length=5, choices=[('Nam', 'Nam'), ('Nu', 'Nữ')], blank=True)
    email = models.EmailField(blank=True, verbose_name='Email')
    so_dien_thoai = models.CharField(max_length=15, blank=True, verbose_name='Số điện thoại')
    nganh = models.ForeignKey(Nganh, on_delete=models.SET_NULL, null=True, verbose_name='Ngành')
    khoa = models.CharField(max_length=10, verbose_name='Khóa học', help_text='VD: K2021')
    lop = models.ForeignKey('Lop', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='sinh_viens', verbose_name='Lớp')
    covan = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='sinh_vien_phu_trach', verbose_name='Cố vấn học tập',
                               limit_choices_to={'role': 'covan'})
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='dang_hoc',
                                   verbose_name='Trạng thái')
    ngay_nhap_hoc = models.DateField(null=True, blank=True, verbose_name='Ngày nhập học')

    class Meta:
        verbose_name = 'Sinh viên'
        verbose_name_plural = 'Sinh viên'
        ordering = ['mssv']

    def __str__(self):
        return f"{self.mssv} - {self.ho_ten}"

    @property
    def ten_lop(self):
        return self.lop.ten_lop if self.lop else ''

    @property
    def covan_hien_tai(self):
        """Cố vấn lấy từ lớp (ưu tiên) hoặc field covan."""
        if self.lop and self.lop.covan:
            return self.lop.covan
        return self.covan

    @property
    def ten_covan(self):
        """Tên cố vấn, trả về '-' nếu không có."""
        cv = self.covan_hien_tai
        return cv.full_name if cv else '-'


class HocKy(models.Model):
    KY_CHOICES = [('1', 'Học kỳ 1'), ('2', 'Học kỳ 2'), ('3', 'Học kỳ hè')]
    ky = models.CharField(max_length=2, choices=KY_CHOICES, verbose_name='Kỳ học')
    nam_hoc = models.CharField(max_length=10, verbose_name='Năm học', help_text='VD: 2023-2024')
    ngay_bat_dau = models.DateField(null=True, blank=True, verbose_name='Ngày bắt đầu')
    ngay_ket_thuc = models.DateField(null=True, blank=True, verbose_name='Ngày kết thúc')
    la_hien_tai = models.BooleanField(default=False, verbose_name='Học kỳ hiện tại')

    class Meta:
        verbose_name = 'Học kỳ'
        verbose_name_plural = 'Học kỳ'
        unique_together = ['ky', 'nam_hoc']
        ordering = ['-nam_hoc', '-ky']

    def __str__(self):
        return f"HK{self.ky} - {self.nam_hoc}"

    def save(self, *args, **kwargs):
        if self.nam_hoc and self.ky:
            try:
                years = self.nam_hoc.split('-')
                if len(years) == 2:
                    start_year = int(years[0].strip())
                    end_year = int(years[1].strip())
                    from datetime import date
                    if self.ky == '1':
                        if not self.ngay_bat_dau:
                            self.ngay_bat_dau = date(start_year, 10, 1)
                        if not self.ngay_ket_thuc:
                            self.ngay_ket_thuc = date(end_year, 1, 31)
                    elif self.ky == '2':
                        if not self.ngay_bat_dau:
                            self.ngay_bat_dau = date(end_year, 2, 1)
                        if not self.ngay_ket_thuc:
                            self.ngay_ket_thuc = date(end_year, 6, 30)
            except Exception:
                pass

        if self.la_hien_tai:
            # Set other semesters' la_hien_tai to False (excluding this instance if it already exists)
            qs = HocKy.objects.filter(la_hien_tai=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            qs.update(la_hien_tai=False)
        super().save(*args, **kwargs)



class MonHoc(models.Model):
    LOAI_CHOICES = [
        ('bat_buoc', 'Bắt buộc'),
        ('tu_chon', 'Tự chọn'),
        ('dai_cuong', 'Đại cương'),
        ('chuyen_nganh', 'Chuyên ngành'),
    ]
    ma_mh = models.CharField(max_length=20, unique=True, verbose_name='Mã môn học')
    ten_mh = models.CharField(max_length=200, verbose_name='Tên môn học')
    so_tc = models.PositiveSmallIntegerField(verbose_name='Số tín chỉ')
    loai = models.CharField(max_length=20, choices=LOAI_CHOICES, default='bat_buoc', verbose_name='Loại học phần')
    mo_ta = models.TextField(blank=True, verbose_name='Mô tả')
    nganh = models.ForeignKey(Nganh, on_delete=models.SET_NULL, null=True, blank=True, related_name='mon_hocs', verbose_name='Chương trình đào tạo')
    nam_hoc_ctdt = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Năm học (CTĐT)')
    hoc_ky_ctdt = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Học kỳ (CTĐT)')

    class Meta:
        verbose_name = 'Môn học'
        verbose_name_plural = 'Môn học'
        ordering = ['ma_mh']

    def __str__(self):
        return f"{self.ma_mh} - {self.ten_mh} ({self.so_tc} TC)"
