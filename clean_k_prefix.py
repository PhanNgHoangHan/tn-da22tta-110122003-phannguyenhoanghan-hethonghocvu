import os
import sys
import django

# Add the project path to sys.path
sys.path.append(r'c:\Users\PC MSI\Downloads\HH\DoAnTotNghiep\DB_CBHV')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from students.models import SinhVien, Lop

cleaned_sv = 0
cleaned_lop = 0

for sv in SinhVien.objects.all():
    if sv.khoa.startswith('K') or sv.khoa.startswith('k'):
        sv.khoa = sv.khoa[1:]
        sv.save()
        cleaned_sv += 1
        
for lop in Lop.objects.all():
    if lop.khoa.startswith('K') or lop.khoa.startswith('k'):
        lop.khoa = lop.khoa[1:]
        lop.save()
        cleaned_lop += 1

print(f"SUCCESS: Cleaned {cleaned_sv} students and {cleaned_lop} classes.")
