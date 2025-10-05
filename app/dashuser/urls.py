from django.urls import path
from . import views
from .views import *

app_name = 'dashuser'

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="Dashboard"),
    
    path('lista_localizaciones/', LocalizacionList.as_view(), name='LocalizacionList'),
    path('crear_localizacion/', LocalizacionCreate.as_view(), name='LocalizacionCreate'),
    path('actualizar_localizacion/<int:pk>/', LocalizacionUpdate.as_view(), name="LocalizacionUpdate"),
    path('eliminar_localizacion/<int:pk>/', LocalizacionDelete.as_view(), name="LocalizacionDelete"),
    
    path('alergenos_lista/', AlergenosList.as_view(), name='AlergenosList'), 
    path('crear_alergenos/', AlergenosCreate.as_view(), name='AlergenosCreate'),
    path('actualizar_alergeno/<int:pk>/', AlergenosUpdate.as_view(), name="AlergenosUpdate"),
    path('eliminar_alergeno/<int:pk>/', AlergenosDelete.as_view(), name="AlergenosDelete"),
    
    path('trazas_lista/', TrazasList.as_view(), name='TrazasList'), 
    path('crear_trazas/', TrazasCreate.as_view(), name='TrazasCreate'),
    path('actualizar_trazas/<int:pk>/', TrazasUpdate.as_view(), name="TrazasUpdate"),
    path('eliminar_trazas/<int:pk>/', TrazasDelete.as_view(), name="TrazasDelete"),
    
    path('lista_unidades_de_medida/', UnidadDeMedidaList.as_view(), name='UnidadDeMedidaList'), 
    path('crear_unidades_de_medida/', UnidadDeMedidaCreate.as_view(), name='UnidadDeMedidaCreate'),
    path('actualizar_unidad_de_medida/<int:pk>/', UnidadDeMedidaUpdate.as_view(), name="UnidadDeMedidaUpdate"),
    path('eliminar_unidad_de_medida/<int:pk>/', UnidadDeMedidaDelete.as_view(), name="UnidadDeMedidaDelete"),
    
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
    
    path('crear_etiqueta/', views.crear_etiqueta, name='crear_etiqueta'),
    path('etiqueta/<int:pk>/pdf/', views.etiqueta_pdf, name='etiqueta_pdf'),
    
]