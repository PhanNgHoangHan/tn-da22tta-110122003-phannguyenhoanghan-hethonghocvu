from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from accounts.models import CustomUser
from students.models import MonHoc, HocKy

class ViewPermissionsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = CustomUser.objects.create_user(username='admin', role='admin', password='password')
        self.covan = CustomUser.objects.create_user(username='covan', role='covan', password='password')
        self.sinhvien = CustomUser.objects.create_user(username='sinhvien', role='sinhvien', password='password')
        
        # Create dummy subject and semester
        self.monhoc = MonHoc.objects.create(ma_mh='MH01', ten_mh='Mon Hoc Test', so_tc=3)
        self.hocky = HocKy.objects.create(ky='1', nam_hoc='2023-2024')

    def test_monhoc_edit_disabled(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('students:monhoc_edit', args=[self.monhoc.pk]))
        self.assertRedirects(response, reverse('students:monhoc_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Chức năng sửa môn học đã bị vô hiệu hóa.' in str(m) for m in messages))

    def test_monhoc_delete_disabled(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('students:monhoc_delete', args=[self.monhoc.pk]))
        self.assertRedirects(response, reverse('students:monhoc_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Chức năng xóa môn học đã bị vô hiệu hóa.' in str(m) for m in messages))

    def test_hocky_edit_disabled(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('students:hocky_edit', args=[self.hocky.pk]))
        self.assertRedirects(response, reverse('students:hocky_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Chức năng sửa học kỳ đã bị vô hiệu hóa.' in str(m) for m in messages))

    def test_covan_and_sinhvien_restrictions(self):
        # Test monhoc_create with covan
        self.client.login(username='covan', password='password')
        response = self.client.get(reverse('students:monhoc_create'))
        self.assertRedirects(response, reverse('dashboard:index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Bạn không có quyền truy cập.' in str(m) for m in messages))

        # Test monhoc_create with sinhvien
        self.client.login(username='sinhvien', password='password')
        response = self.client.get(reverse('students:monhoc_create'))
        self.assertRedirects(response, reverse('dashboard:index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Bạn không có quyền truy cập.' in str(m) for m in messages))

    def test_monhoc_list_default_empty(self):
        from students.models import Nganh
        nganh = Nganh.objects.create(ma_nganh='CNTT', ten_nganh='Cong nghe thong tin')
        
        # Subject 1 (Semester 1)
        self.monhoc.nganh = nganh
        self.monhoc.nam_hoc_ctdt = 1
        self.monhoc.hoc_ky_ctdt = 1
        self.monhoc.save()
        
        # Subject 2 (Semester 3)
        monhoc2 = MonHoc.objects.create(
            ma_mh='MH02', ten_mh='Mon Hoc Test 2', so_tc=2,
            nganh=nganh, nam_hoc_ctdt=2, hoc_ky_ctdt=1
        )
        
        self.client.login(username='admin', password='password')
        
        # Default empty
        response = self.client.get(reverse('students:monhoc_list'))
        self.assertEqual(len(response.context['grouped_monhocs']), 0)
        self.assertContains(response, 'Vui lòng chọn một chương trình đào tạo để xem danh sách môn học.')
        
        # When filtered
        response = self.client.get(reverse('students:monhoc_list'), {'nganh': nganh.pk})
        keys = list(response.context['grouped_monhocs'].keys())
        # Ordered descending: [3, 1]
        self.assertEqual(keys, [3, 1])
        self.assertContains(response, self.monhoc.ten_mh)
        self.assertContains(response, monhoc2.ten_mh)

    def test_weighted_gpa_calculation_in_student_detail(self):
        from results.models import KetQuaHocTap
        from students.models import SinhVien
        
        # Setup student profile linked to a CustomUser
        user = CustomUser.objects.create_user(
            username='sv2', password='password', role='sinhvien'
        )
        # Self.sinhvien has no SinhVien profile by default, let's link or create a new student
        sv = SinhVien.objects.create(
            user=user, mssv='110122002', ho_ten='Nguyen Van B', khoa='K2022'
        )
        
        # Create semesters in 2022-2023
        hk1 = HocKy.objects.create(ky='1', nam_hoc='2022-2023')
        hk2 = HocKy.objects.create(ky='2', nam_hoc='2022-2023')
        
        # Subject 1 (4 credits), Subject 2 (2 credits), Subject 3 (2 credits PhysEd)
        mh1 = MonHoc.objects.create(ma_mh='MH10', ten_mh='Mon 10', so_tc=4)
        mh2 = MonHoc.objects.create(ma_mh='MH20', ten_mh='Mon 20', so_tc=2)
        mh3 = MonHoc.objects.create(ma_mh='19200', ten_mh='The chat', so_tc=2)
        
        # Graded results:
        # HK1: 8.0, 4 credits => 32.0. GPA = 8.0
        # HK2: 5.0, 2 credits => 10.0. GPA = 5.0
        # HK2 PhysEd: 9.0, 2 credits => Excluded from GPA
        # Weighted GPA = 7.00 (system 10), 2.83 (system 4)
        KetQuaHocTap.objects.create(
            sinh_vien=sv, mon_hoc=mh1, hoc_ky=hk1,
            diem_qt=8.0, diem_thi=8.0, diem_tk=8.0, lan_hoc=1
        )
        KetQuaHocTap.objects.create(
            sinh_vien=sv, mon_hoc=mh2, hoc_ky=hk2,
            diem_qt=5.0, diem_thi=5.0, diem_tk=5.0, lan_hoc=1
        )
        KetQuaHocTap.objects.create(
            sinh_vien=sv, mon_hoc=mh3, hoc_ky=hk2,
            diem_qt=9.0, diem_thi=9.0, diem_tk=9.0, lan_hoc=1
        )
        
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('students:sinhvien_detail', args=[sv.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Verify calculated values in context
        ket_qua_theo_nam = response.context['ket_qua_theo_nam']
        self.assertIn('2022-2023', ket_qua_theo_nam)
        
        # HK1 cumulative stats:
        hk1_key = str(hk1)
        self.assertIn(hk1_key, ket_qua_theo_nam['2022-2023'])
        hk1_data = ket_qua_theo_nam['2022-2023'][hk1_key]
        self.assertEqual(hk1_data['dtbctl_10'], 8.00)
        self.assertEqual(hk1_data['dtbctl_4'], 3.50)
        self.assertEqual(hk1_data['tc_tl'], 4)
        
        # HK2 cumulative stats:
        hk2_key = str(hk2)
        self.assertIn(hk2_key, ket_qua_theo_nam['2022-2023'])
        hk2_data = ket_qua_theo_nam['2022-2023'][hk2_key]
        self.assertEqual(hk2_data['dtbctl_10'], 7.00)
        self.assertEqual(hk2_data['dtbctl_4'], 2.83)
        self.assertEqual(hk2_data['tc_tl'], 8)
        
        # Cumulative
        self.assertEqual(response.context['toan_khoa_dtb_10'], 7.00)
        self.assertEqual(response.context['toan_khoa_dtb_4'], 2.83)
