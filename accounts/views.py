from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserCreateForm, UserEditForm
from .models import CustomUser
import random
import time
from django.core.mail import send_mail
from django.conf import settings


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard:index')
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def user_list(request):
    if not (request.user.is_admin):
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('dashboard:index')
    users = CustomUser.objects.all().order_by('role', 'username')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def user_create(request):
    if not request.user.is_admin:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('dashboard:index')
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Tạo người dùng thành công.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Tạo người dùng'})


@login_required
def user_edit(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('dashboard:index')
    user = get_object_or_404(CustomUser, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cập nhật người dùng thành công.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Chỉnh sửa người dùng'})


@login_required
def user_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('dashboard:index')
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Xóa người dùng thành công.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Đổi mật khẩu thất bại. Vui lòng kiểm tra lại thông tin.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    error_msg = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        user = CustomUser.objects.filter(username=username, email=email).first()
        if user:
            # Generate a 6-digit verification code
            code = f"{random.randint(100000, 999999)}"
            
            # Store in session
            request.session['password_reset_code'] = code
            request.session['password_reset_username'] = username
            request.session['password_reset_expiry'] = time.time() + 600  # 10 minutes
            
            # Send Email
            subject = '[Hệ thống Quản lý Học vụ TVU] Mã xác minh đặt lại mật khẩu'
            html_message = f"""
            <h3>Mã xác minh đặt lại mật khẩu</h3>
            <p>Chào bạn,</p>
            <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản <strong>{username}</strong>.</p>
            <p>Mã xác minh (OTP) của bạn là: <strong style="font-size: 20px; color: #3498db; letter-spacing: 2px;">{code}</strong></p>
            <p>Mã này có hiệu lực trong vòng 10 phút. Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email này.</p>
            <br>
            <p>Trân trọng,<br>Hệ thống Quản lý Học vụ TVU</p>
            """
            
            try:
                send_mail(
                    subject=subject,
                    message=f"Mã xác minh đặt lại mật khẩu của tài khoản {username} là: {code}. Mã có hiệu lực trong vòng 10 phút.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                return redirect('accounts:reset_password')
            except Exception as e:
                error_msg = f"Không thể gửi email xác minh. Chi tiết lỗi: {str(e)}"
        else:
            error_msg = "Không tìm thấy tài khoản với tên đăng nhập và email đã cung cấp."
            
    return render(request, 'accounts/forgot_password.html', {'error_msg': error_msg})


def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
        
    username = request.session.get('password_reset_username')
    session_code = request.session.get('password_reset_code')
    expiry = request.session.get('password_reset_expiry', 0)
    
    if not username or not session_code:
        return redirect('accounts:forgot_password')
        
    error_msg = None
    if request.method == 'POST':
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if time.time() > expiry:
            error_msg = "Mã xác minh đã hết hạn. Vui lòng lấy lại mã mới."
        elif code != session_code:
            error_msg = "Mã xác minh không chính xác."
        elif new_password != confirm_password:
            error_msg = "Xác nhận mật khẩu mới không khớp."
        else:
            user = CustomUser.objects.filter(username=username).first()
            if user:
                user.set_password(new_password)
                user.save()
                
                # Clear session
                request.session.pop('password_reset_code', None)
                request.session.pop('password_reset_username', None)
                request.session.pop('password_reset_expiry', None)
                
                messages.success(request, 'Đặt lại mật khẩu thành công. Vui lòng đăng nhập với mật khẩu mới.')
                return redirect('accounts:login')
            else:
                error_msg = "Người dùng không tồn tại."
                
    return render(request, 'accounts/reset_password.html', {'error_msg': error_msg})

