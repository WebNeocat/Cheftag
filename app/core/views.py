from django.shortcuts import render
from django.views.generic import ListView
from app.core.models import RegistroAccion
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from .mixins import PaginationMixin
from app.dashuser.views import datos_centro



class RegistroAccionListView(PaginationMixin, LoginRequiredMixin, ListView):
    model = RegistroAccion
    template_name = "core/registro_accion_list.html"
    context_object_name = "registros"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "userprofile") and user.userprofile.centro:
            return RegistroAccion.objects.filter(
                centro=user.userprofile.centro
            ).order_by("-fecha")
        return RegistroAccion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # añadimos el contexto con los datos del centro
        context.update(datos_centro(self.request))
        return context


class RegistroAccionDetailView(LoginRequiredMixin, DetailView):
    model = RegistroAccion
    template_name = "core/registro_accion_detail.html"
    context_object_name = "registro"

    def get_queryset(self):
        """
        Filtra para que solo muestre registros del centro del usuario logueado.
        """
        user = self.request.user
        if hasattr(user, "userprofile") and user.userprofile.centro:
            return RegistroAccion.objects.filter(centro=user.userprofile.centro)
        return RegistroAccion.objects.none()