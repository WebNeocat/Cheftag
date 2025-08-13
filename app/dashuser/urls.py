from django.urls import path
from . import views
from .views import *

app_name = 'dashuser'

urlpatterns = [
    path('home/', views.home, name='home'),
    
    path('lista_localizaciones/', LocalizacionList.as_view(), name='LocalizacionList'),
    path('crear_localizacion/', LocalizacionCreate.as_view(), name='LocalizacionCreate'),
    path('actualizar_localizacion/<int:pk>/', LocalizacionUpdate.as_view(), name="LocalizacionUpdate"),
    path('eliminar_localizacion/<int:pk>/', LocalizacionDelete.as_view(), name="LocalizacionDelete"),
    
    path('alergenos_lista/', AlergenosList.as_view(), name='AlergenosList'), 
    path('crear_alergenos/', AlergenosCreate.as_view(), name='AlergenosCreate'),
    path('actualizar_alergeno/<int:pk>/', AlergenosUpdate.as_view(), name="AlergenosUpdate"),
    path('eliminar_alergeno/<int:pk>/', AlergenosDelete.as_view(), name="AlergenosDelete"),
    
    path('lista_tipos_de_alimento/', TipoAlimentoList.as_view(), name='TipoAlimentoList'), 
    path('crear_tipos_alimentos/', TipoAlimentoCreate.as_view(), name='TipoAlimentoCreate'),
    path('actualizar_tipo_alimento/<int:pk>/', TipoAlimentoUpdate.as_view(), name="TipoAlimentoUpdate"),
    path('eliminar_tipo_alimento/<int:pk>/', TipoAlimentoDelete.as_view(), name="TipoAlimentoDelete"),
    
    path('lista_conservaciones/', ConservacionList.as_view(), name='ConservacionList'),
    path('crear_conservacion/', ConservacionCreate.as_view(), name='ConservacionCreate'),
    path('actualizar_conservacion/<int:pk>/', ConservacionUpdate.as_view(), name="ConservacionUpdate"),
    path('eliminar_conservacion/<int:pk>/', ConservacionDelete.as_view(), name="ConservacionDelete"),
    
    path('lista_alimento/', AlimentoList.as_view(), name='AlimentoList'),
    path('crear_alimento/', AlimentoCreate.as_view(), name='AlimentoCreate'),
    path('alimentos/<int:pk>/', AlimentoDetailView.as_view(), name='AlimentoDetail'),
    path('actualizar_alimentos/<int:pk>/', AlimentoUpdate.as_view(), name='AlimentoUpdate'),
    path('eliminar_alimentos/<int:pk>/', AlimentoDelete.as_view(), name='AlimentoDelete'),
    
    
]