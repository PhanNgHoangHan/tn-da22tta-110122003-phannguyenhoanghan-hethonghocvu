"""
Thêm sinh viên Phan Nguyễn Hoàng Hân với điểm ngẫu nhiên.
Chạy: python manage.py add_sv_han

Chiến lược tạo đúng 2 HK cảnh báo (HK1 2022-2023 và HK1 2025-2026):
- Các HK bình thường: tất cả môn đạt (5.5 - 9.5)
- 2 HK cảnh báo: chỉ cho rớt đúng 5 môn (15 TC) trong tổng số môn của HK
  → TC không đạt = 15 TC > 50% TC đăng ký (vi phạm điều kiện a)
  → ĐTBCHK thấp (vi phạm điều kiện b)
  → TC nợ đọng = 15 TC ≤ 24 TC → KHÔNG lan sang HK sau
  → Các môn F được học lại đạt trong cùng HK (lan_hoc=2) để reset TC nợ
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from students.models import SinhVien, Nganh, Lop, HocKy, MonHoc
from results.models import KetQuaHocTap
from academic_warnings.models import CanhBaoHocVu
from results.utils import kiem_tra_canh_bao

User = get_user_model()

MON_THEO_HK = {
    ('1', '2022-2023'): ['110001','110042','180050','190081','190082','190083','190084',
                          '191','220092','220228','410291','450015'],
    ('2', '2022-2023'): ['110003','170011','180051','192.08','220233','220234',
                          '290000','410292','640033'],
    ('1', '2023-2024'): ['110002','110079','180052','193.15','220096','220099',
                          '220100','410293'],
    ('2', '2023-2024'): ['110057','180001','220018','220101','220236','220237',
                          '220250','410294'],
    ('1', '2024-2025'): ['180053','220065','220086','220239','220265','220267','320045'],
    ('2', '2024-2025'): ['220055','220060','220071','220126','220242','220269','420000'],
    ('1', '2025-2026'): ['220057','220078','220120','220243','220245','220266','220268'],
}

HK_ORDER = [
    ('1', '2022-2023'), ('2', '2022-2023'),
    ('1', '2023-2024'), ('2', '2023-2024'),
    ('1', '2024-2025'), ('2', '2024-2025'),
    ('1', '2025-2026'),
]

# 2 HK cố định sẽ bị cảnh báo
HK_CANH_BAO = {('1', '2022-2023'), ('1', '2025-2026')}

# Số môn F trong mỗi HK cảnh báo: chọn 5 môn (15 TC) để vi phạm >50%
# nhưng TC nợ = 15 ≤ 24 → không lan sang HK sau
SO_MON_F = 5  # 5 môn × 3 TC = 15 TC nợ ≤ 24


class Command(BaseCommand):
    help = 'Thêm sinh viên Phan Nguyễn Hoàng Hân với điểm ngẫu nhiên'

    def handle(self, *args, **kwargs):
        mssv = '110122003'
        ho_ten = 'Phan Nguyễn Hoàng Hân'
        email = 'phannguyenhoanghan@gmail.com'

        # 1. Ngành + Lớp
        nganh, _ = Nganh.objects.get_or_create(
            ma_nganh='CNTT', defaults={'ten_nganh': 'Công nghệ thông tin'}
        )
        lop_obj, _ = Lop.objects.get_or_create(
            ten_lop='DA22TTA',
            defaults={'nganh': nganh, 'khoa': 'Công nghệ thông tin'}
        )

        # 2. Tài khoản
        sv_user, created = User.objects.get_or_create(
            username=mssv,
            defaults={'full_name': ho_ten, 'email': email, 'role': 'sinhvien'}
        )
        if created:
            sv_user.set_password(mssv)
            sv_user.save()
            self.stdout.write(f'✓ Tạo tài khoản: {mssv} / {mssv}')
        else:
            self.stdout.write(f'✓ Tài khoản: {mssv}')

        # 3. Sinh viên
        sv, _ = SinhVien.objects.update_or_create(
            mssv=mssv,
            defaults={
                'ho_ten': ho_ten, 'email': email, 'nganh': nganh,
                'khoa': 'Công nghệ thông tin', 'lop': lop_obj,
                'trang_thai': 'dang_hoc', 'user': sv_user,
            }
        )
        self.stdout.write(f'✓ Sinh viên: {sv}')
        self.stdout.write(f'✓ 2 HK cảnh báo cố định: {list(HK_CANH_BAO)}')

        # 4. Tạo kết quả học tập
        kq_count = 0
        mon_f_per_hk = {}  # lưu các môn F của từng HK cảnh báo

        for (ky, nam) in HK_ORDER:
            if (ky, nam) not in MON_THEO_HK:
                continue
            hk = HocKy.objects.filter(ky=ky, nam_hoc=nam).first()
            if not hk:
                self.stdout.write(f'  Không tìm thấy HK{ky}-{nam}')
                continue

            ma_mhs = MON_THEO_HK[(ky, nam)]
            la_hk_cb = (ky, nam) in HK_CANH_BAO

            if la_hk_cb:
                # Lấy danh sách môn và tính tổng TC
                mon_list = []
                for ma in ma_mhs:
                    mh = MonHoc.objects.filter(ma_mh=ma).first()
                    if mh:
                        mon_list.append(mh)
                tc_total = sum(m.so_tc for m in mon_list)

                # Chọn môn F sao cho tổng TC > 50% TC đăng ký nhưng ≤ 24
                # Sắp xếp theo TC giảm dần để chọn ít môn nhất mà đủ >50%
                mon_list_sorted = sorted(mon_list, key=lambda m: m.so_tc, reverse=True)
                mon_f = []
                tc_f_acc = 0
                nguong = tc_total * 0.5
                for mh_item in mon_list_sorted:
                    if tc_f_acc <= nguong:
                        mon_f.append(mh_item)
                        tc_f_acc += mh_item.so_tc
                    if tc_f_acc > nguong and tc_f_acc <= 24:
                        break

                # Đảm bảo không vượt 24 TC nợ
                while tc_f_acc > 24 and mon_f:
                    removed = mon_f.pop()
                    tc_f_acc -= removed.so_tc

                mon_f_set = set(m.pk for m in mon_f)
                tc_f = sum(m.so_tc for m in mon_f)
                tc_total = sum(m.so_tc for m in mon_list)
                self.stdout.write(
                    f'  HK{ky}-{nam}: {len(mon_f)} môn F ({tc_f}/{tc_total} TC = '
                    f'{tc_f/tc_total*100:.0f}%)'
                )

                for mh in mon_list:
                    if mh.pk in mon_f_set:
                        # Điểm F: rất thấp để ĐTBCHK < 1.0
                        qt  = round(random.uniform(0.0, 1.5), 1)
                        thi = round(random.uniform(0.0, 1.5), 1)
                    else:
                        # Điểm đạt bình thường
                        qt  = round(random.uniform(5.5, 9.5), 1)
                        thi = round(random.uniform(5.5, 9.5), 1)
                    tk = round((qt + thi) / 2, 2)
                    KetQuaHocTap.objects.update_or_create(
                        sinh_vien=sv, mon_hoc=mh, hoc_ky=hk, lan_hoc=1,
                        defaults={'diem_qt': qt, 'diem_thi': thi, 'diem_tk': tk}
                    )
                    kq_count += 1

                mon_f_per_hk[(ky, nam)] = mon_f

            else:
                # HK bình thường: tất cả đạt
                for ma in ma_mhs:
                    mh = MonHoc.objects.filter(ma_mh=ma).first()
                    if not mh:
                        continue
                    qt  = round(random.uniform(5.5, 9.5), 1)
                    thi = round(random.uniform(5.5, 9.5), 1)
                    tk  = round((qt + thi) / 2, 2)
                    KetQuaHocTap.objects.update_or_create(
                        sinh_vien=sv, mon_hoc=mh, hoc_ky=hk, lan_hoc=1,
                        defaults={'diem_qt': qt, 'diem_thi': thi, 'diem_tk': tk}
                    )
                    kq_count += 1

        # 5. Thêm lần học 2 (đạt) cho các môn F → TC nợ về 0
        for (ky, nam), mon_f_list in mon_f_per_hk.items():
            hk = HocKy.objects.filter(ky=ky, nam_hoc=nam).first()
            for mh in mon_f_list:
                qt  = round(random.uniform(5.5, 8.5), 1)
                thi = round(random.uniform(5.5, 8.5), 1)
                tk  = round((qt + thi) / 2, 2)
                KetQuaHocTap.objects.update_or_create(
                    sinh_vien=sv, mon_hoc=mh, hoc_ky=hk, lan_hoc=2,
                    defaults={'diem_qt': qt, 'diem_thi': thi, 'diem_tk': tk}
                )
                kq_count += 1

        self.stdout.write(f'✓ Tổng kết quả học tập: {kq_count}')

        # Kiểm tra TC nợ thực tế
        from results.utils import tinh_tc_no_dong
        tc_no = tinh_tc_no_dong(sv)
        self.stdout.write(f'  TC nợ đọng thực tế: {tc_no} TC (phải ≤ 24)')

        # 6. Kiểm tra và tạo cảnh báo theo thứ tự HK tăng dần
        cb_count = 0
        so_lan_lien_tiep = 0
        for (ky, nam) in HK_ORDER:
            hk = HocKy.objects.filter(ky=ky, nam_hoc=nam).first()
            if not hk:
                continue
            co_canh_bao, ly_do = kiem_tra_canh_bao(sv, hk)
            if co_canh_bao:
                so_lan_lien_tiep += 1
                muc = 'buoc_thoi_hoc' if so_lan_lien_tiep > 2 else 'canh_bao'
                if so_lan_lien_tiep > 2:
                    ly_do = f'Bị cảnh báo học vụ {so_lan_lien_tiep} lần liên tiếp (Buộc thôi học). ' + ly_do
                CanhBaoHocVu.objects.update_or_create(
                    sinh_vien=sv, hoc_ky=hk,
                    defaults={
                        'muc_canh_bao': muc, 'ly_do': ly_do,
                        'trang_thai': 'moi', 'so_lan_canh_bao': so_lan_lien_tiep,
                    }
                )
                cb_count += 1
                self.stdout.write(f'  ⚠️  HK{ky}-{nam} [{muc}]: {ly_do[:80]}')
                if muc == 'buoc_thoi_hoc':
                    sv.trang_thai = 'dinh_chi'; sv.save()
                elif sv.trang_thai == 'dang_hoc':
                    sv.trang_thai = 'canh_bao'; sv.save()
            else:
                so_lan_lien_tiep = 0

        self.stdout.write(f'✓ Tổng cảnh báo: {cb_count}')
        if cb_count != 2:
            self.stdout.write(self.style.WARNING(
                f'⚠️  Tạo được {cb_count} cảnh báo (mục tiêu: 2).'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Hoàn thành!\n'
            f'  Tài khoản: {mssv} / {mssv}\n'
            f'  Sinh viên: {ho_ten} | Lớp: DA22TTA'
        ))
