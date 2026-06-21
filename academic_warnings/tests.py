from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from students.models import SinhVien, Lop, Nganh, HocKy, MonHoc
from results.models import KetQuaHocTap
from results.utils import tinh_canh_bao_som
from academic_warnings.models import LichSuGuiCanhBaoSom

class EarlyWarningTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create user accounts
        self.admin = CustomUser.objects.create_user(username='admin', password='password', role='admin')
        self.covan = CustomUser.objects.create_user(username='covan', password='password', role='covan')
        self.sv_user = CustomUser.objects.create_user(username='sv_user', password='password', role='sinhvien')
        
        # Setup course and departments
        self.nganh = Nganh.objects.create(ma_nganh='CNTT', ten_nganh='Cong nghe thong tin')
        self.lop = Lop.objects.create(ten_lop='DA22TTA', nganh=self.nganh, covan=self.covan, khoa='K22')
        
        self.sv = SinhVien.objects.create(
            user=self.sv_user, mssv='110122003', ho_ten='Phan Nguyen Hoang Han', 
            lop=self.lop, nganh=self.nganh, khoa='K22', email='han@student.tvu.edu.vn'
        )
        
        # Create semesters
        self.hk1 = HocKy.objects.create(ky='1', nam_hoc='2023-2024')
        self.hk2 = HocKy.objects.create(ky='2', nam_hoc='2023-2024')
        
        # Create subjects
        self.mh1 = MonHoc.objects.create(ma_mh='MH1', ten_mh='Math', so_tc=4)
        self.mh2 = MonHoc.objects.create(ma_mh='MH2', ten_mh='Physics', so_tc=3)
        self.mh3 = MonHoc.objects.create(ma_mh='MH3', ten_mh='Web Programming', so_tc=3)

    def test_risk_level_safe(self):
        # Math: 8.0 (B+ -> 3.5), Physics: 7.0 (B -> 3.0). Cumulative GPA = (3.5*4 + 3.0*3)/7 = 3.28 >= 2.0 -> Safe
        KetQuaHocTap.objects.create(sinh_vien=self.sv, mon_hoc=self.mh1, hoc_ky=self.hk1, diem_tk=8.0, lan_hoc=1)
        KetQuaHocTap.objects.create(sinh_vien=self.sv, mon_hoc=self.mh2, hoc_ky=self.hk1, diem_tk=7.0, lan_hoc=1)
        
        analysis = tinh_canh_bao_som(self.sv)
        self.assertEqual(analysis['muc_nguy_co'], 'safe')
        self.assertEqual(analysis['muc_nguy_co_display'], 'An toàn')
        self.assertEqual(len(analysis['diem_yeu']), 0) # No weak points

    def test_risk_level_monitor_and_weak_points(self):
        # Math: 5.5 (C -> 2.0). Physics: 5.0 (D+ -> 1.5). Cumulative GPA = (2.0*4 + 1.5*3)/7 = 1.78.
        # But wait, GPA 1.78 is between 1.2 and 1.8, so it will be warning_1.
        # Let's target GPA 1.85: Math: 6.0 (C -> 2.0), Physics: 5.5 (C -> 2.0), but wait, let's just use exact GPA 1.9.
        # GPA = 1.9 (e.g. 1.9 * 7 = 13.3). If Math is 5.5 (C -> 2.0, 4 TC) and Physics is 5.5 (C -> 2.0, 3 TC), GPA = 2.0 (safe).
        # Let's adjust grades:
        # Math: 5.5 (C -> 2.0, 4 TC) -> 8.0 points.
        # Physics: 5.0 (D+ -> 1.5, 3 TC) -> 4.5 points. Total = 12.5. GPA = 12.5 / 7 = 1.78 (warning_1).
        # What if Math is 5.5 (C -> 2.0, 4 TC) and Physics is 5.2 (D+ -> 1.5, 3 TC) -> 2.0 * 4 + 1.5 * 3 = 12.5.
        # Let's set Math: 5.5 (C -> 2.0, 4 TC) and Physics: 5.5 (C -> 2.0, 3 TC) -> 2.0.
        # Let's set Math: 5.5 (C -> 2.0, 4 TC) and Physics: 5.0 (D+ -> 1.5, 3 TC). Total GPA is 1.78. Let's add a 3rd course:
        # Web: 5.0 (D+ -> 1.5, 3 TC). Cumulative GPA = (2.0*4 + 1.5*3 + 1.5*3)/10 = 1.55.
        # To get GPA between 1.8 and 2.0 (monitor):
        # Let Math = 5.5 (C -> 2.0, 4 TC), Physics = 5.5 (C -> 2.0, 3 TC), Web = 5.0 (D+ -> 1.5, 3 TC).
        # GPA = (2.0*4 + 2.0*3 + 1.5*3)/10 = (8 + 6 + 4.5)/10 = 1.85. This is in 1.8 - 2.0 range -> Monitor!
        KetQuaHocTap.objects.create(sinh_vien=self.sv, mon_hoc=self.mh1, hoc_ky=self.hk1, diem_tk=5.5, lan_hoc=1)
        KetQuaHocTap.objects.create(sinh_vien=self.sv, mon_hoc=self.mh2, hoc_ky=self.hk1, diem_tk=5.5, lan_hoc=1)
        KetQuaHocTap.objects.create(sinh_vien=self.sv, mon_hoc=self.mh3, hoc_ky=self.hk1, diem_tk=5.0, lan_hoc=1)
        
        analysis = tinh_canh_bao_som(self.sv)
        self.assertEqual(analysis['muc_nguy_co'], 'monitor')
        self.assertEqual(analysis['muc_nguy_co_display'], 'Theo dõi')
        
        # Weak points should include Web (D+).
        self.assertEqual(len(analysis['diem_yeu']), 1)
        self.assertEqual(analysis['diem_yeu'][0]['ma_mh'], 'MH3')
        self.assertEqual(analysis['diem_yeu'][0]['diem_chu'], 'D+')
        
        # Web (D+ -> 1.5). If improved to A (4.0), improvement is (4.0 - 1.5) * 3 / 10 = 2.5 * 3 / 10 = 0.75.
        self.assertAlmostEqual(analysis['diem_yeu'][0]['improvement'], 0.75)

    def test_risk_level_warning_2(self):
        # Math: 2.0 (F -> 0.0). Physics: 3.0 (F -> 0.0). GPA = 0.0 < 1.2 -> Warning Level 2
        KetQuaHocTap.objects.create(sinh_vien=self.sv, mon_hoc=self.mh1, hoc_ky=self.hk1, diem_tk=2.0, lan_hoc=1)
        KetQuaHocTap.objects.create(sinh_vien=self.sv, mon_hoc=self.mh2, hoc_ky=self.hk1, diem_tk=3.0, lan_hoc=1)
        
        analysis = tinh_canh_bao_som(self.sv)
        self.assertEqual(analysis['muc_nguy_co'], 'warning_2')
        self.assertEqual(analysis['muc_nguy_co_display'], 'Cảnh báo mức 2')
        self.assertEqual(len(analysis['diem_yeu']), 2) # Both are F

    def test_early_warning_views(self):
        # Create a failed grade so they have a weak subject and the simulator renders
        KetQuaHocTap.objects.create(sinh_vien=self.sv, mon_hoc=self.mh1, hoc_ky=self.hk1, diem_tk=3.0, lan_hoc=1)
        
        # Log in as advisor
        self.client.login(username='covan', password='password')
        
        # View list page
        response = self.client.get(reverse('academic_warnings:canhbao_som_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Danh sách cảnh báo sớm')
        
        # View detail page
        response = self.client.get(reverse('academic_warnings:canhbao_som_detail', args=[self.sv.mssv]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Phan Nguyen Hoang Han')
        self.assertContains(response, 'Bảng tính mô phỏng cải thiện GPA')
        
        # Send early warning email view
        email_response = self.client.post(reverse('academic_warnings:canhbao_som_gui_email', args=[self.sv.mssv]))
        self.assertEqual(email_response.status_code, 302) # Redirects back to detail page
        
        # Verify email logs
        self.assertEqual(LichSuGuiCanhBaoSom.objects.filter(sinh_vien=self.sv).count(), 1)

