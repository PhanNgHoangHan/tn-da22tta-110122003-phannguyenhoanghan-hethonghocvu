from django.contrib import admin
from .models import KetQuaHocTap


@admin.register(KetQuaHocTap)
class KetQuaAdmin(admin.ModelAdmin):
    list_display = ['sinh_vien', 'mon_hoc', 'hoc_ky', 'diem_qt', 'diem_thi', 'diem_tk', 'lan_hoc']
    list_filter = ['hoc_ky', 'mon_hoc']
    search_fields = ['sinh_vien__mssv', 'sinh_vien__ho_ten', 'mon_hoc__ma_mh']
    raw_id_fields = ['sinh_vien', 'mon_hoc']
