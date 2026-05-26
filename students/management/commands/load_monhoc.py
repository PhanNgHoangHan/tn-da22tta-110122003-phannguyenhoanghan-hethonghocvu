"""
Lệnh nạp môn học và học kỳ thực tế từ dữ liệu bảng điểm.
Chạy: python manage.py load_monhoc
"""
from django.core.management.base import BaseCommand
from students.models import MonHoc, HocKy


HOCKY_DATA = [
    ('1', '2022-2023', False),
    ('2', '2022-2023', False),
    ('1', '2023-2024', False),
    ('2', '2023-2024', False),
    ('1', '2024-2025', False),
    ('2', '2024-2025', False),
    ('1', '2025-2026', True),
    ('2', '2025-2026', False),
]

# (ma_mh, ten_mh, so_tc, loai)
MONHOC_DATA = [
    # HK1 2022-2023
    ('110001', 'Đại số tuyến tính', 2, 'dai_cuong'),
    ('110042', 'Vi tích phân A1', 3, 'dai_cuong'),
    ('180050', 'Triết học Mác - Lênin', 3, 'dai_cuong'),
    ('190081', 'Học phần I: Đường lối QP và an ninh của ĐCSVN', 3, 'bat_buoc'),
    ('190082', 'Học phần II: Công tác quốc phòng và an ninh', 2, 'bat_buoc'),
    ('190083', 'Học phần III: Quân sự chung', 1, 'bat_buoc'),
    ('190084', 'Học phần IV: Kỹ thuật chiến đấu bộ binh và chiến thuật', 2, 'bat_buoc'),
    ('191', 'Giáo dục thể chất 1 (Điền kinh)', 1, 'bat_buoc'),
    ('220092', 'Nhập môn công nghệ thông tin', 2, 'chuyen_nganh'),
    ('220228', 'Kỹ thuật lập trình', 4, 'chuyen_nganh'),
    ('410291', 'Anh văn không chuyên 1', 3, 'bat_buoc'),
    ('450015', 'Pháp luật đại cương', 2, 'dai_cuong'),
    # HK2 2022-2023
    ('110003', 'Toán rời rạc', 2, 'dai_cuong'),
    ('170011', 'Tiếng Việt thực hành', 2, 'dai_cuong'),
    ('180051', 'Kinh tế chính trị Mác - Lênin', 2, 'dai_cuong'),
    ('192.08', 'Giáo dục thể chất 2 (bóng đá)', 1, 'bat_buoc'),
    ('220233', 'Đại số đại cương', 2, 'dai_cuong'),
    ('220234', 'Cấu trúc dữ liệu và giải thuật', 4, 'chuyen_nganh'),
    ('290000', 'Phương pháp NC khoa học', 2, 'dai_cuong'),
    ('410292', 'Anh văn không chuyên 2', 4, 'bat_buoc'),
    ('640033', 'Logic học đại cương', 2, 'dai_cuong'),
    # HK1 2023-2024
    ('110002', 'Vi tích phân A2', 2, 'dai_cuong'),
    ('110079', 'Kiến trúc máy tính', 3, 'chuyen_nganh'),
    ('180052', 'Chủ nghĩa xã hội khoa học', 2, 'dai_cuong'),
    ('193.15', 'Giáo dục thể chất 3 (bóng chuyền)', 1, 'bat_buoc'),
    ('220096', 'Cơ sở dữ liệu', 3, 'chuyen_nganh'),
    ('220099', 'Lập trình hướng đối tượng', 3, 'chuyen_nganh'),
    ('220100', 'Lý thuyết đồ thị', 3, 'chuyen_nganh'),
    ('410293', 'Anh văn không chuyên 3', 3, 'bat_buoc'),
    # HK2 2023-2024
    ('110057', 'Quy hoạch tuyến tính', 2, 'dai_cuong'),
    ('180001', 'Tư tưởng Hồ Chí Minh', 2, 'dai_cuong'),
    ('220018', 'Mạng máy tính', 3, 'chuyen_nganh'),
    ('220101', 'Hệ điều hành', 3, 'chuyen_nganh'),
    ('220236', 'Thiết kế Web', 3, 'chuyen_nganh'),
    ('220237', 'Lý thuyết xếp hàng', 2, 'chuyen_nganh'),
    ('220250', 'Anh văn chuyên ngành công nghệ thông tin', 3, 'bat_buoc'),
    ('410294', 'Anh văn không chuyên 4', 3, 'bat_buoc'),
    # HK1 2024-2025
    ('180053', 'Lịch sử Đảng Cộng sản Việt Nam', 2, 'dai_cuong'),
    ('220065', 'Thương mại điện tử', 3, 'chuyen_nganh'),
    ('220086', 'Lập trình ứng dụng trên Windows', 3, 'chuyen_nganh'),
    ('220239', 'Phân tích và thiết kế hệ thống thông tin', 3, 'chuyen_nganh'),
    ('220265', 'Thực tập đồ án cơ sở ngành', 3, 'chuyen_nganh'),
    ('220267', 'Điện toán đám mây', 3, 'chuyen_nganh'),
    ('320045', 'Thống kê và phân tích dữ liệu', 3, 'chuyen_nganh'),
    # HK2 2024-2025
    ('220055', 'Công nghệ phần mềm', 3, 'chuyen_nganh'),
    ('220060', 'Hệ quản trị cơ sở dữ liệu', 3, 'chuyen_nganh'),
    ('220071', 'Lập trình thiết bị di động', 3, 'chuyen_nganh'),
    ('220126', 'An toàn và bảo mật thông tin', 3, 'chuyen_nganh'),
    ('220242', 'Cơ sở trí tuệ nhân tạo', 3, 'chuyen_nganh'),
    ('220269', 'Khai phá dữ liệu', 3, 'chuyen_nganh'),
    ('420000', 'Kỹ thuật XD & ban hành văn bản', 2, 'bat_buoc'),
    # HK1 2025-2026
    ('220057', 'Xử lý ảnh', 3, 'chuyen_nganh'),
    ('220078', 'Quản trị dự án công nghệ thông tin', 3, 'chuyen_nganh'),
    ('220120', 'Xây dựng phần mềm hướng đối tượng', 3, 'chuyen_nganh'),
    ('220243', 'Phát triển ứng dụng Web với mã nguồn mở', 3, 'chuyen_nganh'),
    ('220245', 'Tương tác người - máy', 3, 'chuyen_nganh'),
    ('220266', 'Thực tập đồ án chuyên ngành', 3, 'chuyen_nganh'),
    ('220268', 'Phát triển ứng dụng hướng dịch vụ', 3, 'chuyen_nganh'),
    # HK2 2025-2026
    ('2', 'Đồ án tốt nghiệp', 7, 'chuyen_nganh'),
    ('160038', 'Thực tập cuối khóa', 3, 'chuyen_nganh'),
]


class Command(BaseCommand):
    help = 'Nạp môn học và học kỳ thực tế'

    def handle(self, *args, **kwargs):
        # Tạo học kỳ
        hk_count = 0
        for ky, nam, hien_tai in HOCKY_DATA:
            _, created = HocKy.objects.get_or_create(
                ky=ky, nam_hoc=nam,
                defaults={'la_hien_tai': hien_tai}
            )
            if created:
                hk_count += 1
        self.stdout.write(f'✓ Tạo {hk_count} học kỳ mới (tổng: {HocKy.objects.count()})')

        # Tạo môn học (bỏ qua trùng)
        mh_count = 0
        for ma, ten, tc, loai in MONHOC_DATA:
            _, created = MonHoc.objects.get_or_create(
                ma_mh=ma,
                defaults={'ten_mh': ten, 'so_tc': tc, 'loai': loai}
            )
            if created:
                mh_count += 1
        self.stdout.write(f'✓ Tạo {mh_count} môn học mới (tổng: {MonHoc.objects.count()})')
        self.stdout.write(self.style.SUCCESS('✅ Hoàn thành!'))
