from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard:index'), name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('students/', include('students.urls', namespace='students')),
    path('results/', include('results.urls', namespace='results')),
    path('canh-bao/', include('academic_warnings.urls', namespace='academic_warnings')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
