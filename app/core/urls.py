from django.urls import path
from .views import RegistroAccionListView, RegistroAccionDetailView

app_name = 'core'

urlpatterns = [
    path("registros/", RegistroAccionListView.as_view(), name="registro_accion_list"),
    path("registros/<int:pk>/", RegistroAccionDetailView.as_view(), name="registro_accion_detail"),
]
