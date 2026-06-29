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
    latest_hk = HocKy.objects.filter(ket_qua__diem_tk__isnull=False).distinct().order_by('-nam_hoc', '-ky').first()
    if not latest_hk:
        latest_hk = HocKy.objects.order_by('-nam_hoc', '-ky').first()
    qs = CanhBaoHocVu.objects.select_related('sinh_vien', 'hoc_ky', 'sinh_vien__nganh', 'sinh_vien__lop').exclude(nguoi_dung_an=request.user).order_by('trang_thai', '-ngay_tao')
    if latest_hk:
        qs = qs.filter(hoc_ky=latest_hk)

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
            qs = qs.filter(sinh_vien__lop__ten_lop__istartswith=f'DA{cohort_suffix}')
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
    
    nganhs = Nganh.objects.exclude(ma_nganh__iexact='None').exclude(ten_nganh__iexact='None')
    khoas = [k for k in Nganh.objects.exclude(khoa__isnull=True).exclude(khoa='').values_list('khoa', flat=True).distinct() if k.lower() != 'none']
    
    # Lấy danh sách khóa học duy nhất từ các lớp
    unique_years = set()
    for name in Lop.objects.values_list('ten_lop', flat=True):
        if name:
            m = re.search(r'\d{2}', name)
            if m:
                unique_years.add("20" + m.group())
    khoa_hocs = sorted(list(unique_years), reverse=True)

    lops = Lop.objects.exclude(ten_lop__iexact='None')
    if request.user.is_covan:
        lops = lops.filter(covan=request.user)
    if nganh_id:
        lops = lops.filter(nganh_id=nganh_id)
    if khoa_hoc:
        cohort_suffix = khoa_hoc[-2:]
        lops = lops.filter(ten_lop__istartswith=f'DA{cohort_suffix}')
        
    if khoa:
        nganhs = nganhs.filter(khoa=khoa)
        lops = lops.filter(nganh__khoa=khoa)

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
        'latest_hk': latest_hk,
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
    latest_hk = HocKy.objects.filter(ket_qua__diem_tk__isnull=False).distinct().order_by('-nam_hoc', '-ky').first()
    if not latest_hk:
        latest_hk = HocKy.objects.order_by('-nam_hoc', '-ky').first()
    qs = CanhBaoHocVu.objects.select_related('sinh_vien', 'hoc_ky', 'sinh_vien__lop').filter(
        trang_thai='chua_xu_ly'
    ).exclude(nguoi_dung_an=request.user)
    if latest_hk:
        qs = qs.filter(hoc_ky=latest_hk)

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


@login_required
def canhbao_som_list(request):
    """Danh sách cảnh báo sớm học vụ dành cho cố vấn học tập và giáo vụ."""
    if request.user.is_sinhvien:
        # Sinh viên thì chuyển thẳng đến trang chi tiết cảnh báo sớm của chính mình
        try:
            mssv = request.user.sinh_vien.mssv
            return redirect('academic_warnings:canhbao_som_detail', mssv=mssv)
        except Exception:
            messages.error(request, 'Không tìm thấy hồ sơ sinh viên.')
            return redirect('dashboard:index')

    from results.utils import tinh_canh_bao_som, remove_accents
    from students.models import Nganh, Lop

    qs = SinhVien.objects.select_related('lop', 'nganh', 'lop__covan').all()
    if request.user.is_covan:
        qs = qs.filter(lop__covan=request.user)

    # Lấy các bộ lọc phân cấp
    khoa = request.GET.get('khoa', '')
    nganh_id = request.GET.get('nganh', '')
    lop_id = request.GET.get('lop', '')
    khoa_hoc = request.GET.get('khoa_hoc', '')
    q = request.GET.get('q', '')
    muc_nguy_co_filter = request.GET.get('muc_nguy_co', '')

    # Áp dụng bộ lọc
    if khoa_hoc:
        cohort_suffix = khoa_hoc[-2:]
        qs = qs.filter(lop__ten_lop__istartswith=f'DA{cohort_suffix}')
    if khoa:
        qs = qs.filter(nganh__khoa=khoa)
    if nganh_id:
        qs = qs.filter(nganh_id=nganh_id)
    if lop_id:
        qs = qs.filter(lop_id=lop_id)
    if q:
        q_clean = remove_accents(q)
        qs = [
            sv for sv in qs
            if q_clean in remove_accents(sv.mssv)
            or q_clean in remove_accents(sv.ho_ten)
        ]

    # Chuyển QuerySet/danh sách sinh viên thành list và trích xuất danh sách ID
    student_list = list(qs)
    student_ids = [sv.id for sv in student_list]

    from results.models import KetQuaHocTap

    # Truy vấn tối ưu hóa (batch select) tất cả điểm và cảnh báo học vụ
    results_list = list(
        KetQuaHocTap.objects.filter(sinh_vien_id__in=student_ids, diem_tk__isnull=False)
        .select_related('mon_hoc', 'hoc_ky')
        .order_by('hoc_ky__nam_hoc', 'hoc_ky__ky')
    )
    prefetch_results = {}
    for r in results_list:
        if r.sinh_vien_id not in prefetch_results:
            prefetch_results[r.sinh_vien_id] = []
        prefetch_results[r.sinh_vien_id].append(r)

    warnings_list = list(CanhBaoHocVu.objects.filter(sinh_vien_id__in=student_ids))
    prefetch_warnings = {}
    for cb in warnings_list:
        prefetch_warnings[(cb.sinh_vien_id, cb.hoc_ky_id)] = cb

    # Tính toán thông tin cảnh báo sớm sử dụng dữ liệu đã prefetch
    students_data = []
    counts = {'total': 0, 'safe': 0, 'monitor': 0, 'warning_1': 0, 'warning_2': 0}
    latest_hk = HocKy.objects.filter(ket_qua__diem_tk__isnull=False).distinct().order_by('-nam_hoc', '-ky').first()
    if not latest_hk:
        latest_hk = HocKy.objects.order_by('-nam_hoc', '-ky').first()

    for sv in student_list:
        analysis = tinh_canh_bao_som(sv, hoc_ky=latest_hk, prefetch_results=prefetch_results, prefetch_warnings=prefetch_warnings)
        level = analysis['muc_nguy_co']
        counts['total'] += 1
        if level in counts:
            counts[level] += 1
            
        if not muc_nguy_co_filter or level == muc_nguy_co_filter:
            students_data.append(analysis)

    # Đưa các sinh viên có mức nguy cơ cao lên đầu
    level_order = {'warning_2': 0, 'warning_1': 1, 'monitor': 2, 'safe': 3}
    students_data.sort(key=lambda x: level_order.get(x['muc_nguy_co'], 4))

    # Bộ lọc dropdowns
    nganhs = Nganh.objects.exclude(ma_nganh__iexact='None').exclude(ten_nganh__iexact='None')
    khoas = [k for k in Nganh.objects.exclude(khoa__isnull=True).exclude(khoa='').values_list('khoa', flat=True).distinct() if k.lower() != 'none']
    
    import re
    unique_years = set()
    for name in Lop.objects.values_list('ten_lop', flat=True):
        if name:
            m = re.search(r'\d{2}', name)
            if m:
                unique_years.add("20" + m.group())
    khoa_hocs = sorted(list(unique_years), reverse=True)

    lops = Lop.objects.exclude(ten_lop__iexact='None')
    if request.user.is_covan:
        lops = lops.filter(covan=request.user)
    if nganh_id:
        lops = lops.filter(nganh_id=nganh_id)
    if khoa_hoc:
        cohort_suffix = khoa_hoc[-2:]
        lops = lops.filter(ten_lop__istartswith=f'DA{cohort_suffix}')
    if khoa:
        nganhs = nganhs.filter(khoa=khoa)
        lops = lops.filter(nganh__khoa=khoa)

    return render(request, 'academic_warnings/canhbao_som_list.html', {
        'students_data': students_data,
        'counts': counts,
        'khoas': khoas,
        'nganhs': nganhs,
        'lops': lops,
        'khoa_hocs': khoa_hocs,
        'selected_khoa': khoa,
        'nganh_id': nganh_id,
        'selected_lop': lop_id,
        'selected_khoa_hoc': khoa_hoc,
        'muc_nguy_co_filter': muc_nguy_co_filter,
        'q': q,
        'latest_hk': latest_hk,
    })


@login_required
def canhbao_som_detail(request, mssv):
    """Chi tiết phân tích cảnh báo sớm học vụ của 1 sinh viên (5 tầng)."""
    sv = get_object_or_404(SinhVien, mssv=mssv)

    # Kiểm tra quyền truy cập
    if request.user.is_sinhvien and request.user.sinh_vien.mssv != mssv:
        messages.error(request, 'Bạn không có quyền truy cập hồ sơ cảnh báo sớm của sinh viên khác.')
        return redirect('dashboard:index')
    elif request.user.is_covan and sv.lop.covan != request.user:
        messages.error(request, 'Bạn không có quyền truy cập cảnh báo sớm của sinh viên lớp khác.')
        return redirect('academic_warnings:canhbao_som_list')

    from results.utils import tinh_canh_bao_som
    from .models import LichSuGuiCanhBaoSom

    from results.models import KetQuaHocTap
    from .models import LichSuGuiCanhBaoSom

    # Lấy học kỳ được chọn để xem phân tích chi tiết (mặc định là học kỳ gần nhất có điểm của sinh viên này)
    hk_id = request.GET.get('hoc_ky', '')
    selected_hk = None
    if hk_id:
        selected_hk = get_object_or_404(HocKy, pk=hk_id)
    else:
        selected_hk = HocKy.objects.filter(ket_qua__sinh_vien=sv, ket_qua__diem_tk__isnull=False).distinct().order_by('-nam_hoc', '-ky').first()
        if not selected_hk:
            selected_hk = HocKy.objects.order_by('-nam_hoc', '-ky').first()

    # Prefetch kết quả của sinh viên này
    results_list = list(
        KetQuaHocTap.objects.filter(sinh_vien=sv, diem_tk__isnull=False)
        .select_related('mon_hoc', 'hoc_ky')
        .order_by('hoc_ky__nam_hoc', 'hoc_ky__ky')
    )
    prefetch_results = {sv.id: results_list}

    warnings_list = list(CanhBaoHocVu.objects.filter(sinh_vien=sv))
    prefetch_warnings = {}
    for cb in warnings_list:
        prefetch_warnings[(cb.sinh_vien_id, cb.hoc_ky_id)] = cb

    # Tính toán cảnh báo sớm hiện tại
    analysis = tinh_canh_bao_som(sv, selected_hk, prefetch_results=prefetch_results, prefetch_warnings=prefetch_warnings)

    # Lấy lịch sử tất cả các học kỳ có điểm để vẽ biểu đồ và hiển thị tiến trình
    hockys = HocKy.objects.filter(ket_qua__sinh_vien=sv).distinct().order_by('nam_hoc', 'ky')
    history_data = []
    
    for hk in hockys:
        analysis_hk = tinh_canh_bao_som(sv, hk, prefetch_results=prefetch_results, prefetch_warnings=prefetch_warnings)
        history_data.append({
            'hoc_ky': str(hk),
            'gpa_hk_4': analysis_hk['gpa_hk_4'],
            'gpa_tl_4': analysis_hk['gpa_tl_4'],
            'muc_nguy_co': analysis_hk['muc_nguy_co'],
            'muc_nguy_co_display': analysis_hk['muc_nguy_co_display'],
            'mau_nguy_co': analysis_hk['mau_nguy_co'],
        })

    # Lịch sử gửi email cảnh báo sớm
    lich_su_gui = LichSuGuiCanhBaoSom.objects.filter(sinh_vien=sv).order_by('-ngay_gui')

    return render(request, 'academic_warnings/canhbao_som_detail.html', {
        'sv': sv,
        'analysis': analysis,
        'history_data': history_data,
        'hockys': hockys,
        'selected_hk': selected_hk or analysis['hoc_ky'],
        'lich_su_gui': lich_su_gui,
    })


@login_required
def canhbao_som_gui_email(request, mssv):
    """Gửi email thông báo cảnh báo sớm cho 1 sinh viên."""
    if not (request.user.is_giaovu or request.user.is_admin):
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('dashboard:index')

    sv = get_object_or_404(SinhVien, mssv=mssv)
    if request.user.is_covan and sv.lop.covan != request.user:
        messages.error(request, 'Bạn chỉ có quyền gửi thông báo cho sinh viên lớp mình phụ trách.')
        return redirect('academic_warnings:canhbao_som_list')

    from results.utils import tinh_canh_bao_som
    from .models import LichSuGuiCanhBaoSom
    from django.core.mail import send_mail
    from django.conf import settings

    analysis = tinh_canh_bao_som(sv)
    
    if not sv.email:
        messages.error(request, f'Sinh viên {sv.ho_ten} chưa cập nhật địa chỉ email.')
        return redirect('academic_warnings:canhbao_som_detail', mssv=mssv)

    subject = f'[TVU] Thông báo Cảnh báo sớm Học tập & Học vụ - Mức độ: {analysis["muc_nguy_co_display"]}'
    
    goi_y_str = ""
    if analysis['goi_y']:
        goi_y_str = "\nKhuyến nghị cải thiện:\n"
        for idx, gy in enumerate(analysis['goi_y'], 1):
            # Remove markdown bold syntax for plain text email
            clean_gy = gy.replace('**', '')
            goi_y_str += f"{idx}. {clean_gy}\n"

    body = f"""Kính gửi Sinh viên {sv.ho_ten},

Hệ thống Quản lý Học vụ Trường Kỹ thuật và Công nghệ Đại học Trà Vinh gửi thông báo phân tích kết quả học tập tính đến học kỳ {analysis['hoc_ky']}:

- Họ tên: {sv.ho_ten}
- Mã số sinh viên: {sv.mssv}
- Lớp: {sv.lop.ten_lop if sv.lop else '-'}
- Điểm trung bình học kỳ vừa qua: {analysis['gpa_hk_4']:.2f} (Hệ 4) / {analysis['gpa_hk_10']:.2f} (Hệ 10)
- Điểm trung bình tích lũy (GPA): {analysis['gpa_tl_4']:.2f} (Hệ 4) / {analysis['gpa_tl_10']:.2f} (Hệ 10)
- Tín chỉ tích lũy: {analysis['tc_tl_pass']}/{analysis['tc_tl_reg']} TC
- Xu hướng học tập: {analysis['xu_huong_display']}

---
MỨC ĐỘ NGUY CƠ HỌC VỤ: {analysis['muc_nguy_co_display']}
Chi tiết phân tích: {analysis['ly_do']}
---
{goi_y_str}
Chúc bạn sớm cải thiện được kết quả học tập của mình. Nếu cần thêm hỗ trợ, vui lòng chủ động đặt lịch hẹn để trao đổi thêm với Cố vấn học tập của lớp.

Trân trọng,
Giáo vụ Trường Kỹ thuật và Công nghệ
"""

    email_sent = False
    email_error = None
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL or 'giaovu@tvu.edu.vn',
            [sv.email],
            fail_silently=False,
        )
        email_sent = True
    except Exception as e:
        email_error = str(e)
        
    # Vẫn lưu lịch sử gửi email để phục vụ demo/kiểm thử khi thiếu SMTP
    LichSuGuiCanhBaoSom.objects.create(
        sinh_vien=sv,
        hoc_ky=analysis['hoc_ky'],
        muc_nguy_co=analysis['muc_nguy_co_display'],
        gpa_he4=analysis['gpa_tl_4']
    )
    
    if email_sent:
        messages.success(request, f'Đã gửi email cảnh báo sớm thành công đến {sv.ho_ten} ({sv.email}).')
    else:
        messages.warning(request, f'Đã ghi nhận lịch sử cảnh báo cho {sv.ho_ten}. Tuy nhiên, không thể gửi email thực tế do lỗi SMTP/hệ thống: {email_error}')

    return redirect('academic_warnings:canhbao_som_detail', mssv=mssv)


@login_required
def canhbao_som_gui_email_hang_loat(request):
    """Gửi email cảnh báo sớm hàng loạt dựa trên bộ lọc đang hoạt động."""
    if not (request.user.is_giaovu or request.user.is_admin):
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('dashboard:index')

    from results.utils import tinh_canh_bao_som, remove_accents
    from .models import LichSuGuiCanhBaoSom
    from django.core.mail import send_mail
    from django.conf import settings

    qs = SinhVien.objects.select_related('lop', 'nganh').all()
    if request.user.is_covan:
        qs = qs.filter(lop__covan=request.user)

    # Lấy lại các bộ lọc gửi lên từ form POST/GET
    khoa = request.GET.get('khoa', '') or request.POST.get('khoa', '')
    nganh_id = request.GET.get('nganh', '') or request.POST.get('nganh', '')
    lop_id = request.GET.get('lop', '') or request.POST.get('lop', '')
    khoa_hoc = request.GET.get('khoa_hoc', '') or request.POST.get('khoa_hoc', '')
    q = request.GET.get('q', '') or request.POST.get('q', '')
    muc_nguy_co_filter = request.GET.get('muc_nguy_co', '') or request.POST.get('muc_nguy_co', '')

    if khoa_hoc:
        cohort_suffix = khoa_hoc[-2:]
        qs = qs.filter(lop__ten_lop__istartswith=f'DA{cohort_suffix}')
    if khoa:
        qs = qs.filter(nganh__khoa=khoa)
    if nganh_id:
        qs = qs.filter(nganh_id=nganh_id)
    if lop_id:
        qs = qs.filter(lop_id=lop_id)
    if q:
        q_clean = remove_accents(q)
        qs = [
            sv for sv in qs
            if q_clean in remove_accents(sv.mssv)
            or q_clean in remove_accents(sv.ho_ten)
        ]

    success_count = 0
    errors = []

    student_list = list(qs)
    student_ids = [sv.id for sv in student_list]

    from results.models import KetQuaHocTap

    results_list = list(
        KetQuaHocTap.objects.filter(sinh_vien_id__in=student_ids, diem_tk__isnull=False)
        .select_related('mon_hoc', 'hoc_ky')
        .order_by('hoc_ky__nam_hoc', 'hoc_ky__ky')
    )
    prefetch_results = {}
    for r in results_list:
        if r.sinh_vien_id not in prefetch_results:
            prefetch_results[r.sinh_vien_id] = []
        prefetch_results[r.sinh_vien_id].append(r)

    warnings_list = list(CanhBaoHocVu.objects.filter(sinh_vien_id__in=student_ids))
    prefetch_warnings = {}
    for cb in warnings_list:
        prefetch_warnings[(cb.sinh_vien_id, cb.hoc_ky_id)] = cb

    latest_hk = HocKy.objects.filter(ket_qua__diem_tk__isnull=False).distinct().order_by('-nam_hoc', '-ky').first()
    if not latest_hk:
        latest_hk = HocKy.objects.order_by('-nam_hoc', '-ky').first()
    for sv in student_list:
        analysis = tinh_canh_bao_som(sv, hoc_ky=latest_hk, prefetch_results=prefetch_results, prefetch_warnings=prefetch_warnings)
        level = analysis['muc_nguy_co']

        # Chỉ gửi cho sinh viên khớp với bộ lọc mức nguy cơ (không gửi cho sinh viên An toàn nếu chỉ lọc Cảnh báo/Theo dõi)
        if muc_nguy_co_filter and level != muc_nguy_co_filter:
            continue
            
        # Không tự động gửi email cho sinh viên "An toàn" trong chế độ gửi hàng loạt
        if not muc_nguy_co_filter and level == 'safe':
            continue

        if not sv.email:
            continue

        subject = f'[TVU] Thông báo Cảnh báo sớm Học tập & Học vụ - Mức độ: {analysis["muc_nguy_co_display"]}'
        
        goi_y_str = ""
        if analysis['goi_y']:
            goi_y_str = "\nKhuyến nghị cải thiện:\n"
            for idx, gy in enumerate(analysis['goi_y'], 1):
                clean_gy = gy.replace('**', '')
                goi_y_str += f"{idx}. {clean_gy}\n"

        body = f"""Kính gửi Sinh viên {sv.ho_ten},

Hệ thống Quản lý Học vụ Trường Kỹ thuật và Công nghệ - Đại học Trà Vinh gửi thông báo phân tích kết quả học tập tính đến học kỳ {analysis['hoc_ky']}:

- Họ tên: {sv.ho_ten}
- Mã số sinh viên: {sv.mssv}
- Lớp: {sv.lop.ten_lop if sv.lop else '-'}
- Điểm trung bình học kỳ vừa qua: {analysis['gpa_hk_4']:.2f} (Hệ 4) / {analysis['gpa_hk_10']:.2f} (Hệ 10)
- Điểm trung bình tích lũy (GPA): {analysis['gpa_tl_4']:.2f} (Hệ 4) / {analysis['gpa_tl_10']:.2f} (Hệ 10)
- Tín chỉ tích lũy: {analysis['tc_tl_pass']}/{analysis['tc_tl_reg']} TC
- Xu hướng học tập: {analysis['xu_huong_display']}

---
MỨC ĐỘ NGUY CƠ HỌC VỤ: {analysis['muc_nguy_co_display']}
Chi tiết phân tích: {analysis['ly_do']}
---
{goi_y_str}
Chúc bạn sớm cải thiện được kết quả học tập của mình. Nếu cần thêm hỗ trợ, vui lòng chủ động đặt lịch hẹn để trao đổi thêm với Cố vấn học tập của lớp.

Trân trọng,
Giáo vụ Trường Kỹ thuật và Công nghệ
"""

        email_sent = False
        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL or 'giaovu@tvu.edu.vn',
                [sv.email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            errors.append(f"{sv.ho_ten} (Lỗi SMTP: {e})")
            
        # Vẫn lưu lịch sử gửi email để phục vụ demo/kiểm thử khi thiếu SMTP
        LichSuGuiCanhBaoSom.objects.create(
            sinh_vien=sv,
            hoc_ky=analysis['hoc_ky'],
            muc_nguy_co=analysis['muc_nguy_co_display'],
            gpa_he4=analysis['gpa_tl_4']
        )
        success_count += 1

    actual_sent_count = success_count - len(errors)
    if actual_sent_count > 0:
        messages.success(request, f'Đã gửi email cảnh báo sớm thành công đến {actual_sent_count} sinh viên.')
    if errors:
        messages.warning(request, f'Đã ghi nhận lịch sử cảnh báo cho {len(errors)} sinh viên nhưng không gửi được email thực tế: {", ".join(errors[:5])}')

    return redirect('academic_warnings:canhbao_som_list')

