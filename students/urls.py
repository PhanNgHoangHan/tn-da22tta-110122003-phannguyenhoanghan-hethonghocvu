from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Sinh viên
    path('', views.sinhvien_list, name='sinhvien_list'),
    path('<int:pk>/', views.sinhvien_detail, name='sinhvien_detail'),
    path('create/', views.sinhvien_create, name='sinhvien_create'),
    path('<int:pk>/edit/', views.sinhvien_edit, name='sinhvien_edit'),
    path('<int:pk>/delete/', views.sinhvien_delete, name='sinhvien_delete'),
    path('import/', views.import_sinhvien, name='import_sinhvien'),
    path('export/', views.export_sinhvien, name='export_sinhvien'),
    # Môn học
    path('monhoc/', views.monhoc_list, name='monhoc_list'),
    path('monhoc/create/', views.monhoc_create, name='monhoc_create'),
    path('monhoc/<int:pk>/edit/', views.monhoc_edit, name='monhoc_edit'),
    path('monhoc/<int:pk>/delete/', views.monhoc_delete, name='monhoc_delete'),
    # Học kỳ
    path('hocky/', views.hocky_list, name='hocky_list'),
    path('hocky/create/', views.hocky_create, name='hocky_create'),
    path('hocky/<int:pk>/edit/', views.hocky_edit, name='hocky_edit'),
]
