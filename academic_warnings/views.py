from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
import openpyxl
from .models import CanhBaoHocVu
from students.models import SinhVien, HocKy
from results.utils import kiem_tra_canh_bao, dem_canh_bao_lien_tiep, xac_dinh_muc_canh_bao


@login_required
def canhbao_list(request):
    qs = CanhBaoHocVu.objects.select_related('sinh_vien', 'hoc_ky', 'sinh_vien__nganh', 'sinh_vien__lop').exclude(nguoi_dung_an=request.user).order_by('trang_thai', '-ngay_tao')

    muc       = request.GET.get('muc', '')
    trang_thai = request.GET.get('trang_thai', '')
    hk_id     = request.GET.get('hoc_ky', '')
    q         = request.GET.get('q', '')
    
    # Lấy các bộ lọc phân cấp
    khoa = request.GET.get('khoa', '')
    nganh_id = request.GET.get('nganh', '')
    lop_id = request.GET.get('lop', '')
    khoa_hoc = request.GET.get('khoa_hoc', '')

    if request.user.is_sinhvien:
        qs = qs.filter(sinh_vien__user=request.user)
    else:
        if request.user.is_covan:
            qs = qs.filter(sinh_vien__lop__covan=request.user)
        
        # Áp dụng bộ lọc phân cấp cho cả Giáo vụ và Cố vấn
        if khoa_hoc:
            cohort_suffix = khoa_hoc[-2:]
            qs = qs.filter(sinh_vien__lop__ten_lop__contains=cohort_suffix)
        if khoa:
            qs = qs.filter(sinh_vien__nganh__khoa=khoa)
        if nganh_id:
            qs = qs.filter(sinh_vien__nganh_id=nganh_id)
        if lop_id:
            qs = qs.filter(sinh_vien__lop_id=lop_id)

    if muc:        qs = qs.filter(muc_canh_bao=muc)
    if trang_thai: qs = qs.filter(trang_thai=trang_thai)
    if hk_id:      qs = qs.filter(hoc_ky_id=hk_id)
    if q:
        from results.utils import remove_accents
        q_clean = remove_accents(q)
        qs = [
            cb for cb in qs
            if q_clean in remove_accents(cb.sinh_vien.mssv)
            or q_clean in remove_accents(cb.sinh_vien.ho_ten)
        ]

    hockys = HocKy.objects.all().order_by('-nam_hoc', '-ky')
    
    # Dữ liệu cho bộ lọc phân cấp (để hiển thị dropdown)
    from students.models import Nganh, Lop
    import re
    
    nganhs = Nganh.objects.all()
    khoas = Nganh.objects.values_list('khoa', flat=True).distinct()
    
    # Lấy danh sách khóa học duy nhất từ các lớp
    unique_years = set()
    for name in Lop.objects.values_list('ten_lop', flat=True):
        m = re.search(r'\d{2}', name)
        if m:
            unique_years.add("20" + m.group())
    khoa_hocs = sorted(list(unique_years), reverse=True)

    lops = Lop.objects.all()
    if request.user.is_covan:
        lops = lops.filter(covan=request.user)
    if nganh_id:
        lops = lops.filter(nganh_id=nganh_id)
    if khoa_hoc:
        cohort_suffix = khoa_hoc[-2:]
        lops = lops.filter(ten_lop__contains=cohort_suffix)
        
    if khoa:
        nganhs = nganhs.filter(khoa=khoa)

    return render(request, 'academic_warnings/canhbao_list.html', {
        'canh_baos': qs, 
        'hockys': hockys,
        'nganhs': nganhs,
        'khoas': khoas,
        'lops': lops,
        'khoa_hocs': khoa_hocs,
        'muc': muc, 
        'trang_thai': trang_thai, 
        'hk_id': hk_id, 
        'selected_khoa': khoa,
        'nganh_id': nganh_id,
        'selected_lop': lop_id,
        'selected_khoa_hoc': khoa_hoc,
        'q': q,
    })


@login_required
def canhbao_detail(request, pk):
    cb = get_object_or_404(CanhBaoHocVu, pk=pk)
    if request.user.is_sinhvien and cb.sinh_vien.user != request.user:
        messages.error(request, 'Bạn không có quyền truy cập cảnh báo này.')
        return redirect('academic_warnings:canhbao_list')
    elif request.user.is_covan and cb.sinh_vien.lop.covan != request.user:
        messages.error(request, 'Bạn không có quyền truy cập cảnh báo này.')
        return redirect('academic_warnings:canhbao_list')
    return render(request, 'academic_warnings/canhbao_detail.html', {'cb': cb})


@login_required
def canhbao_update_status(request, pk):
    messages.error(request, 'Chức năng cập nhật cảnh báo đã bị vô hiệu hóa. Chỉ có thể xem cảnh báo.')
    return redirect('academic_warnings:canhbao_list')





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


@login_required
def canhbao_hide(request, pk):
    cb = get_object_or_404(CanhBaoHocVu, pk=pk)
    # Check permissions: only covan of this student's class, or staff/admin can delete
    if not (request.user.is_giaovu or request.user.is_admin or (request.user.is_covan and cb.sinh_vien.lop.covan == request.user)):
        messages.error(request, 'Bạn không có quyền ẩn cảnh báo này.')
        return redirect('academic_warnings:canhbao_list')
    
    cb.nguoi_dung_an.add(request.user)
    messages.success(request, 'Đã ẩn cảnh báo khỏi danh sách quản lý.')
    return redirect('academic_warnings:canhbao_list')


from django.core.mail import send_mail
from django.conf import settings

@login_required
def canhbao_gui_thong_bao(request, pk):
    if not (request.user.is_giaovu or request.user.is_admin):
        messages.error(request, 'Chỉ Giáo vụ mới có quyền gửi thông báo cảnh báo.')
        return redirect('academic_warnings:canhbao_detail', pk=pk)
        
    cb = get_object_or_404(CanhBaoHocVu, pk=pk)
    
    # Send email
    recipient_list = []
    if cb.sinh_vien.email:
        recipient_list.append(cb.sinh_vien.email)
        
    if recipient_list:
        subject = f'[TVU] Thông báo Cảnh báo Học vụ - Học kỳ {cb.hoc_ky}'
        message = f"""Kính gửi Sinh viên {cb.sinh_vien.ho_ten},

Hệ thống Quản lý Học vụ Đại học Trà Vinh xin thông báo về tình trạng học tập của sinh viên:
- Họ tên: {cb.sinh_vien.ho_ten}
- Mã số sinh viên: {cb.sinh_vien.mssv}
- Lớp: {cb.sinh_vien.lop.ten_lop if cb.sinh_vien.lop else '-'}
- Học kỳ cảnh báo: {cb.hoc_ky}
- Mức cảnh báo: {cb.get_muc_canh_bao_display()} (Lần thứ: {cb.so_lan_canh_bao})
- Lý do cảnh báo: {cb.ly_do}

Kính đề nghị sinh viên liên hệ ngay với Cố vấn học tập để nhận tư vấn học vụ và lập kế hoạch cải thiện kết quả học tập.

Trân trọng,
Phòng Giáo vụ - Đại học Trà Vinh
"""
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or 'giaovu@tvu.edu.vn',
                recipient_list,
                fail_silently=False,
            )
            cb.trang_thai = 'da_xu_ly'
            cb.save()
            messages.success(request, f'Đã gửi email thông báo thành công đến Sinh viên ({", ".join(recipient_list)}). Cảnh báo chuyển sang trạng thái Đã thông báo.')
        except Exception as e:
            messages.error(request, f'Lỗi khi gửi email: {e}')
    else:
        # Nếu không có email thì vẫn đổi trạng thái
        cb.trang_thai = 'da_xu_ly'
        cb.save()
        messages.warning(request, 'Không tìm thấy địa chỉ email của sinh viên. Trạng thái cảnh báo vẫn được cập nhật thành Đã thông báo.')
        
    return redirect('academic_warnings:canhbao_detail', pk=pk)


@login_required
def canhbao_gui_thong_bao_hang_loat(request):
    if not (request.user.is_giaovu or request.user.is_admin):
        messages.error(request, 'Chỉ Giáo vụ mới có quyền gửi thông báo cảnh báo.')
        return redirect('academic_warnings:canhbao_list')

    # Re-apply the filters from GET/POST parameters
    qs = CanhBaoHocVu.objects.select_related('sinh_vien', 'hoc_ky', 'sinh_vien__lop').filter(
        trang_thai='chua_xu_ly'
    ).exclude(nguoi_dung_an=request.user)

    if request.user.is_covan:
        qs = qs.filter(sinh_vien__lop__covan=request.user)

    muc       = request.GET.get('muc', '') or request.POST.get('muc', '')
    hk_id     = request.GET.get('hoc_ky', '') or request.POST.get('hoc_ky', '')
    lop_id    = request.GET.get('lop', '') or request.POST.get('lop', '')
    q         = request.GET.get('q', '') or request.POST.get('q', '')

    if muc:        qs = qs.filter(muc_canh_bao=muc)
    if hk_id:      qs = qs.filter(hoc_ky_id=hk_id)
    if lop_id:     qs = qs.filter(sinh_vien__lop_id=lop_id)
    if q:
        from results.utils import remove_accents
        q_clean = remove_accents(q)
        qs = [
            cb for cb in qs
            if q_clean in remove_accents(cb.sinh_vien.mssv)
            or q_clean in remove_accents(cb.sinh_vien.ho_ten)
        ]

    # Send emails
    success_count = 0
    errors = []

    for cb in qs:
        recipient_list = []
        if cb.sinh_vien.email:
            recipient_list.append(cb.sinh_vien.email)
        
        if recipient_list:
            subject = f'[TVU] Thông báo Cảnh báo Học vụ - Học kỳ {cb.hoc_ky}'
            message = f"""Kính gửi Sinh viên {cb.sinh_vien.ho_ten},

Hệ thống Quản lý Học vụ Đại học Trà Vinh xin thông báo về tình trạng học tập của sinh viên:
- Họ tên: {cb.sinh_vien.ho_ten}
- Mã số sinh viên: {cb.sinh_vien.mssv}
- Lớp: {cb.sinh_vien.lop.ten_lop if cb.sinh_vien.lop else '-'}
- Học kỳ cảnh báo: {cb.hoc_ky}
- Mức cảnh báo: {cb.get_muc_canh_bao_display()} (Lần thứ: {cb.so_lan_canh_bao})
- Lý do cảnh báo: {cb.ly_do}

Kính đề nghị sinh viên liên hệ ngay với Cố vấn học tập để nhận tư vấn học vụ và lập kế hoạch cải thiện kết quả học tập.

Trân trọng,
Phòng Giáo vụ - Đại học Trà Vinh
"""
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL or 'giaovu@tvu.edu.vn',
                    recipient_list,
                    fail_silently=False,
                )
                cb.trang_thai = 'da_xu_ly'
                cb.save()
                success_count += 1
            except Exception as e:
                errors.append(f"{cb.sinh_vien.ho_ten}: {str(e)}")
        else:
            # Nếu không có email, vẫn đổi trạng thái
            cb.trang_thai = 'da_xu_ly'
            cb.save()
            success_count += 1

    if success_count > 0:
        messages.success(request, f'Đã gửi email thông báo học vụ thành công cho {success_count} sinh viên.')
    if errors:
        messages.error(request, f'Lỗi gửi mail ở {len(errors)} sinh viên: {", ".join(errors[:5])}')
        
    return redirect('academic_warnings:canhbao_list')
