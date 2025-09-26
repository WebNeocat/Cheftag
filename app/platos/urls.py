from django.urls import path
from .views import *
from . import views

app_name = 'platos'

urlpatterns = [

    path('tiposplatos/', TipoPlatoList.as_view(), name='TipoPlatoList'),
    path('tiposplatos/crear/', TipoPlatoCreate.as_view(), name='TipoPlatoCreate'),
    path('tiposplatos/<int:pk>/', TipoPlatoUpdate.as_view(), name='TipoPlatoUpdate'),
    path('tiposplatos/<int:pk>/eliminar/', TipoPlatoDelete.as_view(), name='TipoPlatoDelete'),
    
    path('textomodo/', TextoModoList.as_view(), name='TextoModoList'),
    path('textomodo/crear/', TextoModoCreate.as_view(), name='TextoModoCreate'),
    path('textomodo/<int:pk>/', TextoModoUpdate.as_view(), name='TextoModoUpdate'),
    path('textomodo/<int:pk>/eliminar/', TextoModoDelete.as_view(), name='TextoModoDelete'),

    path('platos/', PlatoList.as_view(), name='PlatoList'),
    path('platos/crear/', PlatoCreate.as_view(), name='PlatoCreate'),
    path('platos/<int:pk>/', PlatoDetail.as_view(), name='PlatoDetail'),
    path('platos/<int:pk>/editar/', PlatoUpdate.as_view(), name='PlatoUpdate'),
    path('platos/<int:pk>/eliminar/', PlatoDelete.as_view(), name='PlatoDelete'),
    
    path('salsas/', SalsaList.as_view(), name='SalsaList'),
    path('salsas/crear/', SalsaCreate.as_view(), name='SalsaCreate'),
    path('salsas/<int:pk>/', SalsaDetail.as_view(), name='SalsaDetail'),
    path('salsas/<int:pk>/editar/', SalsaUpdate.as_view(), name='SalsaUpdate'),
    path('salsas/<int:pk>/eliminar/', SalsaDelete.as_view(), name='SalsaDelete'),
    
    path('platos/<int:plato_id>/receta/crear/', RecetaCreate.as_view(), name='crear_receta'),
    path('recetas/<int:pk>/editar/', RecetaUpdate.as_view(), name='editar_receta'),
    path('recetas/<int:pk>/', RecetaDetailView.as_view(), name='RecetaDetail'),
    
    path("etiquetas/generar/", views.generar_etiqueta, name="generar_etiqueta"),
    path("etiquetas/<int:etiqueta_id>/preview/", views.preview_etiqueta, name="preview_etiqueta"),
    path("etiquetas/imprimir/", views.imprimir_etiquetas, name="imprimir_etiquetas"),
    
    path('lotes/historicos/', LotesResumenListView.as_view(), name='LotesResumenListView'),
    path('lote/<str:lote>/', LoteDetalleListView.as_view(), name='lote_detalle'),
    path('reimprimir/<int:pk>/', views.reimprimir_etiqueta, name='reimprimir_etiqueta'),
    path('reimprimir-etiquetas/', views.reimprimir_etiquetas, name='reimprimir_etiquetas'),
]   
 