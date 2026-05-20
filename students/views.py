import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
import openpyxl
from .models import SinhVien, MonHoc, HocKy, Nganh
from .forms import SinhVienForm, MonHocForm, HocKyForm, NganhForm, ImportCSVForm


def role_required(*roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles and not request.user.is_admin:
                messages.error(request, 'Bạn không có quyền truy cập.')
                return redirect('dashboard:index')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ---- Sinh viên ----
@login_required
def sinhvien_list(request):
    qs = SinhVien.objects.select_related('nganh', 'covan').all()
    q = request.GET.get('q', '')
    trang_thai = request.GET.get('trang_thai', '')
    nganh_id = request.GET.get('nganh', '')

    if request.user.is_sinhvien:
        try:
            qs = qs.filter(user=request.user)
        except Exception:
            qs = qs.none()
    elif request.user.is_covan:
        qs = qs.filter(lop__covan=request.user)

    if q:
        qs = qs.filter(Q(mssv__icontains=q) | Q(ho_ten__icontains=q) | Q(lop__ten_lop__icontains=q))
    if trang_thai:
        qs = qs.filter(trang_thai=trang_thai)
    if nganh_id:
        qs = qs.filter(nganh_id=nganh_id)

    nganhs = Nganh.objects.all()
    return render(request, 'students/sinhvien_list.html', {
        'sinhviens': qs, 'nganhs': nganhs, 'q': q,
        'trang_thai': trang_thai, 'nganh_id': nganh_id,
    })


@login_required
def sinhvien_detail(request, pk):
    sv = get_object_or_404(SinhVien, pk=pk)
    if request.user.is_sinhvien:
        linked_sv = SinhVien.objects.filter(user=request.user).first()
        if linked_sv is None or linked_sv.pk != sv.pk:
            messages.error(request, 'Bạn không có quyền xem thông tin này.')
            return redirect('dashboard:index')

    from results.models import KetQuaHocTap
    from academic_warnings.models import CanhBaoHocVu
    from results.utils import tinh_dtbchk, tinh_dtbctl, la_dat, diem_he4
    from collections import OrderedDict

    canh_baos = CanhBaoHocVu.objects.filter(sinh_vien=sv).order_by('-ngay_tao')

    # Tổ chức kết quả theo năm học → học kỳ
    ket_qua_all = KetQuaHocTap.objects.filter(sinh_vien=sv).select_related(
        'mon_hoc', 'hoc_ky').order_by('hoc_ky__nam_hoc', 'hoc_ky__ky', 'mon_hoc__ten_mh')

    ket_qua_theo_nam = OrderedDict()
    for kq in ket_qua_all:
        nam = kq.hoc_ky.nam_hoc
        hk_ten = str(kq.hoc_ky)
        if nam not in ket_qua_theo_nam:
            ket_qua_theo_nam[nam] = OrderedDict()
        if hk_ten not in ket_qua_theo_nam[nam]:
            ket_qua_theo_nam[nam][hk_ten] = {'ket_qua': [], 'tong_mon': 0,
                                               'tc_dang_ky': 0, 'tc_dat': 0, 'dtbchk': 0.0}
        ket_qua_theo_nam[nam][hk_ten]['ket_qua'].append(kq)

    # Tính thống kê từng học kỳ
    for nam, hk_dict in ket_qua_theo_nam.items():
        for hk_ten, data in hk_dict.items():
            kqs = data['ket_qua']
            data['tong_mon'] = len(kqs)
            data['tc_dang_ky'] = sum(k.mon_hoc.so_tc for k in kqs)
            data['tc_dat'] = sum(k.mon_hoc.so_tc for k in kqs if la_dat(k.diem_tk))
            tong_tc = sum(k.mon_hoc.so_tc for k in kqs if k.diem_tk is not None)
            tong_diem_10 = sum(k.diem_tk * k.mon_hoc.so_tc for k in kqs if k.diem_tk is not None)
            tong_diem_4  = sum((diem_he4(k.diem_tk) or 0) * k.mon_hoc.so_tc for k in kqs if k.diem_tk is not None)
            data['dtbchk']   = round(tong_diem_10 / tong_tc, 2) if tong_tc > 0 else 0.0
            data['dtbchk_4'] = round(tong_diem_4  / tong_tc, 2) if tong_tc > 0 else 0.0

    # Tổng hợp toàn khóa
    dtbctl_10, dtbctl_4, tc_tl, tc_da_hoc = tinh_dtbctl(sv)

    # Tính điểm tích lũy từng năm học (TB cộng ĐTBCHK các HK trong năm)
    dtb_theo_nam = {}
    for nam_hoc, hk_dict in ket_qua_theo_nam.items():
        hk_dtb_10 = [d['dtbchk'] for d in hk_dict.values() if d['dtbchk'] > 0]
        hk_dtb_4  = [d['dtbchk_4'] for d in hk_dict.values() if d['dtbchk_4'] > 0]
        tc_nam = sum(d['tc_dang_ky'] for d in hk_dict.values())
        tc_dat_nam = sum(d['tc_dat'] for d in hk_dict.values())
        dtb_theo_nam[nam_hoc] = {
            'dtb_10': round(sum(hk_dtb_10) / len(hk_dtb_10), 2) if hk_dtb_10 else 0.0,
            'dtb_4':  round(sum(hk_dtb_4)  / len(hk_dtb_4),  2) if hk_dtb_4  else 0.0,
            'tc_dang_ky': tc_nam,
            'tc_dat': tc_dat_nam,
        }

    # Điểm tích lũy toàn khóa = TB cộng ĐTBCHK tất cả HK
    all_dtb_10 = [d['dtbchk'] for nam in ket_qua_theo_nam.values()
                  for d in nam.values() if d['dtbchk'] > 0]
    all_dtb_4  = [d['dtbchk_4'] for nam in ket_qua_theo_nam.values()
                  for d in nam.values() if d['dtbchk_4'] > 0]
    toan_khoa_dtb_10 = round(sum(all_dtb_10) / len(all_dtb_10), 2) if all_dtb_10 else 0.0
    toan_khoa_dtb_4  = round(sum(all_dtb_4)  / len(all_dtb_4),  2) if all_dtb_4  else 0.0

    return render(request, 'students/sinhvien_detail.html', {
        'sv': sv,
        'canh_baos': canh_baos,
        'ket_qua_theo_nam': ket_qua_theo_nam,
        'dtb_theo_nam': dtb_theo_nam,
        'dtbctl_10': dtbctl_10,
        'dtbctl_4': dtbctl_4,
        'tc_tl': tc_tl,
        'tc_da_hoc': tc_da_hoc,
        'toan_khoa_dtb_10': toan_khoa_dtb_10,
        'toan_khoa_dtb_4': toan_khoa_dtb_4,
    })


@login_required
@role_required('giaovu', 'admin')
def sinhvien_create(request):
    form = SinhVienForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Thêm sinh viên thành công.')
        return redirect('students:sinhvien_list')
    return render(request, 'students/sinhvien_form.html', {'form': form, 'title': 'Thêm sinh viên'})


@login_required
@role_required('giaovu', 'admin')
def sinhvien_edit(request, pk):
    sv = get_object_or_404(SinhVien, pk=pk)
    form = SinhVienForm(request.POST or None, instance=sv)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cập nhật sinh viên thành công.')
        return redirect('students:sinhvien_list')
    return render(request, 'students/sinhvien_form.html', {'form': form, 'title': 'Chỉnh sửa sinh viên'})


@login_required
@role_required('giaovu', 'admin')
def sinhvien_delete(request, pk):
    sv = get_object_or_404(SinhVien, pk=pk)
    if request.method == 'POST':
        sv.delete()
        messages.success(request, 'Xóa sinh viên thành công.')
        return redirect('students:sinhvien_list')
    return render(request, 'students/confirm_delete.html', {'obj': sv, 'title': 'Xóa sinh viên'})


# ---- Môn học ----
@login_required
def monhoc_list(request):
    qs = MonHoc.objects.all()
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(ma_mh__icontains=q) | Q(ten_mh__icontains=q))
    return render(request, 'students/monhoc_list.html', {'monhocs': qs, 'q': q})


@login_required
@role_required('giaovu', 'admin')
def monhoc_create(request):
    form = MonHocForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Thêm môn học thành công.')
        return redirect('students:monhoc_list')
    return render(request, 'students/monhoc_form.html', {'form': form, 'title': 'Thêm môn học'})


@login_required
@role_required('giaovu', 'admin')
def monhoc_edit(request, pk):
    mh = get_object_or_404(MonHoc, pk=pk)
    form = MonHocForm(request.POST or None, instance=mh)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cập nhật môn học thành công.')
        return redirect('students:monhoc_list')
    return render(request, 'students/monhoc_form.html', {'form': form, 'title': 'Chỉnh sửa môn học'})


@login_required
@role_required('giaovu', 'admin')
def monhoc_delete(request, pk):
    mh = get_object_or_404(MonHoc, pk=pk)
    if request.method == 'POST':
        mh.delete()
        messages.success(request, 'Xóa môn học thành công.')
        return redirect('students:monhoc_list')
    return render(request, 'students/confirm_delete.html', {'obj': mh, 'title': 'Xóa môn học'})


# ---- Học kỳ ----
@login_required
def hocky_list(request):
    hockys = HocKy.objects.all()
    return render(request, 'students/hocky_list.html', {'hockys': hockys})


@login_required
@role_required('giaovu', 'admin')
def hocky_create(request):
    form = HocKyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Thêm học kỳ thành công.')
        return redirect('students:hocky_list')
    return render(request, 'students/hocky_form.html', {'form': form, 'title': 'Thêm học kỳ'})


@login_required
@role_required('giaovu', 'admin')
def hocky_edit(request, pk):
    hk = get_object_or_404(HocKy, pk=pk)
    form = HocKyForm(request.POST or None, instance=hk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cập nhật học kỳ thành công.')
        return redirect('students:hocky_list')
    return render(request, 'students/hocky_form.html', {'form': form, 'title': 'Chỉnh sửa học kỳ'})


# ---- Import CSV ----
@login_required
@role_required('giaovu', 'admin')
def import_sinhvien(request):
    form = ImportCSVForm(request.POST or None, request.FILES or None)
    errors = []
    if request.method == 'POST' and form.is_valid():
        f = request.FILES['file']
        name = f.name.lower()
        count = 0
        try:
            if name.endswith('.csv'):
                decoded = f.read().decode('utf-8-sig')
                reader = csv.DictReader(io.StringIO(decoded))
                for row in reader:
                    try:
                        nganh, _ = Nganh.objects.get_or_create(
                            ma_nganh=row.get('ma_nganh', 'KT'),
                            defaults={'ten_nganh': row.get('ten_nganh', 'Chưa xác định')}
                        )
                        SinhVien.objects.update_or_create(
                            mssv=row['mssv'],
                            defaults={
                                'ho_ten': row.get('ho_ten', ''),
                                'email': row.get('email', ''),
                                'khoa': row.get('khoa', ''),
                                'lop': row.get('lop', ''),
                                'nganh': nganh,
                                'trang_thai': row.get('trang_thai', 'dang_hoc'),
                            }
                        )
                        count += 1
                    except Exception as e:
                        errors.append(f"Dòng {row}: {e}")
            elif name.endswith(('.xlsx', '.xls')):
                wb = openpyxl.load_workbook(f)
                ws = wb.active
                headers = [cell.value for cell in ws[1]]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    data = dict(zip(headers, row))
                    if not data.get('mssv'):
                        continue
                    try:
                        nganh, _ = Nganh.objects.get_or_create(
                            ma_nganh=data.get('ma_nganh', 'KT'),
                            defaults={'ten_nganh': data.get('ten_nganh', 'Chưa xác định')}
                        )
                        SinhVien.objects.update_or_create(
                            mssv=str(data['mssv']),
                            defaults={
                                'ho_ten': data.get('ho_ten', ''),
                                'email': data.get('email', '') or '',
                                'khoa': str(data.get('khoa', '')),
                                'lop': data.get('lop', '') or '',
                                'nganh': nganh,
                                'trang_thai': data.get('trang_thai', 'dang_hoc') or 'dang_hoc',
                            }
                        )
                        count += 1
                    except Exception as e:
                        errors.append(f"Dòng {data}: {e}")
            messages.success(request, f'Import thành công {count} sinh viên.')
            if errors:
                messages.warning(request, f'{len(errors)} dòng lỗi: ' + '; '.join(errors[:5]))
            return redirect('students:sinhvien_list')
        except Exception as e:
            messages.error(request, f'Lỗi đọc file: {e}')
    return render(request, 'students/import.html', {'form': form, 'title': 'Import sinh viên', 'errors': errors})


# ---- Export Excel ----
@login_required
def export_sinhvien(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Sinh viên'
    headers = ['MSSV', 'Họ tên', 'Email', 'Ngành', 'Khóa', 'Lớp', 'Trạng thái']
    ws.append(headers)
    for sv in SinhVien.objects.select_related('nganh').all():
        ws.append([sv.mssv, sv.ho_ten, sv.email,
                   sv.nganh.ten_nganh if sv.nganh else '',
                   sv.khoa, sv.lop, sv.get_trang_thai_display()])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="sinh_vien.xlsx"'
    wb.save(response)
    return response
