from django.urls import path
from . import views
from .views import *

app_name = 'super'

urlpatterns = [
    path('home/', views.home, name='home'),
    
    path("crear_usuario/", crear_usuario, name="crear_usuario"),
    path("listado_usuarios/", UsuariosList.as_view(), name="UsuariosList"),
    
    path("listado_centros/", CentrosList.as_view(), name="CentrosList"),
    path("crear_centro/", CentroCreate.as_view(), name="CentroCreate"),
]