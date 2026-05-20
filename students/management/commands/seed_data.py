"""
Lệnh tạo dữ liệu mẫu cho hệ thống.
Chạy: python manage.py seed_data
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from students.models import Nganh, Lop, SinhVien, HocKy, MonHoc
from results.models import KetQuaHocTap
from academic_warnings.models import CanhBaoHocVu
from results.utils import kiem_tra_canh_bao

User = get_user_model()


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho hệ thống'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang tạo dữ liệu mẫu...')

        # 1. Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@school.edu.vn', 'admin123',
                                           full_name='Quản trị viên', role='admin')
            self.stdout.write('✓ Tạo admin (admin/admin123)')

        # 2. Giáo vụ
        if not User.objects.filter(username='giaovu1').exists():
            User.objects.create_user('giaovu1', 'giaovu@school.edu.vn', 'giaovu123',
                                      full_name='Nguyễn Thị Giáo Vụ', role='giaovu')
            self.stdout.write('✓ Tạo giáo vụ (giaovu1/giaovu123)')

        # 3. Cố vấn học tập - mỗi cố vấn phụ trách 1 lớp
        covan_data = [
            ('Trần Văn Cố Vấn A', 'covan1'),
            ('Lê Thị Cố Vấn B', 'covan2'),
            ('Phạm Văn Cố Vấn C', 'covan3'),
            ('Nguyễn Thị Cố Vấn D', 'covan4'),
        ]
        covan_users = []
        for name, username in covan_data:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, f'{username}@school.edu.vn', 'covan123',
                                              full_name=name, role='covan')
                self.stdout.write(f'✓ Tạo cố vấn ({username}/covan123)')
            else:
                u = User.objects.get(username=username)
            covan_users.append(u)

        # 4. Ngành học
        nganhs_data = [
            ('CNTT', 'Công nghệ thông tin'),
            ('KTPM', 'Kỹ thuật phần mềm'),
            ('HTTT', 'Hệ thống thông tin'),
            ('KHMT', 'Khoa học máy tính'),
        ]
        nganhs = []
        for ma, ten in nganhs_data:
            n, _ = Nganh.objects.get_or_create(ma_nganh=ma, defaults={'ten_nganh': ten})
            nganhs.append(n)
        self.stdout.write(f'✓ Tạo {len(nganhs)} ngành học')

        # 5. Học kỳ (theo thứ tự thời gian tăng dần)
        hockys_data = [
            ('1', '2022-2023', False),
            ('2', '2022-2023', False),
            ('1', '2023-2024', False),
            ('2', '2023-2024', False),
            ('1', '2024-2025', True),
        ]
        hockys = []
        for ky, nam, hien_tai in hockys_data:
            hk, _ = HocKy.objects.get_or_create(ky=ky, nam_hoc=nam,
                                                  defaults={'la_hien_tai': hien_tai})
            hockys.append(hk)
        self.stdout.write(f'✓ Tạo {len(hockys)} học kỳ')

        # 6. Môn học
        monhocs_data = [
            ('MATH101', 'Toán cao cấp 1', 3, 'dai_cuong'),
            ('MATH102', 'Toán cao cấp 2', 3, 'dai_cuong'),
            ('PHYS101', 'Vật lý đại cương', 3, 'dai_cuong'),
            ('PROG101', 'Lập trình cơ bản', 3, 'chuyen_nganh'),
            ('PROG201', 'Lập trình hướng đối tượng', 3, 'chuyen_nganh'),
            ('DB101', 'Cơ sở dữ liệu', 3, 'chuyen_nganh'),
            ('NET101', 'Mạng máy tính', 3, 'chuyen_nganh'),
            ('OS101', 'Hệ điều hành', 3, 'chuyen_nganh'),
            ('AI101', 'Trí tuệ nhân tạo', 3, 'tu_chon'),
            ('WEB101', 'Lập trình web', 3, 'tu_chon'),
            ('SE101', 'Kỹ thuật phần mềm', 3, 'chuyen_nganh'),
            ('ENG101', 'Tiếng Anh 1', 3, 'bat_buoc'),
        ]
        monhocs = []
        for ma, ten, tc, loai in monhocs_data:
            mh, _ = MonHoc.objects.get_or_create(ma_mh=ma, defaults={'ten_mh': ten, 'so_tc': tc, 'loai': loai})
            monhocs.append(mh)
        self.stdout.write(f'✓ Tạo {len(monhocs)} môn học')

        # 7. Tạo lớp và sinh viên
        # Mỗi cố vấn phụ trách đúng 1 lớp (OneToOne)
        lop_config = [
            ('CNTT21A', 0, 0, list(range(1,  9))),
            ('KTPM21A', 1, 1, list(range(9,  17))),
            ('HTTT21A', 2, 2, list(range(17, 24))),
            ('KHMT21A', 3, 3, list(range(24, 31))),
        ]

        sv_count = 0
        for ten_lop, nganh_idx, covan_idx, sv_indices in lop_config:
            nganh = nganhs[nganh_idx]
            covan = covan_users[covan_idx]
            # Tạo lớp với cố vấn phụ trách (OneToOne)
            lop_obj, _ = Lop.objects.get_or_create(
                ten_lop=ten_lop,
                defaults={'nganh': nganh, 'khoa': 'K2021', 'covan': covan}
            )
            # Đảm bảo covan đúng
            if lop_obj.covan != covan:
                lop_obj.covan = covan
                lop_obj.save()

            for i in sv_indices:
                mssv = f'SV{2021000 + i:07d}'
                if SinhVien.objects.filter(mssv=mssv).exists():
                    continue

                sv_user = None
                if i <= 3:
                    uname = f'sv{i:03d}'
                    if not User.objects.filter(username=uname).exists():
                        sv_user = User.objects.create_user(
                            uname, f'{uname}@student.edu.vn', 'sv123',
                            full_name=f'Sinh Viên {i:02d}', role='sinhvien')
                    else:
                        sv_user = User.objects.get(username=uname)

                sv = SinhVien.objects.create(
                    mssv=mssv,
                    ho_ten=f'Sinh Viên {i:02d}',
                    email=f'sv{i:03d}@student.edu.vn',
                    nganh=nganh,
                    khoa='K2021',
                    lop=lop_obj,
                    covan=covan,
                    trang_thai='dang_hoc',
                    user=sv_user,
                )
                sv_count += 1

                # Tạo kết quả học tập cho 4 HK đầu
                for hk in hockys[:4]:
                    mhs_hk = random.sample(monhocs, min(5, len(monhocs)))
                    for mh in mhs_hk:
                        # SV 28-30: điểm rất thấp → vi phạm nhiều điều kiện
                        if i >= 28:
                            diem_qt  = round(random.uniform(0.0, 1.5), 1)
                            diem_thi = round(random.uniform(0.0, 1.5), 1)
                        elif i >= 24:
                            diem_qt  = round(random.uniform(1.5, 3.5), 1)
                            diem_thi = round(random.uniform(1.5, 3.5), 1)
                        elif i >= 19:
                            diem_qt  = round(random.uniform(4.0, 6.5), 1)
                            diem_thi = round(random.uniform(4.0, 6.5), 1)
                        else:
                            diem_qt  = round(random.uniform(6.0, 9.5), 1)
                            diem_thi = round(random.uniform(6.0, 9.5), 1)
                        diem_tk = round((diem_qt + diem_thi) / 2, 2)
                        KetQuaHocTap.objects.get_or_create(
                            sinh_vien=sv, mon_hoc=mh, hoc_ky=hk, lan_hoc=1,
                            defaults={'diem_qt': diem_qt, 'diem_thi': diem_thi, 'diem_tk': diem_tk}
                        )

        self.stdout.write(f'✓ Tạo {sv_count} sinh viên với kết quả học tập')

        # 8. Kiểm tra và tạo cảnh báo
        # Duyệt theo thứ tự HK tăng dần để đếm lần cảnh báo liên tiếp chính xác
        cb_count = 0
        for sv in SinhVien.objects.all():
            so_lan_lien_tiep = 0
            for hk in hockys[:4]:  # HK đã có kết quả, theo thứ tự cũ → mới
                muc, ly_do = kiem_tra_canh_bao(sv, hk)
                if muc:
                    so_lan_lien_tiep += 1
                    # Nếu đã cảnh báo > 2 lần liên tiếp → buộc thôi học
                    if so_lan_lien_tiep > 2:
                        muc = 'buoc_thoi_hoc'
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
                    cb_count += 1

                    # Cập nhật trạng thái SV
                    if muc == 'buoc_thoi_hoc':
                        sv.trang_thai = 'dinh_chi'
                        sv.save()
                    elif sv.trang_thai == 'dang_hoc':
                        sv.trang_thai = 'canh_bao'
                        sv.save()
                else:
                    # HK không cảnh báo → reset đếm liên tiếp
                    so_lan_lien_tiep = 0

        self.stdout.write(f'✓ Tạo {cb_count} cảnh báo học vụ')
        self.stdout.write(self.style.SUCCESS('\n✅ Hoàn thành! Tài khoản mẫu:'))
        self.stdout.write('  admin / admin123 (Quản trị viên)')
        self.stdout.write('  giaovu1 / giaovu123 (Giáo vụ)')
        self.stdout.write('  covan1 / covan123 (Cố vấn học tập - lớp CNTT21A)')
        self.stdout.write('  covan2 / covan123 (Cố vấn học tập - lớp KTPM21A)')
        self.stdout.write('  sv001 / sv123 (Sinh viên)')
