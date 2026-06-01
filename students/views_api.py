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
    
    data = {
        'nganhs': [],
        'lops': []
    }
    
    if khoa:
        nganhs = Nganh.objects.filter(khoa=khoa).values('id', 'ten_nganh', 'ma_nganh')
        data['nganhs'] = list(nganhs)
        
    if nganh_id:
        lops = Lop.objects.filter(nganh_id=nganh_id).values('id', 'ten_lop')
        data['lops'] = list(lops)
        
    return JsonResponse(data)
