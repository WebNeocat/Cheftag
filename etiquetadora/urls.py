from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.login.urls', namespace='login')),
    path('super/', include('app.super.urls', namespace='super')), 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
