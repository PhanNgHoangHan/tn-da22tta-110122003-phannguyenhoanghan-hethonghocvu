import os
import sys
import django

# Add the project path to sys.path
sys.path.append(r'c:\Users\PC MSI\Downloads\HH\DoAnTotNghiep\DB_CBHV')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from students.models import MonHoc, Nganh

nganh_cntt = Nganh.objects.filter(ma_nganh='CNTT').first()
if nganh_cntt:
    count = MonHoc.objects.all().update(nganh=nganh_cntt)
    print(f"SUCCESS: Associated {count} subjects with CNTT major.")
else:
    print("ERROR: CNTT major not found!")
