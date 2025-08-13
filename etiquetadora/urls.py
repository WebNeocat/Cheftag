from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.login.urls', namespace='login')),
    path('super/', include('app.super.urls', namespace='super')), 
    path('dashuser/', include('app.dashuser.urls', namespace='dashuser')),
    path('platos/', include('app.platos.urls', namespace='platos')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
