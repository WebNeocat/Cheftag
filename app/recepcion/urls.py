from django.urls import path
from .views import *
from . import views

app_name = 'recepcion'

urlpatterns = [
    path('proveedores/nuevo/', ProveedorCreate.as_view(), name='ProveedorCreate'),
    path('proveedores/listado/', ProveedorList.as_view(), name='ProveedorList'),
    path('actualizar_proveedor/<int:pk>/', ProveedorUpdate.as_view(), name="ProveedorUpdate"),
    path('eliminar_proveedor/<int:pk>/', ProveedorDelete.as_view(), name="ProveedorDelete"),
    path('detalle/proveedor/<int:pk>/', ProveedorDetailView.as_view(), name="ProveedorDetail"),
    
    path('recepcion_manual/nuevo/', RecepcionManualCreate.as_view(), name='RecepcionManualCreate'),
    path('recepcion_manual/listado/', RecepcionManualList.as_view(), name='RecepcionManualList'),
    path('detalle/recepcion_manual/<int:pk>/', RecepcionManualDetail.as_view(), name="RecepcionManualDetail"),
    path('eliminar_recepcion_manual/<int:pk>/', RecepcionManualDelete.as_view(), name="RecepcionManualDelete"),
    
]