from django.urls import path
from . import views

app_name = 'academic_warnings'

urlpatterns = [
    path('', views.canhbao_list, name='canhbao_list'),
    path('<int:pk>/', views.canhbao_detail, name='canhbao_detail'),
    path('<int:pk>/update/', views.canhbao_update_status, name='canhbao_update'),
    path('kiem-tra/', views.kiem_tra_canh_bao_view, name='kiem_tra'),
    path('export/', views.export_canhbao, name='export'),
]
