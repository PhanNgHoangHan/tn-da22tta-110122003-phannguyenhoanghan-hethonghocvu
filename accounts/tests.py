from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from accounts.models import CustomUser
import time


class ForgotPasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@tvu.edu.vn',
            password='oldpassword123',
            full_name='Test User',
            role='sinhvien'
        )

    def test_forgot_password_view_get(self):
        response = self.client.get(reverse('accounts:forgot_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/forgot_password.html')

    def test_forgot_password_success(self):
        # Post valid user info
        response = self.client.post(reverse('accounts:forgot_password'), {
            'username': 'testuser',
            'email': 'testuser@tvu.edu.vn',
            'send_method': 'email'
        })
        # Should redirect to reset password
        self.assertRedirects(response, reverse('accounts:reset_password'))
        
        # Should check session variables
        session = self.client.session
        self.assertEqual(session.get('password_reset_username'), 'testuser')
        self.assertIsNotNone(session.get('password_reset_code'))
        self.assertTrue(len(session.get('password_reset_code')) == 6)
        self.assertGreater(session.get('password_reset_expiry'), time.time())

        # Should send an email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[Hệ thống Quản lý Học vụ TVU] Mã xác minh đặt lại mật khẩu')
        self.assertIn('testuser', mail.outbox[0].body)
        self.assertIn(session.get('password_reset_code'), mail.outbox[0].body)

    def test_forgot_password_invalid_credentials(self):
        # Post invalid info
        response = self.client.post(reverse('accounts:forgot_password'), {
            'username': 'nonexistent',
            'email': 'wrong@tvu.edu.vn',
            'send_method': 'email'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Không tìm thấy tài khoản")
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_password_no_session(self):
        # Accessing reset password directly without session should redirect to forgot password
        response = self.client.get(reverse('accounts:reset_password'))
        self.assertRedirects(response, reverse('accounts:forgot_password'))

    def test_reset_password_success(self):
        # Trigger forgot password to set session variables
        self.client.post(reverse('accounts:forgot_password'), {
            'username': 'testuser',
            'email': 'testuser@tvu.edu.vn',
            'send_method': 'email'
        })
        
        session = self.client.session
        otp_code = session.get('password_reset_code')

        # Post correct OTP and matching new passwords
        response = self.client.post(reverse('accounts:reset_password'), {
            'code': otp_code,
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })
        self.assertRedirects(response, reverse('accounts:login'))

        # Check that user password has updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

        # Check session is cleared
        session = self.client.session
        self.assertNotIn('password_reset_code', session)
        self.assertNotIn('password_reset_username', session)

    def test_reset_password_incorrect_code(self):
        self.client.post(reverse('accounts:forgot_password'), {
            'username': 'testuser',
            'email': 'testuser@tvu.edu.vn',
            'send_method': 'email'
        })
        
        # Post wrong code
        response = self.client.post(reverse('accounts:reset_password'), {
            'code': '000000',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mã xác minh không chính xác")
        
        # Password should not change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('newpassword123'))

    def test_reset_password_mismatched_passwords(self):
        self.client.post(reverse('accounts:forgot_password'), {
            'username': 'testuser',
            'email': 'testuser@tvu.edu.vn',
            'send_method': 'email'
        })
        
        session = self.client.session
        otp_code = session.get('password_reset_code')

        # Post mismatched passwords
        response = self.client.post(reverse('accounts:reset_password'), {
            'code': otp_code,
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Xác nhận mật khẩu mới không khớp")

        # Password should not change
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('newpassword123'))
