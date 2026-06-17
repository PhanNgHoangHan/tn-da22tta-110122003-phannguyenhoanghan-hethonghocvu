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
    Đếm tổng số lần bị cảnh báo tích lũy trước học kỳ `truoc_hoc_ky` (không cần liên tiếp).
    Nếu `truoc_hoc_ky` là None, tính tổng số lần cảnh báo từ trước đến nay.
    """
    from academic_warnings.models import CanhBaoHocVu
    from students.models import HocKy
    from django.db.models import Q

    hockys = HocKy.objects.filter(
        ket_qua__sinh_vien=sinh_vien
    ).distinct()

    if truoc_hoc_ky:
        hockys = hockys.filter(
            Q(nam_hoc__lt=truoc_hoc_ky.nam_hoc) |
            Q(nam_hoc=truoc_hoc_ky.nam_hoc, ky__lt=truoc_hoc_ky.ky)
        )

    hockys = hockys.order_by('-nam_hoc', '-ky')

    total_warnings = 0
    for hk in hockys:
        co_cb, _ = kiem_tra_canh_bao(sinh_vien, hk)
        if co_cb:
            total_warnings += 1
    return total_warnings



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
        return 'buoc_thoi_hoc', f'Bị cảnh báo học vụ {so_lan_lien_tiep} lần liên tiếp (Buộc thôi học).'

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
                    return 'buoc_thoi_hoc', f'Đã bị cảnh báo ở học kỳ chính trước ({hk_truoc}) và Điểm trung bình học kỳ hệ 4 học kỳ này ({dtbchk_4:.2f} < 1.00) (Buộc thôi học).'

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
        co_canh_bao, ly_do = kiem_tra_canh_bao(sinh_vien, hk)
        if co_canh_bao:
            so_lan_lien_tiep = dem_canh_bao_lien_tiep(sinh_vien, hk) + 1
            muc, ly_do_bo_sung = xac_dinh_muc_canh_bao(sinh_vien, hk, so_lan_lien_tiep)
            
            # Nếu có từ 3 lần cảnh báo liên tiếp trở lên, tổng hợp lý do đầy đủ của các lần
            if so_lan_lien_tiep >= 3:
                import re
                def clean_reason(text):
                    if not text:
                        return ''
                    # Bỏ các prefix 'Lý do X:' lồng nhau
                    text = re.sub(r'(?:^|;\s*)L\u00fd do \d+:\s*', lambda m: '; ' if m.group().startswith(';') else '', text)
                    return text.strip()

                reasons_list = []
                # Lấy lại các học kỳ cảnh báo trước đó của sinh viên này trong chuỗi liên tiếp
                prev_cbs = CanhBaoHocVu.objects.filter(
                    sinh_vien=sinh_vien, 
                    so_lan_canh_bao__lt=so_lan_lien_tiep
                ).order_by('so_lan_canh_bao')
                
                for prev_cb in prev_cbs:
                    _, r_raw = kiem_tra_canh_bao(sinh_vien, prev_cb.hoc_ky)
                    reasons_list.append(f"Lần {prev_cb.so_lan_canh_bao} ({prev_cb.hoc_ky}): {clean_reason(r_raw)}")
                
                # Thêm lý do của lần hiện tại
                reasons_list.append(f"Lần {so_lan_lien_tiep} ({hk}): {clean_reason(ly_do)}")
                ly_do = "; ".join(reasons_list)

            if ly_do_bo_sung:
                ly_do = ly_do_bo_sung + ' ' + ly_do

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
