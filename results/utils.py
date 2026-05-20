"""
Các hàm tính toán điểm và cảnh báo học vụ - Đại học Trà Vinh.

Thang điểm môn học (hệ 10 → chữ → hệ 4):
  9.0 - 10.0 → A  → 4.0
  8.0 -  8.9 → B+ → 3.5
  7.0 -  7.9 → B  → 3.0
  6.5 -  6.9 → C+ → 2.5
  5.5 -  6.4 → C  → 2.0
  5.0 -  5.4 → D+ → 1.5
  4.0 -  4.9 → D  → 1.0
  < 4.0      → F  → 0.0

Học phần đạt: điểm >= 4.0 (từ D trở lên).

Công thức điểm tổng kết môn: ĐTgK = (ĐTBQT + ĐKT) / 2

Điểm trung bình HK / tích lũy: trung bình có trọng số (số TC),
  bao gồm TẤT CẢ học phần (kể cả F).

Điều kiện cảnh báo học vụ (lớp tín chỉ) - vi phạm 1 trong 4:
  a) TC không đạt trong HK > 50% TC đăng ký HK,
     HOẶC TC nợ đọng từ đầu khóa > 24 TC
  b) ĐTBCHK < 0.80 (HK đầu khóa) hoặc < 1.00 (HK tiếp theo)
  c) ĐTBCTL < 1.20 (năm 1) / 1.40 (năm 2) / 1.60 (năm 3) / 1.80 (năm 4+)
  d) Không đăng ký học trong HK chính mà không được phép

Buộc thôi học: số lần cảnh báo liên tiếp > 2 lần.
"""


# ─── Thang điểm môn học ────────────────────────────────────────────────────

def diem_chu(diem_10):
    """Chuyển điểm hệ 10 → điểm chữ theo bảng quy chế TVU."""
    if diem_10 is None:
        return None
    if diem_10 >= 9.0:  return 'A'
    if diem_10 >= 8.0:  return 'B+'
    if diem_10 >= 7.0:  return 'B'
    if diem_10 >= 6.5:  return 'C+'
    if diem_10 >= 5.5:  return 'C'
    if diem_10 >= 5.0:  return 'D+'
    if diem_10 >= 4.0:  return 'D'
    return 'F'


def diem_he4(diem_10):
    """Chuyển điểm hệ 10 → hệ 4 theo bảng quy chế TVU."""
    if diem_10 is None:
        return None
    if diem_10 >= 9.0:  return 4.0
    if diem_10 >= 8.0:  return 3.5
    if diem_10 >= 7.0:  return 3.0
    if diem_10 >= 6.5:  return 2.5
    if diem_10 >= 5.5:  return 2.0
    if diem_10 >= 5.0:  return 1.5
    if diem_10 >= 4.0:  return 1.0
    return 0.0


def xep_loai_hoc_luc(diem_10):
    """Xếp loại học lực theo điểm hệ 10."""
    chu = diem_chu(diem_10)
    return {
        'A': 'Xuất sắc', 'B+': 'Giỏi', 'B': 'Khá',
        'C+': 'Trung bình khá', 'C': 'Trung bình',
        'D+': 'Trung bình yếu', 'D': 'Yếu',
        'F': 'Kém'
    }.get(chu, '')


def la_dat(diem_10):
    """Học phần đạt khi điểm >= 4.0 (từ D trở lên)."""
    return diem_10 is not None and diem_10 >= 4.0


# ─── Tính điểm trung bình ──────────────────────────────────────────────────

def tinh_dtbchk(sinh_vien, hoc_ky):
    """
    Tính ĐTBCHK hệ 10 = Σ(điểm_i × TC_i) / Σ(TC_i).
    Tính ĐTBCHK hệ 4  = Σ(diem_he4_i × TC_i) / Σ(TC_i).
    Bao gồm TẤT CẢ học phần trong HK (kể cả F).
    Trả về (dtbchk_10, dtbchk_4, tong_tc_hk, tc_dat_hk).
    """
    from results.models import KetQuaHocTap
    ket_qua = KetQuaHocTap.objects.filter(
        sinh_vien=sinh_vien, hoc_ky=hoc_ky, diem_tk__isnull=False
    ).select_related('mon_hoc')

    tong_tc = 0
    tong_diem_10 = 0.0
    tong_diem_4 = 0.0
    tc_dat = 0
    for kq in ket_qua:
        tc = kq.mon_hoc.so_tc
        tong_tc += tc
        tong_diem_10 += (kq.diem_tk or 0) * tc
        tong_diem_4  += (diem_he4(kq.diem_tk) or 0) * tc
        if la_dat(kq.diem_tk):
            tc_dat += tc

    if tong_tc == 0:
        return 0.0, 0.0, 0, 0
    return (round(tong_diem_10 / tong_tc, 2),
            round(tong_diem_4  / tong_tc, 2),
            tong_tc, tc_dat)


def tinh_dtbctl(sinh_vien):
    """
    Tính ĐTBCTL hệ 10 và hệ 4 (lấy điểm tốt nhất mỗi môn, trọng số TC, kể cả F).
    Trả về (dtbctl_10, dtbctl_4, tc_tich_luy, tong_tc_da_hoc).
    """
    from results.models import KetQuaHocTap

    mon_ids = KetQuaHocTap.objects.filter(
        sinh_vien=sinh_vien, diem_tk__isnull=False
    ).values_list('mon_hoc_id', flat=True).distinct()

    tong_tc = 0
    tong_diem_10 = 0.0
    tong_diem_4  = 0.0
    tc_tich_luy  = 0

    for mon_id in mon_ids:
        best = KetQuaHocTap.objects.filter(
            sinh_vien=sinh_vien, mon_hoc_id=mon_id, diem_tk__isnull=False
        ).order_by('-diem_tk').first()
        if best:
            tc = best.mon_hoc.so_tc
            tong_tc += tc
            tong_diem_10 += (best.diem_tk or 0) * tc
            tong_diem_4  += (diem_he4(best.diem_tk) or 0) * tc
            if la_dat(best.diem_tk):
                tc_tich_luy += tc

    dtbctl_10 = round(tong_diem_10 / tong_tc, 2) if tong_tc > 0 else 0.0
    dtbctl_4  = round(tong_diem_4  / tong_tc, 2) if tong_tc > 0 else 0.0
    return dtbctl_10, dtbctl_4, tc_tich_luy, tong_tc


# ─── Các hàm hỗ trợ cảnh báo ──────────────────────────────────────────────

def tinh_tc_khong_dat_hk(sinh_vien, hoc_ky):
    """Tổng TC học phần không đạt (điểm F) trong HK."""
    from results.models import KetQuaHocTap
    ket_qua = KetQuaHocTap.objects.filter(
        sinh_vien=sinh_vien, hoc_ky=hoc_ky, diem_tk__isnull=False
    ).select_related('mon_hoc')
    return sum(kq.mon_hoc.so_tc for kq in ket_qua if not la_dat(kq.diem_tk))


def tinh_tc_no_dong(sinh_vien):
    """
    Tổng TC nợ đọng từ đầu khóa = TC các môn chưa đạt (điểm F tốt nhất).
    Môn đã học lại đạt thì không tính nợ đọng.
    """
    from results.models import KetQuaHocTap

    mon_ids = KetQuaHocTap.objects.filter(
        sinh_vien=sinh_vien, diem_tk__isnull=False
    ).values_list('mon_hoc_id', flat=True).distinct()

    tc_no = 0
    for mon_id in mon_ids:
        best = KetQuaHocTap.objects.filter(
            sinh_vien=sinh_vien, mon_hoc_id=mon_id, diem_tk__isnull=False
        ).order_by('-diem_tk').first()
        if best and not la_dat(best.diem_tk):
            tc_no += best.mon_hoc.so_tc
    return tc_no


def xac_dinh_nam_hoc_sv(sinh_vien, hoc_ky):
    """
    Xác định sinh viên đang ở năm thứ mấy dựa trên số HK đã học.
    2 HK/năm → năm 1: HK 1-2, năm 2: HK 3-4, năm 3: HK 5-6, năm 4+: HK 7+
    """
    from students.models import HocKy
    so_hk = HocKy.objects.filter(
        ket_qua__sinh_vien=sinh_vien
    ).distinct().count()

    if so_hk <= 2:   return 1
    if so_hk <= 4:   return 2
    if so_hk <= 6:   return 3
    return 4


def la_hk_dau_khoa(sinh_vien, hoc_ky):
    """Kiểm tra có phải HK đầu tiên của sinh viên không."""
    from students.models import HocKy
    hk_dau = HocKy.objects.filter(
        ket_qua__sinh_vien=sinh_vien
    ).distinct().order_by('nam_hoc', 'ky').first()
    return hk_dau is not None and hk_dau.pk == hoc_ky.pk


def dem_canh_bao_lien_tiep(sinh_vien):
    """Đếm số lần cảnh báo liên tiếp gần nhất (tính từ HK gần nhất về trước)."""
    from academic_warnings.models import CanhBaoHocVu
    from students.models import HocKy

    hockys = HocKy.objects.filter(
        ket_qua__sinh_vien=sinh_vien
    ).distinct().order_by('-nam_hoc', '-ky')

    lien_tiep = 0
    for hk in hockys:
        cb = CanhBaoHocVu.objects.filter(sinh_vien=sinh_vien, hoc_ky=hk).first()
        if cb:
            lien_tiep += 1
        else:
            break
    return lien_tiep


# ─── Kiểm tra cảnh báo học vụ ─────────────────────────────────────────────

def kiem_tra_canh_bao(sinh_vien, hoc_ky, khong_dang_ky=False):
    """
    Kiểm tra điều kiện cảnh báo học vụ theo quy chế Đại học Trà Vinh.

    Vi phạm 1 trong 4 điều kiện → cảnh báo học vụ:
      a) TC không đạt trong HK > 50% TC đăng ký HK,
         HOẶC TC nợ đọng từ đầu khóa > 24 TC
      b) ĐTBCHK < 0.80 (HK đầu khóa) hoặc < 1.00 (HK tiếp theo)
      c) ĐTBCTL < 1.20/1.40/1.60/1.80 theo năm học
      d) Không đăng ký học trong HK chính mà không được phép

    Trả về (co_canh_bao: bool, ly_do: str).
    Việc xác định 'buoc_thoi_hoc' do caller quyết định dựa trên số lần liên tiếp.
    """
    dtbchk_10, dtbchk_4, tc_hk, _ = tinh_dtbchk(sinh_vien, hoc_ky)
    dtbctl_10, dtbctl_4, tc_tl, _ = tinh_dtbctl(sinh_vien)
    nam_hoc = xac_dinh_nam_hoc_sv(sinh_vien, hoc_ky)
    hk_dau = la_hk_dau_khoa(sinh_vien, hoc_ky)

    if tc_hk == 0 and not khong_dang_ky:
        return False, ''

    vi_pham = []

    # ── Điều kiện a ──────────────────────────────────────────────────────
    if tc_hk > 0:
        tc_khong_dat_hk = tinh_tc_khong_dat_hk(sinh_vien, hoc_ky)
        tc_no_dong = tinh_tc_no_dong(sinh_vien)
        ly_do_a = []
        if tc_khong_dat_hk > tc_hk * 0.5:
            pct = tc_khong_dat_hk / tc_hk * 100
            ly_do_a.append(
                f'TC không đạt trong HK {tc_khong_dat_hk}/{tc_hk} TC ({pct:.0f}% > 50%)'
            )
        if tc_no_dong > 24:
            ly_do_a.append(f'TC nợ đọng từ đầu khóa {tc_no_dong} TC > 24 TC')
        if ly_do_a:
            vi_pham.append('a) ' + '; '.join(ly_do_a))

    # ── Điều kiện b ──────────────────────────────────────────────────────
    if tc_hk > 0:
        nguong_hk = 0.80 if hk_dau else 1.00
        if dtbchk_10 < nguong_hk:
            vi_pham.append(
                f'b) ĐTBCHK {dtbchk_10:.2f} < {nguong_hk} '
                f'({"HK đầu khóa" if hk_dau else "HK tiếp theo"})'
            )

    # ── Điều kiện c ──────────────────────────────────────────────────────
    nguong_ctl = {1: 1.20, 2: 1.40, 3: 1.60, 4: 1.80}.get(min(nam_hoc, 4), 1.80)
    if dtbctl_10 < nguong_ctl:
        vi_pham.append(
            f'c) ĐTBCTL {dtbctl_10:.2f} < {nguong_ctl} (năm thứ {nam_hoc})'
        )

    # ── Điều kiện d ──────────────────────────────────────────────────────
    if khong_dang_ky:
        vi_pham.append('d) Không đăng ký học trong HK chính mà không được phép')

    if not vi_pham:
        return False, ''

    return True, '; '.join(vi_pham)


# ─── Thống kê ──────────────────────────────────────────────────────────────

def thong_ke_hocky(sinh_vien, hoc_ky):
    """Thống kê kết quả học tập trong một học kỳ."""
    from results.models import KetQuaHocTap
    ket_qua = KetQuaHocTap.objects.filter(
        sinh_vien=sinh_vien, hoc_ky=hoc_ky, diem_tk__isnull=False
    ).select_related('mon_hoc')

    tong_mon = ket_qua.count()
    mon_dat = sum(1 for kq in ket_qua if la_dat(kq.diem_tk))
    mon_f = sum(1 for kq in ket_qua if kq.diem_tk is not None and kq.diem_tk < 4.0)
    tc_dang_ky = sum(kq.mon_hoc.so_tc for kq in ket_qua)
    tc_dat = sum(kq.mon_hoc.so_tc for kq in ket_qua if la_dat(kq.diem_tk))
    tc_khong_dat = tc_dang_ky - tc_dat
    dtbchk_10, dtbchk_4, _, _ = tinh_dtbchk(sinh_vien, hoc_ky)

    return {
        'tong_mon': tong_mon,
        'mon_dat': mon_dat,
        'mon_khong_dat': tong_mon - mon_dat,
        'mon_f': mon_f,
        'tc_dang_ky': tc_dang_ky,
        'tc_dat': tc_dat,
        'tc_khong_dat': tc_khong_dat,
        'dtbchk': dtbchk_10,
        'dtbchk_4': dtbchk_4,
    }


def get_phan_phoi_diem(sinh_vien=None, hoc_ky=None):
    """Phân phối điểm theo thang chữ A, B+, B, C+, C, D+, D, F."""
    from results.models import KetQuaHocTap
    qs = KetQuaHocTap.objects.filter(diem_tk__isnull=False)
    if sinh_vien:
        qs = qs.filter(sinh_vien=sinh_vien)
    if hoc_ky:
        qs = qs.filter(hoc_ky=hoc_ky)

    phan_phoi = {'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D+': 0, 'D': 0, 'F': 0}
    for kq in qs:
        chu = diem_chu(kq.diem_tk)
        if chu in phan_phoi:
            phan_phoi[chu] += 1
    return phan_phoi
