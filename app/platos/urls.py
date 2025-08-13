from django.urls import path
from .views import *

app_name = 'platos'

urlpatterns = [

   path('tiposplatos/', TipoPlatoList.as_view(), name='TipoPlatoList'),
    path('tiposplatos/crear/', TipoPlatoCreate.as_view(), name='TipoPlatoCreate'),
    path('tiposplatos/<int:pk>/', TipoPlatoUpdate.as_view(), name='TipoPlatoUpdate'),
    path('tiposplatos/<int:pk>/eliminar/', TipoPlatoDelete.as_view(), name='TipoPlatoDelete'),
]    