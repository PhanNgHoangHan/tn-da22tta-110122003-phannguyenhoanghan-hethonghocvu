from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserCreateForm, UserEditForm
from .models import CustomUser


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
