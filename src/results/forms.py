from django import forms
from .models import KetQuaHocTap
from students.models import SinhVien, MonHoc, HocKy


class KetQuaForm(forms.ModelForm):
    class Meta:
        model = KetQuaHocTap
        fields = ['sinh_vien', 'mon_hoc', 'hoc_ky', 'diem_qt', 'diem_thi', 'diem_tk', 'lan_hoc', 'ghi_chu']
        widgets = {
            'sinh_vien': forms.Select(attrs={'class': 'form-select'}),
            'mon_hoc': forms.Select(attrs={'class': 'form-select'}),
            'hoc_ky': forms.Select(attrs={'class': 'form-select'}),
            'diem_qt': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '10'}),
            'diem_thi': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '10'}),
            'diem_tk': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '10'}),
            'lan_hoc': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'ghi_chu': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ImportDiemForm(forms.Form):
    file = forms.FileField(
        label='File CSV/Excel',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'})
    )


class FilterKetQuaForm(forms.Form):
    sinh_vien = forms.ModelChoiceField(
        queryset=SinhVien.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Sinh viên', empty_label='-- Tất cả --'
    )
    hoc_ky = forms.ModelChoiceField(
        queryset=HocKy.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Học kỳ', empty_label='-- Tất cả --'
    )
    mon_hoc = forms.ModelChoiceField(
        queryset=MonHoc.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Môn học', empty_label='-- Tất cả --'
    )
