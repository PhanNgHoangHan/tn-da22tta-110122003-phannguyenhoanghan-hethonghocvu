from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Nganh, Lop

@login_required
def api_filter_options(request):
    """
    API trả về danh sách Ngành theo Khoa và danh sách Lớp theo Ngành.
    """
    khoa = request.GET.get('khoa', '')
    nganh_id = request.GET.get('nganh', '')
    khoa_hoc = request.GET.get('khoa_hoc', '')
    
    data = {
        'nganhs': [],
        'lops': []
    }
    
    if khoa:
        nganhs = Nganh.objects.filter(khoa=khoa).exclude(ma_nganh__iexact='None').exclude(ten_nganh__iexact='None').values('id', 'ten_nganh', 'ma_nganh')
        data['nganhs'] = list(nganhs)
        
    if nganh_id:
        lops = Lop.objects.filter(nganh_id=nganh_id).exclude(ten_lop__iexact='None')
        if khoa_hoc:
            cohort_suffix = khoa_hoc[-2:]
            lops = lops.filter(ten_lop__istartswith=f'DA{cohort_suffix}')
        data['lops'] = list(lops.values('id', 'ten_lop'))
        
    return JsonResponse(data)
