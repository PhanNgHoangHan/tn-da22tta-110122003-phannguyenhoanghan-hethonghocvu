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


import unicodedata

def remove_accents(input_str):
    if not input_str:
        return ""
    # Loại bỏ khoảng trắng thừa ở hai đầu và thu gọn nhiều khoảng trắng liên tiếp
    input_str = " ".join(input_str.strip().split())
    input_str = unicodedata.normalize('NFC', input_str).lower()
    
    # Vietnamese tones and diacritics mapping
    mapping = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    }
    
    res = []
    for c in input_str:
        res.append(mapping.get(c, c))
    
    decomposed = unicodedata.normalize('NFD', "".join(res))
    return "".join([c for c in decomposed if not unicodedata.combining(c)])


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


def la_gdtc(ma_mh):
    """Kiểm tra môn học có phải Giáo dục thể chất hay không (loại trừ Giáo dục quốc phòng 190)."""
    if not ma_mh:
        return False
    cleaned = ma_mh.strip()
    return cleaned.startswith('19') and not cleaned.startswith('190')


# ─── Tính điểm trung bình ──────────────────────────────────────────────────

def tinh_dtbchk(sinh_vien, hoc_ky):
    """
    Tính ĐTBCHK hệ 10 = Σ(điểm_i × TC_i) / Σ(TC_i).
    Tính ĐTBCHK hệ 4  = Σ(diem_he4_i × TC_i) / Σ(TC_i).
    Chỉ tính lần học đầu tiên (lan_hoc=1) trong HK - đúng quy chế.
    Loại trừ môn Giáo dục thể chất và Giáo dục quốc phòng (mã bắt đầu bằng 19) khỏi ĐTB.
    Trả về (dtbchk_10, dtbchk_4, tong_tc_hk, tc_dat_hk).
    """
    from results.models import KetQuaHocTap
    ket_qua = KetQuaHocTap.objects.filter(
        sinh_vien=sinh_vien, hoc_ky=hoc_ky, diem_tk__isnull=False, lan_hoc=1
    ).select_related('mon_hoc')

    tong_tc_gpa = 0
    tong_diem_10 = 0.0
    tong_diem_4 = 0.0
    
    tong_tc_hk = 0
    tc_dat = 0
    for kq in ket_qua:
        tc = kq.mon_hoc.so_tc
        tong_tc_hk += tc
        if la_dat(kq.diem_tk):
            tc_dat += tc
            
        # Loại bỏ môn Giáo dục thể chất khỏi tính ĐTB
        if la_gdtc(kq.mon_hoc.ma_mh):
            continue
            
        tong_tc_gpa += tc
        tong_diem_10 += (kq.diem_tk or 0) * tc
        tong_diem_4  += (diem_he4(kq.diem_tk) or 0) * tc

    if tong_tc_gpa == 0:
        return 0.0, 0.0, tong_tc_hk, tc_dat
    return (round(tong_diem_10 / tong_tc_gpa, 2),
            round(tong_diem_4  / tong_tc_gpa, 2),
            tong_tc_hk, tc_dat)


def tinh_dtbctl(sinh_vien, hoc_ky=None):
    """
    Tính ĐTBCTL hệ 10 và hệ 4 (lấy điểm tốt nhất mỗi môn, trọng số TC, kể cả F).
    Chỉ tính các học kỳ từ trước đến học kỳ `hoc_ky` (nếu có).
    Loại trừ môn Giáo dục thể chất và Giáo dục quốc phòng (mã bắt đầu bằng 19) khỏi ĐTBCTL.
    Trả về (dtbctl_10, dtbctl_4, tc_tich_luy, tong_tc_da_hoc).
    """
    from results.models import KetQuaHocTap
    from django.db.models import Q

    qs = KetQuaHocTap.objects.filter(sinh_vien=sinh_vien, diem_tk__isnull=False)
    if hoc_ky:
        qs = qs.filter(
            Q(hoc_ky__nam_hoc__lt=hoc_ky.nam_hoc) |
            Q(hoc_ky__nam_hoc=hoc_ky.nam_hoc, hoc_ky__ky__lte=hoc_ky.ky)
        )

    mon_ids = qs.values_list('mon_hoc_id', flat=True).distinct()

    tong_tc_gpa = 0
    tong_diem_10 = 0.0
    tong_diem_4  = 0.0
    tc_tich_luy  = 0
    tong_tc_da_hoc = 0

    for mon_id in mon_ids:
        best = qs.filter(mon_hoc_id=mon_id).order_by('-diem_tk').first()
        if best:
            tc = best.mon_hoc.so_tc
            tong_tc_da_hoc += tc
            if la_dat(best.diem_tk):
                tc_tich_luy += tc
                
            # Loại bỏ môn Giáo dục thể chất khỏi tính ĐTB
            if la_gdtc(best.mon_hoc.ma_mh):
                continue
                
            tong_tc_gpa += tc
            tong_diem_10 += (best.diem_tk or 0) * tc
            tong_diem_4  += (diem_he4(best.diem_tk) or 0) * tc

    dtbctl_10 = round(tong_diem_10 / tong_tc_gpa, 2) if tong_tc_gpa > 0 else 0.0
    dtbctl_4  = round(tong_diem_4  / tong_tc_gpa, 2) if tong_tc_gpa > 0 else 0.0
    return dtbctl_10, dtbctl_4, tc_tich_luy, tong_tc_da_hoc



# ─── Các hàm hỗ trợ cảnh báo ──────────────────────────────────────────────

def tinh_tc_khong_dat_hk(sinh_vien, hoc_ky):
    """Tổng TC học phần không đạt (điểm F) trong HK."""
    from results.models import KetQuaHocTap
    ket_qua = KetQuaHocTap.objects.filter(
        sinh_vien=sinh_vien, hoc_ky=hoc_ky, diem_tk__isnull=False
    ).select_related('mon_hoc')
    return sum(kq.mon_hoc.so_tc for kq in ket_qua if not la_dat(kq.diem_tk))


def tinh_tc_no_dong(sinh_vien, hoc_ky=None):
    """
    Tổng TC nợ đọng từ đầu khóa đến học kỳ `hoc_ky` = TC các môn chưa đạt (điểm F tốt nhất).
    Môn đã học lại đạt thì không tính nợ đọng.
    """
    from results.models import KetQuaHocTap
    from django.db.models import Q

    qs = KetQuaHocTap.objects.filter(sinh_vien=sinh_vien, diem_tk__isnull=False)
    if hoc_ky:
        qs = qs.filter(
            Q(hoc_ky__nam_hoc__lt=hoc_ky.nam_hoc) |
            Q(hoc_ky__nam_hoc=hoc_ky.nam_hoc, hoc_ky__ky__lte=hoc_ky.ky)
        )

    mon_ids = qs.values_list('mon_hoc_id', flat=True).distinct()

    tc_no = 0
    for mon_id in mon_ids:
        best = qs.filter(mon_hoc_id=mon_id).order_by('-diem_tk').first()
        if best and not la_dat(best.diem_tk):
            tc_no += best.mon_hoc.so_tc
    return tc_no



def xac_dinh_nam_hoc_sv(sinh_vien, hoc_ky):
    """
    Xác định sinh viên đang ở năm thứ mấy tính đến học kỳ `hoc_ky`.
    2 HK/năm → năm 1: HK 1-2, năm 2: HK 3-4, năm 3: HK 5-6, năm 4+: HK 7+
    Chỉ đếm các HK có điểm từ trước đến HK hiện tại (tránh tính tương lai).
    """
    from students.models import HocKy
    from django.db.models import Q
    so_hk = HocKy.objects.filter(
        ket_qua__sinh_vien=sinh_vien
    ).filter(
        Q(nam_hoc__lt=hoc_ky.nam_hoc) |
        Q(nam_hoc=hoc_ky.nam_hoc, ky__lte=hoc_ky.ky)
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


def dem_canh_bao_lien_tiep(sinh_vien, truoc_hoc_ky=None):
    """
    Đếm số lần bị cảnh báo liên tiếp ngay trước học kỳ `truoc_hoc_ky` (chỉ xét các học kỳ chính 1 và 2).
    Nếu gặp học kỳ chính nào không bị cảnh báo học vụ, chuỗi liên tiếp sẽ bị ngắt (dừng đếm).
    """
    from academic_warnings.models import CanhBaoHocVu
    from students.models import HocKy
    from django.db.models import Q

    hockys = HocKy.objects.filter(
        ket_qua__sinh_vien=sinh_vien,
        ky__in=['1', '2']  # Chỉ xét các học kỳ chính
    ).distinct()

    if truoc_hoc_ky:
        hockys = hockys.filter(
            Q(nam_hoc__lt=truoc_hoc_ky.nam_hoc) |
            Q(nam_hoc=truoc_hoc_ky.nam_hoc, ky__lt=truoc_hoc_ky.ky)
        )

    hockys = hockys.order_by('-nam_hoc', '-ky')

    consecutive_warnings = 0
    for hk in hockys:
        co_cb, _ = kiem_tra_canh_bao(sinh_vien, hk)
        if co_cb:
            consecutive_warnings += 1
        else:
            break  # Gặp học kỳ chính an toàn -> ngắt chuỗi liên tiếp
    return consecutive_warnings



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
    if hoc_ky.ky == '3':  # Học kỳ hè/học kỳ phụ không xét cảnh báo học vụ
        return False, ''

    dtbchk_10, dtbchk_4, tc_hk, _ = tinh_dtbchk(sinh_vien, hoc_ky)
    dtbctl_10, dtbctl_4, tc_tl, _ = tinh_dtbctl(sinh_vien, hoc_ky)
    nam_hoc = xac_dinh_nam_hoc_sv(sinh_vien, hoc_ky)
    hk_dau = la_hk_dau_khoa(sinh_vien, hoc_ky)

    if tc_hk == 0 and not khong_dang_ky:
        return False, ''

    vi_pham = []

    # ── Điều kiện a ──────────────────────────────────────────────────────
    if tc_hk > 0:
        tc_khong_dat_hk = tinh_tc_khong_dat_hk(sinh_vien, hoc_ky)
        tc_no_dong = tinh_tc_no_dong(sinh_vien, hoc_ky)

        ly_do_a = []
        if tc_khong_dat_hk > tc_hk * 0.5:
            pct = tc_khong_dat_hk / tc_hk * 100
            ly_do_a.append(
                f'Tín chỉ không đạt trong học kỳ {tc_khong_dat_hk}/{tc_hk} tín chỉ ({pct:.0f}% > 50%)'
            )
        if tc_no_dong > 24:
            ly_do_a.append(f'Tín chỉ nợ đọng từ đầu khóa {tc_no_dong} tín chỉ > 24 tín chỉ')
        if ly_do_a:
            vi_pham.append('; '.join(ly_do_a))

    # ── Điều kiện b ──────────────────────────────────────────────────────
    if tc_hk > 0:
        nguong_hk = 0.80 if hk_dau else 1.00
        if dtbchk_4 < nguong_hk:
            vi_pham.append(
                f'Điểm trung bình học kỳ hệ 4 {dtbchk_4:.2f} < {nguong_hk:.2f}'
            )

    # ── Điều kiện c ──────────────────────────────────────────────────────
    if not hk_dau:
        nguong_ctl = {1: 1.20, 2: 1.40, 3: 1.60, 4: 1.80}.get(min(nam_hoc, 4), 1.80)
        if dtbctl_4 < nguong_ctl:
            vi_pham.append(
                f'Điểm trung bình tích lũy hệ 4 {dtbctl_4:.2f} < {nguong_ctl:.2f} (năm thứ {nam_hoc})'
            )


    # ── Điều kiện d ──────────────────────────────────────────────────────
    if khong_dang_ky:
        vi_pham.append('Không đăng ký học trong học kỳ chính mà không được phép')

    if not vi_pham:
        return False, ''

    if len(vi_pham) == 1:
        return True, vi_pham[0]

    vi_pham_numbered = [f"Lý do {i+1}: {vp}" for i, vp in enumerate(vi_pham)]
    return True, '; '.join(vi_pham_numbered)


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


def xac_dinh_muc_canh_bao(sinh_vien, hoc_ky, so_lan_lien_tiep):
    """
    Xác định mức cảnh báo ('canh_bao' hoặc 'buoc_thoi_hoc') và lý do bổ sung (nếu có).
    Trả về (muc: str, ly_do_bo_sung: str).
    """
    from academic_warnings.models import CanhBaoHocVu
    from students.models import HocKy
    from django.db.models import Q

    # Điều kiện 1: Số lần cảnh báo học tập vượt quá 2 (tức là cảnh báo đến lần thứ 3)
    if so_lan_lien_tiep > 2:
        return 'buoc_thoi_hoc', 'lien_tiep'

    # Điều kiện 2: Đã bị cảnh báo học tập và học kỳ chính kế tiếp có điểm trung bình chung học kỳ dưới 1,00 theo hệ 4.
    if hoc_ky.ky in ['1', '2']:
        # Tìm học kỳ chính liền trước học kỳ này
        hk_truoc = HocKy.objects.filter(
            Q(nam_hoc__lt=hoc_ky.nam_hoc) |
            Q(nam_hoc=hoc_ky.nam_hoc, ky__lt=hoc_ky.ky)
        ).filter(ky__in=['1', '2']).order_by('-nam_hoc', '-ky').first()

        if hk_truoc:
            co_cb_truoc = CanhBaoHocVu.objects.filter(sinh_vien=sinh_vien, hoc_ky=hk_truoc).exists()
            if co_cb_truoc:
                # Tính ĐTBCHK hệ 4 học kỳ này
                _, dtbchk_4, tong_tc_hk, _ = tinh_dtbchk(sinh_vien, hoc_ky)
                if tong_tc_hk > 0 and dtbchk_4 < 1.00:
                    return 'buoc_thoi_hoc', f'Đã bị cảnh báo ở học kỳ chính trước ({hk_truoc}) và Điểm trung bình học kỳ hệ 4 học kỳ này ({dtbchk_4:.2f} < 1.00)'

    return 'canh_bao', ''


def dong_bo_canh_bao_sinh_vien(sinh_vien):
    """
    Đồng bộ tự động tất cả cảnh báo học vụ và trạng thái của một sinh viên.
    Duyệt qua toàn bộ các học kỳ có điểm theo trình tự thời gian tăng dần,
    cập nhật hoặc xóa các cảnh báo tương ứng, và thiết lập trạng thái sinh viên phù hợp.
    """
    from academic_warnings.models import CanhBaoHocVu
    from students.models import HocKy

    # Lấy danh sách học kỳ có điểm theo trình tự thời gian tăng dần
    hockys = HocKy.objects.filter(
        ket_qua__sinh_vien=sinh_vien
    ).distinct().order_by('nam_hoc', 'ky')

    for hk in hockys:
        co_canh_bao, ly_do_check = kiem_tra_canh_bao(sinh_vien, hk)
        if co_canh_bao:
            so_lan_lien_tiep = dem_canh_bao_lien_tiep(sinh_vien, hk) + 1
            muc, ly_do_bo_sung = xac_dinh_muc_canh_bao(sinh_vien, hk, so_lan_lien_tiep)
            
            if muc == 'buoc_thoi_hoc':
                if ly_do_bo_sung == 'lien_tiep':
                    # Tìm 3 học kỳ chính liên tiếp có cảnh báo kết thúc bằng học kỳ `hk` hiện tại
                    from django.db.models import Q
                    main_hks = HocKy.objects.filter(
                        ket_qua__sinh_vien=sinh_vien,
                        ky__in=['1', '2']
                    ).filter(
                        Q(nam_hoc__lt=hk.nam_hoc) |
                        Q(nam_hoc=hk.nam_hoc, ky__lte=hk.ky)
                    ).distinct().order_by('-nam_hoc', '-ky')
                    
                    consecutive_hks = []
                    for m_hk in main_hks:
                        co_cb, _ = kiem_tra_canh_bao(sinh_vien, m_hk)
                        if co_cb:
                            consecutive_hks.append(m_hk)
                        else:
                            break
                        if len(consecutive_hks) == 3:
                            break
                    
                    consecutive_hks.reverse()
                    
                    if len(consecutive_hks) >= 3:
                        hk1_str = f"học kì {consecutive_hks[0].ky} - {consecutive_hks[0].nam_hoc}"
                        hk2_str = f"học kì {consecutive_hks[1].ky} - {consecutive_hks[1].nam_hoc}"
                        hk3_str = f"học kì {consecutive_hks[2].ky} - {consecutive_hks[2].nam_hoc}"
                        
                        import re
                        r3_clean = re.sub(r'(?:^|;\s*)L\u00fd do \d+:\s*', lambda m: '; ' if m.group().startswith(';') else '', ly_do_check).strip()
                        
                        ly_do = f"Đã bị cảnh báo 3 lần liên tiếp, lần 1 {hk1_str}, lần 2 {hk2_str}, lần 3 {hk3_str} với lý do {r3_clean}"
                    else:
                        ly_do = f"Đã bị cảnh báo {so_lan_lien_tiep} lần liên tiếp"
                else:
                    ly_do = ly_do_bo_sung
            else:
                ly_do = ly_do_check

            CanhBaoHocVu.objects.update_or_create(
                sinh_vien=sinh_vien, hoc_ky=hk,
                defaults={
                    'muc_canh_bao': muc,
                    'ly_do': ly_do,
                    'trang_thai': 'chua_xu_ly',
                    'so_lan_canh_bao': so_lan_lien_tiep,
                }
            )
        else:
            # Nếu không thỏa mãn điều kiện cảnh báo học kỳ này, xóa bản ghi cảnh báo cũ nếu có
            CanhBaoHocVu.objects.filter(sinh_vien=sinh_vien, hoc_ky=hk).delete()

    # Cập nhật trạng thái sinh viên:
    # 1. Nếu có bất kỳ cảnh báo "buộc thôi học" nào -> dinh_chi
    # 2. Cảnh báo lần 1 và lần 2 (canh_bao) vẫn tính là dang_hoc
    # 3. Ngược lại -> dang_hoc
    has_bth = CanhBaoHocVu.objects.filter(sinh_vien=sinh_vien, muc_canh_bao='buoc_thoi_hoc').exists()
    if has_bth:
        sinh_vien.trang_thai = 'dinh_chi'
    else:
        sinh_vien.trang_thai = 'dang_hoc'
    sinh_vien.save()


def tinh_dtbchk_in_memory(student_results, hoc_ky):
    """Tính ĐTBCHK hệ 10 và hệ 4 hoàn toàn in-memory từ danh sách kết quả học tập đã được prefetch."""
    tong_tc_gpa = 0
    tong_diem_10 = 0.0
    tong_diem_4 = 0.0
    tong_tc_hk = 0
    tc_dat = 0
    
    # Lọc các kết quả trong học kỳ này, có điểm và lần học = 1
    hk_results = [
        r for r in student_results 
        if r.hoc_ky_id == hoc_ky.id and r.diem_tk is not None and r.lan_hoc == 1
    ]
    
    for r in hk_results:
        tc = r.mon_hoc.so_tc
        tong_tc_hk += tc
        if la_dat(r.diem_tk):
            tc_dat += tc
            
        if la_gdtc(r.mon_hoc.ma_mh):
            continue
            
        tong_tc_gpa += tc
        tong_diem_10 += r.diem_tk * tc
        tong_diem_4  += (diem_he4(r.diem_tk) or 0) * tc

    if tong_tc_gpa == 0:
        return 0.0, 0.0, tong_tc_hk, tc_dat
    return (round(tong_diem_10 / tong_tc_gpa, 2),
            round(tong_diem_4  / tong_tc_gpa, 2),
            tong_tc_hk, tc_dat)


def tinh_dtbctl_in_memory(student_results, hoc_ky=None):
    """Tính ĐTBCTL hệ 10 và hệ 4 hoàn toàn in-memory từ danh sách kết quả học tập đã được prefetch."""
    # Lọc các môn học có điểm từ trước đến học kỳ chỉ định
    qs = [r for r in student_results if r.diem_tk is not None]
    if hoc_ky:
        qs = [
            r for r in qs
            if r.hoc_ky.nam_hoc < hoc_ky.nam_hoc or (r.hoc_ky.nam_hoc == hoc_ky.nam_hoc and r.hoc_ky.ky <= hoc_ky.ky)
        ]

    # Tìm điểm tốt nhất của mỗi môn học
    best_results = {}
    for r in qs:
        m_id = r.mon_hoc_id
        if m_id not in best_results or r.diem_tk > best_results[m_id].diem_tk:
            best_results[m_id] = r
            
    tong_tc_gpa = 0
    tong_diem_10 = 0.0
    tong_diem_4  = 0.0
    tc_tich_luy  = 0
    tong_tc_da_hoc = 0

    for best in best_results.values():
        tc = best.mon_hoc.so_tc
        tong_tc_da_hoc += tc
        if la_dat(best.diem_tk):
            tc_tich_luy += tc
            
        if la_gdtc(best.mon_hoc.ma_mh):
            continue
            
        tong_tc_gpa += tc
        tong_diem_10 += best.diem_tk * tc
        tong_diem_4  += (diem_he4(best.diem_tk) or 0) * tc

    dtbctl_10 = round(tong_diem_10 / tong_tc_gpa, 2) if tong_tc_gpa > 0 else 0.0
    dtbctl_4  = round(tong_diem_4  / tong_tc_gpa, 2) if tong_tc_gpa > 0 else 0.0
    return dtbctl_10, dtbctl_4, tc_tich_luy, tong_tc_da_hoc


def tinh_canh_bao_som(sinh_vien, hoc_ky=None, prefetch_results=None, prefetch_warnings=None):
    """
    Phân tích cảnh báo sớm học vụ theo 5 tầng quyết định.
    Hỗ trợ tham số prefetch_results và prefetch_warnings để chạy O(1) in-memory mà không truy vấn database.
    """
    from students.models import HocKy
    from results.models import KetQuaHocTap
    from academic_warnings.models import CanhBaoHocVu
    from django.db.models import Q

    # Tầng 1: Thu thập dữ liệu học kỳ
    if prefetch_results is not None:
        student_results = prefetch_results.get(sinh_vien.id, [])
        # Trích xuất các học kỳ từ kết quả học tập của sinh viên
        hk_dict = {}
        for r in student_results:
            if r.hoc_ky_id not in hk_dict:
                hk_dict[r.hoc_ky_id] = r.hoc_ky
        
        hks_list = list(hk_dict.values())
        if hoc_ky:
            hks_list = [
                hk for hk in hks_list
                if hk.nam_hoc < hoc_ky.nam_hoc or (hk.nam_hoc == hoc_ky.nam_hoc and hk.ky <= hoc_ky.ky)
            ]
        hockys = sorted(hks_list, key=lambda hk: (hk.nam_hoc, hk.ky))
    else:
        student_results = None
        hockys_query = HocKy.objects.filter(ket_qua__sinh_vien=sinh_vien).distinct()
        if hoc_ky:
            hockys_query = hockys_query.filter(
                Q(nam_hoc__lt=hoc_ky.nam_hoc) |
                Q(nam_hoc=hoc_ky.nam_hoc, ky__lte=hoc_ky.ky)
            )
        hockys = list(hockys_query.order_by('nam_hoc', 'ky'))

    default_res = {
        'sinh_vien': sinh_vien,
        'hoc_ky': hoc_ky,
        'muc_nguy_co': 'safe',
        'muc_nguy_co_display': 'An toàn',
        'mau_nguy_co': 'success',
        'gpa_hk_10': 0.0,
        'gpa_hk_4': 0.0,
        'gpa_tl_10': 0.0,
        'gpa_tl_4': 0.0,
        'tc_hk_reg': 0,
        'tc_hk_pass': 0,
        'tc_tl_reg': 0,
        'tc_tl_pass': 0,
        'ly_do': 'Chưa có kết quả học tập ghi nhận.',
        'xu_huong': 'none',
        'xu_huong_display': '-',
        'diem_yeu': [],
        'goi_y': []
    }

    if not hockys:
        return default_res

    # Chọn học kỳ phân tích là học kỳ chỉ định hoặc học kỳ gần nhất
    target_hk = hoc_ky if hoc_ky else hockys[-1]
    
    # Tính toán GPA học kỳ & tích lũy
    if prefetch_results is not None:
        gpa_hk_10, gpa_hk_4, tc_hk_reg, tc_hk_pass = tinh_dtbchk_in_memory(student_results, target_hk)
        gpa_tl_10, gpa_tl_4, tc_tl_pass, tc_tl_reg = tinh_dtbctl_in_memory(student_results, target_hk)
    else:
        gpa_hk_10, gpa_hk_4, tc_hk_reg, tc_hk_pass = tinh_dtbchk(sinh_vien, target_hk)
        gpa_tl_10, gpa_tl_4, tc_tl_pass, tc_tl_reg = tinh_dtbctl(sinh_vien, target_hk)

    # Tầng 2 & 3: Phân loại mức nguy cơ dựa trên GPA tích lũy
    muc_nguy_co = 'safe'
    muc_nguy_co_display = 'An toàn'
    mau_nguy_co = 'success'
    ly_do = f'Kết quả học tập tốt, ĐTBCTL đạt {gpa_tl_4:.2f} (Hệ 4).'

    if gpa_tl_4 < 1.2:
        muc_nguy_co = 'warning_2'
        muc_nguy_co_display = 'Cảnh báo mức 2'
        mau_nguy_co = 'danger'
        ly_do = f'ĐTBCTL quá thấp ({gpa_tl_4:.2f} < 1.20). Có nguy cơ cao bị buộc thôi học.'
    elif gpa_tl_4 < 1.8:
        muc_nguy_co = 'warning_1'
        muc_nguy_co_display = 'Cảnh báo mức 1'
        mau_nguy_co = 'warning'
        ly_do = f'ĐTBCTL thấp ({gpa_tl_4:.2f} < 1.80). Cần cải thiện học tập ngay.'
    elif gpa_tl_4 < 2.0:
        muc_nguy_co = 'monitor'
        muc_nguy_co_display = 'Theo dõi'
        mau_nguy_co = 'info'
        ly_do = f'ĐTBCTL ở mức trung bình yếu ({gpa_tl_4:.2f} < 2.00). Cần theo sát tiến độ để tránh bị cảnh báo học vụ.'

    # Kiểm tra xem có cảnh báo học vụ chính thức nào trong học kỳ này không
    if prefetch_warnings is not None:
        cb_chinh_thuc = prefetch_warnings.get((sinh_vien.id, target_hk.id))
    else:
        cb_chinh_thuc = CanhBaoHocVu.objects.filter(sinh_vien=sinh_vien, hoc_ky=target_hk).first()

    if cb_chinh_thuc:
        if cb_chinh_thuc.muc_canh_bao == 'buoc_thoi_hoc':
            muc_nguy_co = 'warning_2'
            muc_nguy_co_display = 'Cảnh báo mức 2 (Buộc thôi học)'
            mau_nguy_co = 'danger'
            ly_do = f'Buộc thôi học ở học kỳ {target_hk}.'
        else:
            # Bị cảnh báo học vụ chính thức
            if cb_chinh_thuc.so_lan_canh_bao >= 2:
                muc_nguy_co = 'warning_2'
                muc_nguy_co_display = 'Cảnh báo mức 2 (Nguy cơ thôi học)'
                mau_nguy_co = 'danger'
                ly_do = f'Đã bị cảnh báo học vụ chính thức lần thứ {cb_chinh_thuc.so_lan_canh_bao}. Lần tiếp theo sẽ bị Buộc thôi học.'
            elif muc_nguy_co in ['safe', 'monitor']:
                # Nâng cấp lên mức 1 nếu bị cảnh báo chính thức
                muc_nguy_co = 'warning_1'
                muc_nguy_co_display = 'Cảnh báo mức 1'
                mau_nguy_co = 'warning'
                ly_do = f'Bị cảnh báo học vụ chính thức lần 1 ở học kỳ {target_hk}.'

    # Dự báo xu hướng (so sánh với học kỳ liền trước)
    xu_huong = 'none'
    xu_huong_display = '-'
    
    if len(hockys) >= 2 and target_hk in hockys:
        target_idx = hockys.index(target_hk)
        if target_idx > 0:
            prev_hk = hockys[target_idx - 1]
            if prefetch_results is not None:
                _, prev_gpa_tl_4, _, _ = tinh_dtbctl_in_memory(student_results, prev_hk)
            else:
                _, prev_gpa_tl_4, _, _ = tinh_dtbctl(sinh_vien, prev_hk)
            diff = gpa_tl_4 - prev_gpa_tl_4
            if diff > 0.1:
                xu_huong = 'up'
                xu_huong_display = 'Xu hướng cải thiện tốt'
            elif diff < -0.1:
                xu_huong = 'down'
                xu_huong_display = 'Xu hướng sa sút'
            else:
                xu_huong = 'stable'
                xu_huong_display = 'Xu hướng ổn định'

    # Tầng 4: Phân tích điểm yếu & môn ảnh hưởng GPA
    # Lấy điểm tốt nhất của từng môn từ đầu khóa đến học kỳ target_hk
    if prefetch_results is not None:
        results = [
            r for r in student_results
            if r.diem_tk is not None and (
                r.hoc_ky.nam_hoc < target_hk.nam_hoc or (r.hoc_ky.nam_hoc == target_hk.nam_hoc and r.hoc_ky.ky <= target_hk.ky)
            )
        ]
    else:
        qs_results = KetQuaHocTap.objects.filter(sinh_vien=sinh_vien, diem_tk__isnull=False).filter(
            Q(hoc_ky__nam_hoc__lt=target_hk.nam_hoc) |
            Q(hoc_ky__nam_hoc=target_hk.nam_hoc, hoc_ky__ky__lte=target_hk.ky)
        ).select_related('mon_hoc', 'hoc_ky')
        results = list(qs_results)

    best_results = {}
    for r in results:
        m_id = r.mon_hoc_id
        if m_id not in best_results or r.diem_tk > best_results[m_id].diem_tk:
            best_results[m_id] = r
            
    # Tính tổng số tín chỉ tính GPA để chia tỉ lệ cải thiện
    tong_tc_gpa = 0
    for best_kq in best_results.values():
        if not la_gdtc(best_kq.mon_hoc.ma_mh):
            tong_tc_gpa += best_kq.mon_hoc.so_tc

    weak_points = []
    for best_kq in best_results.values():
        diem_10 = best_kq.diem_tk
        diem_ch = diem_chu(diem_10)
        diem_h4 = diem_he4(diem_10)
        so_tc = best_kq.mon_hoc.so_tc
        
        # Môn học bị xếp điểm F, D hoặc D+ được xem là điểm yếu
        if diem_ch in ['F', 'D', 'D+']:
            # Tính lượng điểm GPA hệ 4 có thể cải thiện nếu học lại đạt điểm A (4.0)
            gpa_improvement = 0.0
            if tong_tc_gpa > 0 and not la_gdtc(best_kq.mon_hoc.ma_mh):
                gpa_improvement = ((4.0 - diem_h4) * so_tc) / tong_tc_gpa
            
            weak_points.append({
                'ma_mh': best_kq.mon_hoc.ma_mh,
                'ten_mh': best_kq.mon_hoc.ten_mh,
                'so_tc': so_tc,
                'diem_tk': diem_10,
                'diem_chu': diem_ch,
                'diem_he4': diem_h4,
                'improvement': round(gpa_improvement, 3),
                'hoc_ky': str(best_kq.hoc_ky),
                'hoc_ky_id': best_kq.hoc_ky_id,
                'is_current_hk': best_kq.hoc_ky_id == target_hk.id,
            })
                
    # Sắp xếp điểm yếu: Môn F lên đầu, sau đó sắp xếp theo mức độ cải thiện GPA giảm dần
    weak_points.sort(key=lambda x: (x['diem_chu'] != 'F', -x['improvement']))

    # Gợi ý giải pháp cụ thể
    goi_y = []
    cv = sinh_vien.covan_hien_tai
    cv_name = cv.full_name if cv else "Võ Hoàng Giang"
    cv_email = cv.email if (cv and cv.email) else "giang@gmail.com"

    has_f = False
    has_d_or_dplus = False
    for r in best_results.values():
        ch = diem_chu(r.diem_tk)
        if ch == 'F':
            has_f = True
        elif ch in ['D', 'D+']:
            has_d_or_dplus = True

    if has_f:
        goi_y.append("Đăng ký học lại môn còn nợ.")
        goi_y.append("Nên học cải thiện các môn điểm còn thấp để có kết quả tốt hơn.")
        goi_y.append(f"Chủ động liên hệ Cố vấn học tập {cv_name} (Email: {cv_email}) để nhận tư vấn xây dựng lại lộ trình học tập cá nhân.")
    elif has_d_or_dplus:
        goi_y.append("Nên học cải thiện các môn điểm còn thấp để có kết quả tốt hơn.")
        goi_y.append(f"Chủ động liên hệ Cố vấn học tập {cv_name} (Email: {cv_email}) để nhận tư vấn xây dựng lại lộ trình học tập cá nhân.")
    else:
        goi_y.append("Kết quả học tập của bạn khá tốt, cố gắng duy trì và phát huy nhé!")

    return {
        'sinh_vien': sinh_vien,
        'hoc_ky': target_hk,
        'muc_nguy_co': muc_nguy_co,
        'muc_nguy_co_display': muc_nguy_co_display,
        'mau_nguy_co': mau_nguy_co,
        'gpa_hk_10': gpa_hk_10,
        'gpa_hk_4': gpa_hk_4,
        'gpa_tl_10': gpa_tl_10,
        'gpa_tl_4': gpa_tl_4,
        'tc_hk_reg': tc_hk_reg,
        'tc_hk_pass': tc_hk_pass,
        'tc_tl_reg': tc_tl_reg,
        'tc_tl_pass': tc_tl_pass,
        'ly_do': ly_do,
        'xu_huong': xu_huong,
        'xu_huong_display': xu_huong_display,
        'diem_yeu': weak_points,
        'goi_y': goi_y
    }

