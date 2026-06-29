from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('', views.ketqua_list, name='ketqua_list'),
    path('create/', views.ketqua_create, name='ketqua_create'),
    path('<int:pk>/edit/', views.ketqua_edit, name='ketqua_edit'),
    path('<int:pk>/delete/', views.ketqua_delete, name='ketqua_delete'),
    path('import/', views.import_diem, name='import_diem'),
    path('export/', views.export_diem, name='export_diem'),
    path('api/gpa/<int:sv_id>/', views.api_gpa_chart, name='api_gpa_chart'),
]
