from django.urls import path
from .views import *
from . import views

app_name = 'recepcion'

urlpatterns = [
    path('proveedores/nuevo/', ProveedorCreate.as_view(), name='ProveedorCreate'),
    path('proveedores/listado/', ProveedorList.as_view(), name='ProveedorList'),
    path('actualizar_proveedor/<int:pk>/', ProveedorUpdate.as_view(), name="ProveedorUpdate"),
    path('eliminar_proveedor/<int:pk>/', ProveedorDelete.as_view(), name="ProveedorDelete"),
    path('datos/proveedor/<int:pk>/', ProveedorDetailView.as_view(), name="ProveedorDetail"),
    
    path('recepcion_manual/nuevo/', RecepcionManualCreate.as_view(), name='RecepcionManualCreate'),
    path('recepcion_manual/listado/', RecepcionManualList.as_view(), name='RecepcionManualList'),
    path('editar/recepcion_manual/<int:pk>/', RecepcionManualUpdate.as_view(), name="RecepcionManualUpdate"),
    path('detalle/recepcion_manual/<int:pk>/', RecepcionManualDetail.as_view(), name="RecepcionManualDetail"),
    path('eliminar_recepcion_manual/<int:pk>/', RecepcionManualDeleteFormView.as_view(), name="RecepcionManualDeleteFormView"),
    
    path('recepcion_gs1', views.recepcion_gs1, name="recepcion_gs1"),
    path('parse_gs1_128', views.parse_gs1_128, name="parse_gs1_128"),
    
    path('tipo_de_merma/nuevo/', TipoDeMermaCreate.as_view(), name='TipoDeMermaCreate'),
    path('tipo_de_merma/listado/', TipoDeMermaList.as_view(), name='TipoDeMermaList'),
    path('actualizar_tipo_de_merma/<int:pk>/', TipoDeMermaUpdate.as_view(), name="TipoDeMermaUpdate"),
    path('eliminar_tipo_de_merma/<int:pk>/', TipoDeMermaDelete.as_view(), name="TipoDeMermaDelete"),
    
    path('mermas/nuevo/', MermasCreate.as_view(), name='MermasCreate'),
    path('mermas/listado/', MermasList.as_view(), name='MermasList'),
    path('actualizar_mermas/<int:pk>/', MermasUpdate.as_view(), name="MermasUpdate"),
    path('eliminar_mermas/<int:pk>/', MermasDelete.as_view(), name="MermasDelete"),
    path('datos/mermas/<int:pk>/', MermasDetailView.as_view(), name="MermasDetailView"),
    
    path('lista_ajustes/', AjusteInventarioList.as_view(), name='AjusteInventarioList'),
    path('crear_juste/', AjusteInventarioCreate.as_view(), name='AjusteInventarioCreate'),
    path('actualizar_ajuste/<int:pk>/', AjusteInventarioUpdate.as_view(), name='AjusteInventarioUpdate'),
    path('eliminar_ajuste/<int:pk>/', AjusteInventarioDelete.as_view(), name='AjusteInventarioDelete'),
    
    path('auditoria/listado/', AuditoriaList.as_view(), name='AuditoriaList'),

    
    
]