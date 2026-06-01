import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
import openpyxl
from .models import KetQuaHocTap
from .forms import KetQuaForm, ImportDiemForm, FilterKetQuaForm
from .utils import tinh_dtbctl, tinh_dtbchk, get_phan_phoi_diem, kiem_tra_canh_bao, dem_canh_bao_lien_tiep, xac_dinh_muc_canh_bao, dong_bo_canh_bao_sinh_vien
from students.models import SinhVien, MonHoc, HocKy
from academic_warnings.models import CanhBaoHocVu


def _xu_ly_canh_bao(sv, hoc_ky):
    """Kiểm tra và lưu cảnh báo học vụ sau khi nhập/sửa điểm."""
    dong_bo_canh_bao_sinh_vien(sv)


@login_required
def ketqua_list(request):
    from collections import OrderedDict
    from results.utils import la_dat, diem_he4 as _diem_he4

    # --- Lọc cơ bản: chỉ lấy lần học 1 để hiển thị ---
    qs = KetQuaHocTap.objects.select_related(
        'sinh_vien', 'sinh_vien__lop', 'mon_hoc', 'hoc_ky'
    ).filter(lan_hoc=1)

    if request.user.is_sinhvien:
        sv = SinhVien.objects.filter(user=request.user).first()
        qs = qs.filter(sinh_vien=sv) if sv else qs.none()
    elif request.user.is_covan:
        qs = qs.filter(sinh_vien__lop__covan=request.user)

    # Lọc học kỳ (dùng chung cho cả 2 chế độ)
    hoc_ky_filter = request.GET.get('hoc_ky', '')
    if hoc_ky_filter:
        qs = qs.filter(hoc_ky_id=hoc_ky_filter)

    # Lọc điểm hệ 4 (chỉ cho cố vấn/giáo vụ)
    he4_filter = request.GET.get('he4', '')

    # Lọc phân cấp thông minh cho giáo vụ / admin
    khoa = request.GET.get('khoa', '')
    nganh_id = request.GET.get('nganh', '')
    lop_id = request.GET.get('lop', '')

    if not request.user.is_sinhvien and not request.user.is_covan:
        if khoa:
            qs = qs.filter(sinh_vien__nganh__khoa=khoa)
        if nganh_id:
            qs = qs.filter(sinh_vien__nganh_id=nganh_id)
        if lop_id:
            qs = qs.filter(sinh_vien__lop_id=lop_id)

    hockys = HocKy.objects.all().order_by('-nam_hoc', '-ky')

    # ================================================================
    # CHẾ ĐỘ SINH VIÊN: hiển thị điểm từng môn theo năm → HK (giảm dần)
    # ================================================================
    if request.user.is_sinhvien:
        # Nhóm theo năm (giảm dần) → HK → [kết quả]
        theo_nam = OrderedDict()
        for kq in qs.order_by('-hoc_ky__nam_hoc', '-hoc_ky__ky', 'mon_hoc__ten_mh'):
            nam = kq.hoc_ky.nam_hoc
            hk_ten = str(kq.hoc_ky)
            if nam not in theo_nam:
                theo_nam[nam] = OrderedDict()
            if hk_ten not in theo_nam[nam]:
                theo_nam[nam][hk_ten] = {'ket_qua': [], 'dtbchk_10': 0.0, 'dtbchk_4': 0.0,
                                          'tc_dang_ky': 0, 'tc_dat': 0}
            theo_nam[nam][hk_ten]['ket_qua'].append(kq)

        # Tính ĐTBCHK từng HK và tổng kết từng năm
        all_dtb_10 = []
        all_dtb_4  = []
        for nam, hk_dict in theo_nam.items():
            nam_dtb_10 = []
            nam_dtb_4  = []
            for hk_ten, data in hk_dict.items():
                kqs = data['ket_qua']
                tong_tc = sum(k.mon_hoc.so_tc for k in kqs if k.diem_tk is not None)
                if tong_tc > 0:
                    d10 = round(sum(k.diem_tk * k.mon_hoc.so_tc for k in kqs if k.diem_tk is not None) / tong_tc, 2)
                    d4  = round(sum((_diem_he4(k.diem_tk) or 0) * k.mon_hoc.so_tc for k in kqs if k.diem_tk is not None) / tong_tc, 2)
                else:
                    d10 = d4 = 0.0
                data['dtbchk_10']  = d10
                data['dtbchk_4']   = d4
                data['tc_dang_ky'] = tong_tc
                data['tc_dat']     = sum(k.mon_hoc.so_tc for k in kqs if la_dat(k.diem_tk))
                if d10 > 0:
                    nam_dtb_10.append(d10)
                    nam_dtb_4.append(d4)
                    all_dtb_10.append(d10)
                    all_dtb_4.append(d4)
            # Tổng kết năm = TB cộng các HK trong năm
            theo_nam[nam]['tong_ket'] = {
                'dtb_10': round(sum(nam_dtb_10) / len(nam_dtb_10), 2) if nam_dtb_10 else 0.0,
                'dtb_4':  round(sum(nam_dtb_4)  / len(nam_dtb_4),  2) if nam_dtb_4  else 0.0,
                'tc_dang_ky': sum(d['tc_dang_ky'] for k, d in hk_dict.items() if isinstance(d, dict) and 'tc_dang_ky' in d),
                'tc_dat':     sum(d['tc_dat']     for k, d in hk_dict.items() if isinstance(d, dict) and 'tc_dat' in d),
            }

        # Tổng kết toàn khóa = TB cộng tất cả HK
        toan_khoa = {
            'dtb_10': round(sum(all_dtb_10) / len(all_dtb_10), 2) if all_dtb_10 else 0.0,
            'dtb_4':  round(sum(all_dtb_4)  / len(all_dtb_4),  2) if all_dtb_4  else 0.0,
        }
        # TC tích lũy (dùng tinh_dtbctl)
        if sv:
            from results.utils import tinh_dtbctl
            _, _, tc_tl, _ = tinh_dtbctl(sv)
            toan_khoa['tc_tl'] = tc_tl

        return render(request, 'results/ketqua_list.html', {
            'theo_nam_sv': theo_nam,
            'toan_khoa': toan_khoa,
            'hockys': hockys,
            'hoc_ky_filter': hoc_ky_filter,
            'is_sinhvien': True,
        })

    # ================================================================
    # CHẾ ĐỘ CỐ VẤN / GIÁO VỤ / ADMIN:
    # Hiển thị tổng hợp theo lớp → năm (giảm dần) → HK → sinh viên + điểm HK
    # ================================================================

    # Tính ĐTBCHK cho từng (sinh_vien, hoc_ky)
    # Nhóm: lớp → năm → HK → sv → [kết quả]
    raw = OrderedDict()
    for kq in qs.order_by(
        'sinh_vien__lop__ten_lop', '-hoc_ky__nam_hoc', '-hoc_ky__ky', 'sinh_vien__mssv'
    ):
        ten_lop = kq.sinh_vien.lop.ten_lop if kq.sinh_vien.lop else 'Chưa xếp lớp'
        nam = kq.hoc_ky.nam_hoc
        hk_ten = str(kq.hoc_ky)
        sv_key = kq.sinh_vien.pk

        raw.setdefault(ten_lop, OrderedDict())
        raw[ten_lop].setdefault(nam, OrderedDict())
        raw[ten_lop][nam].setdefault(hk_ten, OrderedDict())
        raw[ten_lop][nam][hk_ten].setdefault(sv_key, {
            'sv': kq.sinh_vien, 'ket_qua': []
        })
        raw[ten_lop][nam][hk_ten][sv_key]['ket_qua'].append(kq)

    # Tính ĐTBCHK hệ 10 và hệ 4 cho từng SV-HK, áp dụng lọc he4
    theo_lop = OrderedDict()
    for ten_lop, theo_nam in raw.items():
        for nam, theo_hk in theo_nam.items():
            for hk_ten, sv_dict in theo_hk.items():
                rows = []
                for sv_key, data in sv_dict.items():
                    kqs = data['ket_qua']
                    tong_tc = sum(k.mon_hoc.so_tc for k in kqs if k.diem_tk is not None)
                    if tong_tc == 0:
                        dtbchk_10 = dtbchk_4 = 0.0
                    else:
                        dtbchk_10 = round(sum(k.diem_tk * k.mon_hoc.so_tc for k in kqs if k.diem_tk is not None) / tong_tc, 2)
                        dtbchk_4  = round(sum((_diem_he4(k.diem_tk) or 0) * k.mon_hoc.so_tc for k in kqs if k.diem_tk is not None) / tong_tc, 2)
                    tc_dat = sum(k.mon_hoc.so_tc for k in kqs if la_dat(k.diem_tk))

                    # Áp dụng lọc điểm hệ 4
                    if he4_filter:
                        try:
                            he4_val = float(he4_filter)
                            if dtbchk_4 < he4_val:
                                continue
                        except ValueError:
                            pass

                    rows.append({
                        'sv': data['sv'],
                        'dtbchk_10': dtbchk_10,
                        'dtbchk_4': dtbchk_4,
                        'tc_dang_ky': tong_tc,
                        'tc_dat': tc_dat,
                        'so_mon': len(kqs),
                    })

                if not rows:
                    continue
                theo_lop.setdefault(ten_lop, OrderedDict())
                theo_lop[ten_lop].setdefault(nam, OrderedDict())
                theo_lop[ten_lop][nam][hk_ten] = rows

    # Dữ liệu cho bộ lọc phân cấp (để hiển thị dropdown)
    from students.models import Nganh
    nganhs = Nganh.objects.all()
    khoas = Nganh.objects.values_list('khoa', flat=True).distinct()
    lops = []
    if nganh_id:
        from students.models import Lop
        lops = Lop.objects.filter(nganh_id=nganh_id)
    if khoa:
        nganhs = nganhs.filter(khoa=khoa)

    return render(request, 'results/ketqua_list.html', {
        'theo_lop': theo_lop,
        'hockys': hockys,
        'hoc_ky_filter': hoc_ky_filter,
        'he4_filter': he4_filter,
        'is_sinhvien': False,
        'nganhs': nganhs,
        'khoas': khoas,
        'lops': lops,
        'selected_khoa': khoa,
        'nganh_id': nganh_id,
        'selected_lop': lop_id,
    })


def _nhom_theo_nam_hk(qs):
    """Nhóm queryset theo năm học giảm dần → học kỳ."""
    from collections import OrderedDict
    result = OrderedDict()
    for kq in qs.order_by('-hoc_ky__nam_hoc', '-hoc_ky__ky', 'mon_hoc__ten_mh'):
        nam = kq.hoc_ky.nam_hoc
        hk_ten = str(kq.hoc_ky)
        if nam not in result:
            result[nam] = OrderedDict()
        if hk_ten not in result[nam]:
            result[nam][hk_ten] = []
        result[nam][hk_ten].append(kq)
    return result

@login_required
def ketqua_create(request):
    if request.user.is_sinhvien or request.user.is_covan:
        messages.error(request, 'Bạn không có quyền nhập điểm.')
        return redirect('results:ketqua_list')
    form = KetQuaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        kq = form.save()
        _xu_ly_canh_bao(kq.sinh_vien, kq.hoc_ky)
        messages.success(request, 'Nhập điểm thành công.')
        return redirect('results:ketqua_list')
    return render(request, 'results/ketqua_form.html', {'form': form, 'title': 'Nhập điểm'})


@login_required
def ketqua_edit(request, pk):
    if request.user.is_sinhvien or request.user.is_covan:
        messages.error(request, 'Bạn không có quyền sửa điểm.')
        return redirect('results:ketqua_list')
    kq = get_object_or_404(KetQuaHocTap, pk=pk)
    form = KetQuaForm(request.POST or None, instance=kq)
    if request.method == 'POST' and form.is_valid():
        kq = form.save()
        _xu_ly_canh_bao(kq.sinh_vien, kq.hoc_ky)
        messages.success(request, 'Cập nhật điểm thành công.')
        return redirect('results:ketqua_list')
    return render(request, 'results/ketqua_form.html', {'form': form, 'title': 'Sửa điểm'})


@login_required
def ketqua_delete(request, pk):
    if request.user.is_sinhvien or request.user.is_covan:
        messages.error(request, 'Bạn không có quyền xóa điểm.')
        return redirect('results:ketqua_list')
    kq = get_object_or_404(KetQuaHocTap, pk=pk)
    if request.method == 'POST':
        sv = kq.sinh_vien
        kq.delete()
        _xu_ly_canh_bao(sv, None)
        messages.success(request, 'Xóa kết quả thành công.')
        return redirect('results:ketqua_list')
    return render(request, 'students/confirm_delete.html', {'obj': kq, 'title': 'Xóa kết quả'})


@login_required
def import_diem(request):
    if request.user.is_sinhvien or request.user.is_covan:
        messages.error(request, 'Bạn không có quyền import điểm.')
        return redirect('results:ketqua_list')
    form = ImportDiemForm(request.POST or None, request.FILES or None)
    errors = []
    if request.method == 'POST' and form.is_valid():
        hoc_ky = form.cleaned_data['hoc_ky']
        f = request.FILES['file']
        count = 0
        try:
            if f.name.lower().endswith('.csv'):
                decoded = f.read().decode('utf-8-sig')
                reader = csv.DictReader(io.StringIO(decoded))
                rows = list(reader)
            else:
                wb = openpyxl.load_workbook(f)
                ws = wb.active
                headers = [cell.value for cell in ws[1]]
                rows = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]

            for row in rows:
                if not row:
                    continue
                mssv_val = row.get('mssv')
                ma_mh_val = row.get('ma_mh')
                if mssv_val is None or ma_mh_val is None:
                    continue
                mssv = str(mssv_val).strip()
                ma_mh = str(ma_mh_val).strip()
                if not mssv or mssv.lower() == 'none' or not ma_mh or ma_mh.lower() == 'none':
                    continue
                try:
                    sv = SinhVien.objects.get(mssv=mssv)
                    mh = MonHoc.objects.get(ma_mh=ma_mh)
                    diem_qt  = float(row['diem_qt'])  if row.get('diem_qt')  not in (None, '', 'None') else None
                    diem_thi = float(row['diem_thi']) if row.get('diem_thi') not in (None, '', 'None') else None
                    diem_tk  = float(row['diem_tk'])  if row.get('diem_tk')  not in (None, '', 'None') else None
                    KetQuaHocTap.objects.update_or_create(
                        sinh_vien=sv, mon_hoc=mh, hoc_ky=hoc_ky,
                        lan_hoc=int(row.get('lan_hoc', 1) or 1),
                        defaults={'diem_qt': diem_qt, 'diem_thi': diem_thi, 'diem_tk': diem_tk}
                    )
                    count += 1
                except Exception as e:
                    errors.append(f"{row}: {e}")

            # Kiểm tra cảnh báo cho tất cả SV trong HK sau khi import xong
            for sv in SinhVien.objects.filter(ket_qua__hoc_ky=hoc_ky).distinct():
                _xu_ly_canh_bao(sv, hoc_ky)

            messages.success(request, f'Import thành công {count} kết quả.')
            if errors:
                messages.warning(request, f'{len(errors)} lỗi: ' + '; '.join(errors[:5]))
            return redirect('results:ketqua_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')
    return render(request, 'results/import_diem.html', {'form': form, 'errors': errors})


@login_required
def export_diem(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Kết quả học tập'
    ws.append(['MSSV', 'Họ tên', 'Môn học', 'Số TC', 'Học kỳ',
               'Điểm QT', 'Điểm thi', 'Điểm TK', 'Điểm chữ', 'Hệ 4', 'Lần học'])
    qs = KetQuaHocTap.objects.select_related('sinh_vien', 'mon_hoc', 'hoc_ky').all()
    if request.user.is_sinhvien:
        qs = qs.filter(sinh_vien__user=request.user)
    elif request.user.is_covan:
        qs = qs.filter(sinh_vien__lop__covan=request.user)
    for kq in qs:
        ws.append([kq.sinh_vien.mssv, kq.sinh_vien.ho_ten, kq.mon_hoc.ten_mh,
                   kq.mon_hoc.so_tc, str(kq.hoc_ky),
                   kq.diem_qt, kq.diem_thi, kq.diem_tk, kq.diem_chu, kq.diem_he4, kq.lan_hoc])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="ket_qua_hoc_tap.xlsx"'
    wb.save(response)
    return response


@login_required
def api_gpa_chart(request, sv_id):
    sv = get_object_or_404(SinhVien, pk=sv_id)
    hockys = HocKy.objects.filter(ket_qua__sinh_vien=sv).distinct().order_by('nam_hoc', 'ky')
    labels, gpas = [], []
    for hk in hockys:
        dtbchk, tc = tinh_dtbchk(sv, hk)
        if tc > 0:
            labels.append(str(hk))
            gpas.append(dtbchk)
    return JsonResponse({'labels': labels, 'gpas': gpas})
