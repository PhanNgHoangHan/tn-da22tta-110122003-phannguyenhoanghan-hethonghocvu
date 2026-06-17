from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from students.models import SinhVien, MonHoc, HocKy
from results.models import KetQuaHocTap

class GPACalculationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create user & student
        self.user = CustomUser.objects.create_user(
            username='sv1', password='password', role='sinhvien'
        )
        self.sv = SinhVien.objects.create(
            user=self.user, mssv='110122001', ho_ten='Nguyen Van A', khoa='K2022'
        )
        
        # Create semesters in the same year: 2022-2023
        self.hk1 = HocKy.objects.create(ky='1', nam_hoc='2022-2023')
        self.hk2 = HocKy.objects.create(ky='2', nam_hoc='2022-2023')
        
        # Create subjects with different credits
        # Subject 1 (4 credits) in HK1
        self.mh1 = MonHoc.objects.create(ma_mh='MH01', ten_mh='Mon 1', so_tc=4)
        # Subject 2 (2 credits) in HK2
        self.mh2 = MonHoc.objects.create(ma_mh='MH02', ten_mh='Mon 2', so_tc=2)
        # Subject 3 (2 credits) in HK2 - Physical Education starting with 19
        self.mh3 = MonHoc.objects.create(ma_mh='19100', ten_mh='The chat', so_tc=2)
        
        # Add grades
        # HK1: grade 8.0, 4 credits => 8.0 * 4 = 32.0. GPA = 8.0 (diem_he4 = 3.5)
        # HK2: grade 5.0, 2 credits => 5.0 * 2 = 10.0. GPA = 5.0 (diem_he4 = 1.5)
        # HK2 PhysEd: grade 9.0, 2 credits => Excluded from GPA
        # Weighted Year GPA system 10 = (32.0 + 10.0) / 6 = 7.00
        # Weighted Year GPA system 4 = ((3.5 * 4) + (1.5 * 2)) / 6 = (14.0 + 3.0) / 6 = 2.83
        
        self.kq1 = KetQuaHocTap.objects.create(
            sinh_vien=self.sv, mon_hoc=self.mh1, hoc_ky=self.hk1,
            diem_qt=8.0, diem_thi=8.0, diem_tk=8.0, lan_hoc=1
        )
        self.kq2 = KetQuaHocTap.objects.create(
            sinh_vien=self.sv, mon_hoc=self.mh2, hoc_ky=self.hk2,
            diem_qt=5.0, diem_thi=5.0, diem_tk=5.0, lan_hoc=1
        )
        self.kq3 = KetQuaHocTap.objects.create(
            sinh_vien=self.sv, mon_hoc=self.mh3, hoc_ky=self.hk2,
            diem_qt=9.0, diem_thi=9.0, diem_tk=9.0, lan_hoc=1
        )
        
    def test_weighted_gpa_calculation_in_view(self):
        self.client.login(username='sv1', password='password')
        response = self.client.get(reverse('results:ketqua_list'))
        
        self.assertEqual(response.status_code, 200)
        
        # Retrieve context data
        theo_nam_sv = response.context['theo_nam_sv']
        toan_khoa = response.context['toan_khoa']
        
        self.assertIn('2022-2023', theo_nam_sv)
        
        # HK1 cumulative stats:
        hk1_key = str(self.hk1)
        self.assertIn(hk1_key, theo_nam_sv['2022-2023'])
        hk1_data = theo_nam_sv['2022-2023'][hk1_key]
        self.assertEqual(hk1_data['dtbctl_10'], 8.00)
        self.assertEqual(hk1_data['dtbctl_4'], 3.50)
        self.assertEqual(hk1_data['tc_tl'], 4)
        
        # HK2 cumulative stats:
        hk2_key = str(self.hk2)
        self.assertIn(hk2_key, theo_nam_sv['2022-2023'])
        hk2_data = theo_nam_sv['2022-2023'][hk2_key]
        self.assertEqual(hk2_data['dtbctl_10'], 7.00)
        self.assertEqual(hk2_data['dtbctl_4'], 2.83)
        self.assertEqual(hk2_data['tc_tl'], 8)
        
        # Cumulative/toan_khoa GPA should also be weighted and exclude PhysEd
        self.assertEqual(toan_khoa['dtb_10'], 7.00)
        self.assertEqual(toan_khoa['dtb_4'], 2.83)

    def test_gdefense_included_gphysed_excluded(self):
        user2 = CustomUser.objects.create_user(
            username='sv2', password='password', role='sinhvien'
        )
        sv2 = SinhVien.objects.create(
            user=user2, mssv='110122002', ho_ten='Nguyen Van B', khoa='K2022'
        )
        mh_reg = MonHoc.objects.create(ma_mh='REG01', ten_mh='Mon thuong', so_tc=3)
        mh_def = MonHoc.objects.create(ma_mh='190081_test', ten_mh='GDQP', so_tc=3)
        mh_pe = MonHoc.objects.create(ma_mh='191001_test', ten_mh='GDTC', so_tc=2)
        
        KetQuaHocTap.objects.create(
            sinh_vien=sv2, mon_hoc=mh_reg, hoc_ky=self.hk1,
            diem_qt=8.0, diem_thi=8.0, diem_tk=8.0, lan_hoc=1
        )
        KetQuaHocTap.objects.create(
            sinh_vien=sv2, mon_hoc=mh_def, hoc_ky=self.hk1,
            diem_qt=7.0, diem_thi=7.0, diem_tk=7.0, lan_hoc=1
        )
        KetQuaHocTap.objects.create(
            sinh_vien=sv2, mon_hoc=mh_pe, hoc_ky=self.hk1,
            diem_qt=9.0, diem_thi=9.0, diem_tk=9.0, lan_hoc=1
        )
        
        from results.utils import tinh_dtbchk
        dtb_10, dtb_4, tc_hk, tc_dat = tinh_dtbchk(sv2, self.hk1)
        self.assertEqual(dtb_10, 7.50)
        self.assertEqual(dtb_4, 3.25)
        self.assertEqual(tc_hk, 8)
        self.assertEqual(tc_dat, 8)
