from django.urls import path
from .views import *
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('crear_pedido/', CreatePedidoView.as_view(), name='crear_pedido'),
    path('listado_pedidos/', ListPedidoView.as_view(), name='listado_pedidos'),
    path('pedido/<int:pk>/', DetailPedidoView.as_view(), name='detalle_pedido'),
    path('pedido/eliminar/<int:pk>/', DeletePedidoView.as_view(), name='eliminar_pedido'),
    path('pedido/editar/<int:pk>/', UpdatePedidoView.as_view(), name='editar_pedido'),
    
    path('pedido/<int:pk>/exportar/pdf/', exportar_pedido_pdf, name='exportar_pedido_pdf'),
    path('pedido/<int:pk>/exportar/excel/', exportar_pedido_excel, name='exportar_pedido_excel'),
    
    path('pedidos/proveedor/<int:pk>/', ListPedidoPorProveedorView.as_view(), name='pedidos_por_proveedor'), 
    
]