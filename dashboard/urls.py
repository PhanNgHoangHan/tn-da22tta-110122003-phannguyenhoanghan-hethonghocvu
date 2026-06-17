from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('sinh-vien/', views.dashboard_sinhvien, name='dashboard_sv'),
    path('co-van/', views.dashboard_covan, name='dashboard_covan'),
    path('giao-vu/', views.dashboard_giaovu, name='dashboard_giaovu'),
    path('bao-cao/', views.bao_cao, name='bao_cao'),
    path('bao-cao/export/', views.export_bao_cao_excel, name='export_bao_cao'),
    path('bao-cao/gui-covan/', views.gui_bao_cao_covan, name='gui_bao_cao_covan'),
]
