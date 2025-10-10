from django.urls import path
from . import views
from .views import *

app_name = 'super'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    
    path("crear_usuario/", UserCreate.as_view(), name="UserCreate"),
    path("listado_usuarios/", UserList.as_view(), name="UserList"),
    path('usuarios/editar/<int:pk>/', UserUpdate.as_view(), name='UserUpdate'),
    path('usuarios/eliminar/<int:pk>/', UserDelete.as_view(), name='UserDelete'),
       
    path("listado_centros/", CentrosList.as_view(), name="CentrosList"),
    path("crear_centro/", CentroCreate.as_view(), name="CentroCreate"),
    path('centros/editar/<int:pk>/', CentroUpdate.as_view(), name='CentroUpdate'),
    path('centros/<int:pk>/', CentroDetail.as_view(), name='CentroDetail'),
    path('centros/eliminar/<int:pk>/', CentroDelete.as_view(), name='CentroDelete'),
    path('centros/<int:pk>/usuarios/', UsuariosCentroListView.as_view(), name='UsuariosCentro'),
    
    path('usuarios/<int:pk>/permisos/', views.UserPermisosView.as_view(), name='user_permisos'),
    
    path('importar/', ImportadorBaseCentro, name='ImportadorBaseCentro'),
    path('importar/alimentos/', ImportadorAlimentos, name='ImportadorAlimentos'),
    path('importar_datos/', views.importar_datos, name='importar_datos'),
    path('importar_datos_alimentos/', views.importar_datos_alimentos, name='importar_datos_alimentos'),

]