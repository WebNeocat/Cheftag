from django.http import HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from app.super.permissions import tiene_permiso

class PermisoMixin:
    """
    Mixin para controlar permisos en CBVs.
    Requiere definir:
      - permiso_modulo: string con el nombre del módulo (ej: "Alérgenos")
    """
    permiso_modulo = None
    permiso_accion = None

    # Mapeo de clases CBV a acciones
    ACTION_MAP = {
        ListView: "read",
        DetailView: "read",
        CreateView: "create",
        UpdateView: "update",
        DeleteView: "delete",
        TemplateView: "read",
    }

    def dispatch(self, request, *args, **kwargs):
        if not self.permiso_modulo:
            return HttpResponseForbidden("Vista mal configurada: falta permiso_modulo")

        # Detecta acción automáticamente
        if not self.permiso_accion:
            for cls, accion in self.ACTION_MAP.items():
                if issubclass(type(self), cls):
                    self.permiso_accion = accion
                    break

        # Chequea si el usuario tiene el permiso
        user_profile = getattr(request.user, "userprofile", None)
        if user_profile is None:
            return HttpResponseForbidden("Usuario sin perfil")
        if not tiene_permiso(user_profile, self.permiso_modulo, self.permiso_accion):
            return HttpResponseForbidden("No tienes permiso para esta acción")

        return super().dispatch(request, *args, **kwargs)



class PaginationMixin:

    pagination_window_size = 3  # 3 páginas a cada lado (7 en total)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context.get('page_obj')
        
        if page_obj:
            current_page = page_obj.number
            total_pages = page_obj.paginator.num_pages
            window = self.pagination_window_size
            
            if total_pages <= (window * 2) + 1:
                context['custom_page_range'] = range(1, total_pages + 1)
            elif current_page <= window:
                context['custom_page_range'] = range(1, (window * 2) + 2)
            elif current_page >= total_pages - window:
                context['custom_page_range'] = range(total_pages - (window * 2), total_pages + 1)
            else:
                context['custom_page_range'] = range(current_page - window, current_page + window + 1)
        
        return context