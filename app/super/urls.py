from django.urls import path
from . import views
from .views import *

app_name = 'super'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    
    path("crear_usuario/", CrearUsuarioView.as_view(), name="crear_usuario"),
    path("listado_usuarios/", UsuariosList.as_view(), name="UsuariosList"),
    path('usuarios/editar/<int:pk>/', ActualizarUsuarioView.as_view(), name='UsuarioUpdate'),
    path('usuarios/eliminar/<int:pk>/', EliminarUsuarioView.as_view(), name='UsuarioDelete'),


    
    path("listado_centros/", CentrosList.as_view(), name="CentrosList"),
    path("crear_centro/", CentroCreate.as_view(), name="CentroCreate"),
    path('centros/editar/<int:pk>/', CentroUpdate.as_view(), name='CentroUpdate'),
    path('centros/<int:pk>/', CentroDetail.as_view(), name='CentroDetail'),
    path('centros/eliminar/<int:pk>/', CentroDelete.as_view(), name='CentroDelete'),
    path('centros/<int:pk>/usuarios/', UsuariosCentroListView.as_view(), name='UsuariosCentro'),

]