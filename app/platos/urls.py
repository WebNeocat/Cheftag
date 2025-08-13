from django.urls import path
from .views import *

app_name = 'platos'

urlpatterns = [

    path('tiposplatos/', TipoPlatoList.as_view(), name='TipoPlatoList'),
    path('tiposplatos/crear/', TipoPlatoCreate.as_view(), name='TipoPlatoCreate'),
    path('tiposplatos/<int:pk>/', TipoPlatoUpdate.as_view(), name='TipoPlatoUpdate'),
    path('tiposplatos/<int:pk>/eliminar/', TipoPlatoDelete.as_view(), name='TipoPlatoDelete'),

    path('platos/', PlatoList.as_view(), name='PlatoList'),
    path('platos/crear/', PlatoCreate.as_view(), name='PlatoCreate'),
    path('platos/<int:pk>/', PlatoDetail.as_view(), name='PlatoDetail'),
    path('platos/<int:pk>/editar/', PlatoUpdate.as_view(), name='PlatoUpdate'),
    path('platos/<int:pk>/eliminar/', PlatoDelete.as_view(), name='PlatoDelete'),
]    