from django.urls import path
from .views import RegistroAccionListView, RegistroAccionDetailView, UsersListView, UsersUpdateView, UserCreateView, UserDeleteView, UserDetailView

app_name = 'core'

urlpatterns = [
    path("registros/", RegistroAccionListView.as_view(), name="registro_accion_list"),
    path("registros/<int:pk>/", RegistroAccionDetailView.as_view(), name="registro_accion_detail"),
    
    path("lista_usuarios/", UsersListView.as_view(), name="UsersListView"),
    path("crear_usuario/", UserCreateView.as_view(), name="UserCreateView"),
    path("editar/usuarios/<int:pk>/", UsersUpdateView.as_view(), name="UsersUpdateView"),
    path("eliminar/usuario/<int:pk>/", UserDeleteView.as_view(), name="UserDeleteView"),
    path("detalles/usuario/<int:pk>/", UserDetailView.as_view(), name="UserDetailView"),
]
