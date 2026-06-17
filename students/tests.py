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
