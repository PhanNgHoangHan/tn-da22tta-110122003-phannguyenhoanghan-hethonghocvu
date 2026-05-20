from django import forms
from .models import SinhVien, MonHoc, HocKy, Nganh, Lop


class SinhVienForm(forms.ModelForm):
    class Meta:
        model = SinhVien
        fields = ['mssv', 'ho_ten', 'ngay_sinh', 'gioi_tinh', 'email', 'so_dien_thoai',
                  'nganh', 'khoa', 'lop', 'covan', 'trang_thai', 'ngay_nhap_hoc', 'user']
        widgets = {
            'mssv': forms.TextInput(attrs={'class': 'form-control'}),
            'ho_ten': forms.TextInput(attrs={'class': 'form-control'}),
            'ngay_sinh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gioi_tinh': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'so_dien_thoai': forms.TextInput(attrs={'class': 'form-control'}),
            'nganh': forms.Select(attrs={'class': 'form-select'}),
            'khoa': forms.TextInput(attrs={'class': 'form-control'}),
            'lop': forms.Select(attrs={'class': 'form-select'}),
            'covan': forms.Select(attrs={'class': 'form-select'}),
            'trang_thai': forms.Select(attrs={'class': 'form-select'}),
            'ngay_nhap_hoc': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
        }


class MonHocForm(forms.ModelForm):
    class Meta:
        model = MonHoc
        fields = ['ma_mh', 'ten_mh', 'so_tc', 'loai', 'mo_ta']
        widgets = {
            'ma_mh': forms.TextInput(attrs={'class': 'form-control'}),
            'ten_mh': forms.TextInput(attrs={'class': 'form-control'}),
            'so_tc': forms.NumberInput(attrs={'class': 'form-control'}),
            'loai': forms.Select(attrs={'class': 'form-select'}),
            'mo_ta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class HocKyForm(forms.ModelForm):
    class Meta:
        model = HocKy
        fields = ['ky', 'nam_hoc', 'ngay_bat_dau', 'ngay_ket_thuc', 'la_hien_tai']
        widgets = {
            'ky': forms.Select(attrs={'class': 'form-select'}),
            'nam_hoc': forms.TextInput(attrs={'class': 'form-control'}),
            'ngay_bat_dau': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ngay_ket_thuc': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class NganhForm(forms.ModelForm):
    class Meta:
        model = Nganh
        fields = ['ma_nganh', 'ten_nganh']
        widgets = {
            'ma_nganh': forms.TextInput(attrs={'class': 'form-control'}),
            'ten_nganh': forms.TextInput(attrs={'class': 'form-control'}),
        }


class LopForm(forms.ModelForm):
    class Meta:
        model = Lop
        fields = ['ten_lop', 'nganh', 'khoa', 'covan']
        widgets = {
            'ten_lop': forms.TextInput(attrs={'class': 'form-control'}),
            'nganh': forms.Select(attrs={'class': 'form-select'}),
            'khoa': forms.TextInput(attrs={'class': 'form-control'}),
            'covan': forms.Select(attrs={'class': 'form-select'}),
        }


class ImportCSVForm(forms.Form):
    file = forms.FileField(
        label='Chọn file CSV/Excel',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'})
    )
