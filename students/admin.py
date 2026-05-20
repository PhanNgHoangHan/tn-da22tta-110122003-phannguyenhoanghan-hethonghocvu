from django.contrib import admin
from .models import SinhVien, MonHoc, HocKy, Nganh, Lop


@admin.register(Nganh)
class NganhAdmin(admin.ModelAdmin):
    list_display = ['ma_nganh', 'ten_nganh']
    search_fields = ['ma_nganh', 'ten_nganh']


@admin.register(Lop)
class LopAdmin(admin.ModelAdmin):
    list_display = ['ten_lop', 'nganh', 'khoa', 'covan']
    list_filter = ['nganh', 'khoa']
    search_fields = ['ten_lop']


@admin.register(SinhVien)
class SinhVienAdmin(admin.ModelAdmin):
    list_display = ['mssv', 'ho_ten', 'nganh', 'lop', 'khoa', 'trang_thai']
    list_filter = ['trang_thai', 'nganh', 'khoa', 'lop']
    search_fields = ['mssv', 'ho_ten', 'email']


@admin.register(HocKy)
class HocKyAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'ngay_bat_dau', 'ngay_ket_thuc', 'la_hien_tai']
    list_filter = ['la_hien_tai']


@admin.register(MonHoc)
class MonHocAdmin(admin.ModelAdmin):
    list_display = ['ma_mh', 'ten_mh', 'so_tc', 'loai']
    list_filter = ['loai']
    search_fields = ['ma_mh', 'ten_mh']
