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
    qs = CanhBaoHocVu.objects.select_related('sinh_vien', 'hoc_ky', 'sinh_vien__nganh', 'sinh_vien__lop').exclude(nguoi_dung_an=request.user)

    if request.user.is_sinhvien:
        qs = qs.filter(sinh_vien__user=request.user)
    elif request.user.is_covan:
        qs = qs.filter(sinh_vien__lop__covan=request.user)

    muc       = request.GET.get('muc', '')
    trang_thai = request.GET.get('trang_thai', '')
    hk_id     = request.GET.get('hoc_ky', '')
    lop_id    = request.GET.get('lop', '')
    q         = request.GET.get('q', '')

    if muc:        qs = qs.filter(muc_canh_bao=muc)
    if trang_thai: qs = qs.filter(trang_thai=trang_thai)
    if hk_id:      qs = qs.filter(hoc_ky_id=hk_id)
    if lop_id:     qs = qs.filter(sinh_vien__lop_id=lop_id)
    if q:          qs = qs.filter(Q(sinh_vien__mssv__icontains=q) | Q(sinh_vien__ho_ten__icontains=q))

    hockys = HocKy.objects.all()
    
    # Lấy danh sách lớp cho Giáo vụ / Admin lọc
    from students.models import Lop
    lops = Lop.objects.all()

    return render(request, 'academic_warnings/canhbao_list.html', {
        'canh_baos': qs, 
        'hockys': hockys,
        'lops': lops,
        'muc': muc, 
        'trang_thai': trang_thai, 
        'hk_id': hk_id, 
        'selected_lop': lop_id,
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
    if request.user.is_sinhvien or request.user.is_covan:
        messages.error(request, 'Bạn không có quyền cập nhật cảnh báo.')
        return redirect('academic_warnings:canhbao_list')
    cb = get_object_or_404(CanhBaoHocVu, pk=pk)
    if request.user.is_covan and cb.sinh_vien.lop.covan != request.user:
        messages.error(request, 'Bạn không có quyền cập nhật cảnh báo này.')
        return redirect('academic_warnings:canhbao_list')
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
- MSSV: {cb.sinh_vien.mssv}
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
            messages.success(request, f'Đã gửi email thông báo thành công đến Sinh viên ({", ".join(recipient_list)}). Cảnh báo chuyển sang trạng thái Đã xử lý.')
        except Exception as e:
            messages.error(request, f'Lỗi khi gửi email: {e}')
    else:
        # Nếu không có email thì vẫn đổi trạng thái
        cb.trang_thai = 'da_xu_ly'
        cb.save()
        messages.warning(request, 'Không tìm thấy địa chỉ email của sinh viên. Trạng thái cảnh báo vẫn được cập nhật thành Đã xử lý.')
        
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
    if q:          qs = qs.filter(Q(sinh_vien__mssv__icontains=q) | Q(sinh_vien__ho_ten__icontains=q))

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
- MSSV: {cb.sinh_vien.mssv}
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
        messages.success(request, f'Đã gửi email thông báo học vụ thành công cho {success_count} sinh viên (và cố vấn tương ứng).')
    if errors:
        messages.error(request, f'Lỗi gửi mail ở {len(errors)} sinh viên: {", ".join(errors[:5])}')
        
    return redirect('academic_warnings:canhbao_list')
