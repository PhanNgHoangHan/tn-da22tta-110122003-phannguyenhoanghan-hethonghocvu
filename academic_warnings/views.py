from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
import openpyxl
from .models import CanhBaoHocVu
from students.models import SinhVien, HocKy
from results.utils import kiem_tra_canh_bao, dem_canh_bao_lien_tiep


@login_required
def canhbao_list(request):
    qs = CanhBaoHocVu.objects.select_related('sinh_vien', 'hoc_ky', 'sinh_vien__nganh').all()

    if request.user.is_sinhvien:
        qs = qs.filter(sinh_vien__user=request.user)
    elif request.user.is_covan:
        qs = qs.filter(sinh_vien__lop__covan=request.user)

    muc       = request.GET.get('muc', '')
    trang_thai = request.GET.get('trang_thai', '')
    hk_id     = request.GET.get('hoc_ky', '')
    q         = request.GET.get('q', '')

    if muc:        qs = qs.filter(muc_canh_bao=muc)
    if trang_thai: qs = qs.filter(trang_thai=trang_thai)
    if hk_id:      qs = qs.filter(hoc_ky_id=hk_id)
    if q:          qs = qs.filter(Q(sinh_vien__mssv__icontains=q) | Q(sinh_vien__ho_ten__icontains=q))

    hockys = HocKy.objects.all()
    return render(request, 'academic_warnings/canhbao_list.html', {
        'canh_baos': qs, 'hockys': hockys,
        'muc': muc, 'trang_thai': trang_thai, 'hk_id': hk_id, 'q': q,
    })


@login_required
def canhbao_detail(request, pk):
    cb = get_object_or_404(CanhBaoHocVu, pk=pk)
    return render(request, 'academic_warnings/canhbao_detail.html', {'cb': cb})


@login_required
def canhbao_update_status(request, pk):
    if request.user.is_sinhvien:
        messages.error(request, 'Bạn không có quyền cập nhật.')
        return redirect('academic_warnings:canhbao_list')
    cb = get_object_or_404(CanhBaoHocVu, pk=pk)
    if request.method == 'POST':
        cb.trang_thai = request.POST.get('trang_thai', cb.trang_thai)
        cb.ghi_chu    = request.POST.get('ghi_chu', cb.ghi_chu)
        cb.save()
        if cb.muc_canh_bao == 'buoc_thoi_hoc':
            cb.sinh_vien.trang_thai = 'dinh_chi'
            cb.sinh_vien.save()
        messages.success(request, 'Cập nhật trạng thái cảnh báo thành công.')
        return redirect('academic_warnings:canhbao_list')
    return render(request, 'academic_warnings/canhbao_update.html', {'cb': cb})


@login_required
def kiem_tra_canh_bao_view(request):
    """Kiểm tra cảnh báo cho tất cả SV trong học kỳ được chọn."""
    if request.user.is_sinhvien:
        messages.error(request, 'Bạn không có quyền.')
        return redirect('dashboard:index')

    hockys = HocKy.objects.all()
    if request.method == 'POST':
        hk_id = request.POST.get('hoc_ky')
        hk = get_object_or_404(HocKy, pk=hk_id)
        count_cb = count_bth = 0

        svs = SinhVien.objects.filter(trang_thai__in=['dang_hoc', 'canh_bao'])
        if request.user.is_covan:
            svs = svs.filter(lop__covan=request.user)

        for sv in svs:
            co_canh_bao, ly_do = kiem_tra_canh_bao(sv, hk)
            if not co_canh_bao:
                continue

            # Đếm số lần cảnh báo liên tiếp hiện tại (chưa tính HK này)
            so_lan_lien_tiep = dem_canh_bao_lien_tiep(sv) + 1
            muc = 'buoc_thoi_hoc' if so_lan_lien_tiep > 2 else 'canh_bao'
            if so_lan_lien_tiep > 2:
                ly_do = f'Đã bị cảnh báo {so_lan_lien_tiep - 1} lần liên tiếp. ' + ly_do

            CanhBaoHocVu.objects.update_or_create(
                sinh_vien=sv, hoc_ky=hk,
                defaults={
                    'muc_canh_bao': muc,
                    'ly_do': ly_do,
                    'trang_thai': 'moi',
                    'so_lan_canh_bao': so_lan_lien_tiep,
                }
            )

            if muc == 'buoc_thoi_hoc':
                sv.trang_thai = 'dinh_chi'
                sv.save()
                count_bth += 1
            else:
                sv.trang_thai = 'canh_bao'
                sv.save()
                count_cb += 1

        msg = f'Đã kiểm tra: {count_cb} sinh viên cảnh báo học vụ'
        if count_bth:
            msg += f', {count_bth} sinh viên buộc thôi học'
        messages.success(request, msg + '.')
        return redirect('academic_warnings:canhbao_list')

    return render(request, 'academic_warnings/kiem_tra.html', {'hockys': hockys})


@login_required
def export_canhbao(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Cảnh báo học vụ'
    ws.append(['MSSV', 'Họ tên', 'Ngành', 'Lớp', 'Học kỳ',
               'Mức cảnh báo', 'Lần thứ', 'Lý do', 'Trạng thái', 'Ngày tạo'])
    qs = CanhBaoHocVu.objects.select_related('sinh_vien', 'hoc_ky', 'sinh_vien__nganh').all()
    if request.user.is_covan:
        qs = qs.filter(sinh_vien__lop__covan=request.user)
    for cb in qs:
        ws.append([
            cb.sinh_vien.mssv, cb.sinh_vien.ho_ten,
            cb.sinh_vien.nganh.ten_nganh if cb.sinh_vien.nganh else '',
            cb.sinh_vien.lop,
            str(cb.hoc_ky), cb.get_muc_canh_bao_display(),
            cb.so_lan_canh_bao, cb.ly_do,
            cb.get_trang_thai_display(),
            cb.ngay_tao.strftime('%d/%m/%Y')
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="canh_bao_hoc_vu.xlsx"'
    wb.save(response)
    return response
