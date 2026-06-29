from django.contrib import admin
from .models import CanhBaoHocVu


@admin.register(CanhBaoHocVu)
class CanhBaoAdmin(admin.ModelAdmin):
    list_display = ['sinh_vien', 'hoc_ky', 'muc_canh_bao', 'trang_thai', 'ngay_tao']
    list_filter = ['muc_canh_bao', 'trang_thai', 'hoc_ky']
    search_fields = ['sinh_vien__mssv', 'sinh_vien__ho_ten']
    readonly_fields = ['ngay_tao']
