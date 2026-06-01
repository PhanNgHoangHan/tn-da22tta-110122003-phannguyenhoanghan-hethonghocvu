from django.urls import path
from . import views

app_name = 'academic_warnings'

urlpatterns = [
    path('', views.canhbao_list, name='canhbao_list'),
    path('<int:pk>/', views.canhbao_detail, name='canhbao_detail'),
    path('<int:pk>/update/', views.canhbao_update_status, name='canhbao_update'),
    path('<int:pk>/hide/', views.canhbao_hide, name='canhbao_hide'),
    path('<int:pk>/send-email/', views.canhbao_gui_thong_bao, name='canhbao_send_email'),
    path('send-bulk-email/', views.canhbao_gui_thong_bao_hang_loat, name='canhbao_send_bulk_email'),
    path('export/', views.export_canhbao, name='export'),
]
