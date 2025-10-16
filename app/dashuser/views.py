from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views import View
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q, F
from django.utils.timezone import localtime, now, timedelta
from django.core.exceptions import ObjectDoesNotExist
from app.core.mixins import PaginationMixin, PermisoMixin
from app.super.views import MODULOS, ACCIONES
from app.super.permissions import tiene_permiso
from django.db.models import Count
from app.platos.models import Plato, Receta, EtiquetaPlato
from app.super.models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from app.pedidos.models import PedidoDetalle
from app.recepcion.models import Recepcion
from .models import Alergenos, TipoAlimento, Alimento, Localizacion, Conservacion, InformacionNutricional, UnidadDeMedida, Trazas, EtiquetaAlimento, Utensilio
from .forms import AlergenosForm, TipoAlimento, LocalizacionForm, TipoAlimentosForm, ConservacionForm, InformacionNutricionalForm, AlimentoForm, UnidadDeMedidaForm, TrazasForm, EtiquetaAlimentoForm, UtensilioForm
import qrcode
import io
import base64



def datos_centro(request):
    """
    Devuelve información del usuario, del centro, saludo y permisos por módulo.
    """
    context = {}

    if not request.user.is_authenticated:
        return context

    # Datos del usuario
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return context

    hora_actual = localtime().hour
    if 5 <= hora_actual < 12:
        saludo = "Buenos días"
    elif 12 <= hora_actual < 18:
        saludo = "Buenas tardes"
    else:
        saludo = "Buenas noches"

    # Imagenes
    imagen_user_url = user_profile.imagen.url if user_profile.imagen else None
    imagen_centro_url = user_profile.centro.imagen.url if user_profile.centro and user_profile.centro.imagen else None

    # Construimos los permisos
    permisos_dict = {}
    for modulo in MODULOS:
        permisos_dict[modulo] = {}
        for accion in ACCIONES:
            permisos_dict[modulo][accion] = tiene_permiso(user_profile, modulo, accion)

    context.update({
        'user_profile': user_profile,
        'nombre': user_profile.nombre,
        'apellidos': user_profile.apellidos,
        'cargo': user_profile.cargo,
        'imagen_user_url': imagen_user_url,
        'imagen_centro_url': imagen_centro_url,
        'saludo': saludo,
        'permisos': permisos_dict,  # <-- aquí todos los permisos por módulo y acción
    })

    return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashuser/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.userprofile
        centro = user_profile.centro
        context.update(datos_centro(self.request))

        # 📊 Platos más creados
        platos_mas_creados = (
            Plato.objects.filter(centro=centro)
            .values("nombre")
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
        )

        # 📊 Alimentos más usados en recetas
        alimentos_mas_usados = (
            Alimento.objects.filter(centro=centro)
            .annotate(num_usos=Count("alimentoplato"))
            .order_by("-num_usos")[:5]
        )

        # 📊 Raciones últimos 7 días (por etiquetas)
        ultimos_dias = now().date() - timedelta(days=7)
        raciones = (
            EtiquetaPlato.objects
            .filter(plato__centro=centro, fecha__date__gte=ultimos_dias)
            .values("fecha__date")
            .annotate(total=Count("id"))
            .order_by("fecha__date")
        )

        # 📊 Totales
        context["stats"] = {
            "total_platos": Plato.objects.filter(centro=centro).count(),
            "total_recetas": Receta.objects.filter(centro=centro).count(),
            "total_alimentos": Alimento.objects.filter(centro=centro).count(),
        }

        # Preparar datos para Chart.js
        context["platos_labels"] = [p["nombre"] for p in platos_mas_creados]
        context["platos_values"] = [p["total"] for p in platos_mas_creados]

        context["alimentos_labels"] = [a.nombre for a in alimentos_mas_usados]
        context["alimentos_values"] = [a.num_usos for a in alimentos_mas_usados]

        context["raciones_labels"] = [r["fecha__date"].strftime("%Y-%m-%d") for r in raciones]
        context["raciones_values"] = [r["total"] for r in raciones]

        return context
    
######################################################################################
###############################  ALERGENOS  ########################################
######################################################################################


class AlergenosList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Alergenos" 
    model = Alergenos
    template_name = 'dashuser/listar_alergenos.html'
    context_object_name = 'alergenos'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Alergenos.objects.filter(centro=centro).order_by('id')

                # Permitir búsqueda dentro de los alérgenos del centro
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query) |
                        Q(codigo__icontains=search_query)
                    )
                return queryset
            else:
                return Alergenos.objects.none()
        except ObjectDoesNotExist:
            return Alergenos.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay alérgenos asociados
        if not context['alergenos'].exists():
            context['mensaje'] = "No tiene alérgenos asociados."

        return context
    
    
class AlergenosCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Alergenos" 
    model = Alergenos
    form_class = AlergenosForm
    template_name = 'dashuser/crear_alergenos.html'
    success_url = reverse_lazy('dashuser:AlergenosList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Alérgeno creado correctamente.')
            return super().form_valid(form)  # solo guarda 1 vez
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
class AlergenosUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Alergenos" 
    model = Alergenos
    template_name = 'dashuser/detalle_alergenos.html'
    form_class = AlergenosForm
    success_url = reverse_lazy('dashuser:AlergenosList')
    context_object_name = 'alergeno'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Alergenos.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return Alergenos.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Alérgeno actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   
    

class AlergenosDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Alergenos" 
    model = Alergenos
    template_name = 'dashuser/alergenos_confirm_delete.html'
    success_url = reverse_lazy('dashuser:AlergenosList')
    context_object_name = 'alergeno'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Alergenos.objects.filter(centro=user_profile.centro)
        else:
            return Alergenos.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.save
        messages.success(self.request, 'Alérgeno eliminado correctamente.')
        return super().delete(request, *args, **kwargs) 
    

######################################################################################
############################# TRAZAS ALERGENOS  ######################################
######################################################################################


class TrazasList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Trazas" 
    model = Trazas
    template_name = 'dashuser/listar_trazas.html'
    context_object_name = 'trazas'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Trazas.objects.filter(centro=centro).order_by('id')

                # Permitir búsqueda dentro de los alérgenos del centro
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query) |
                        Q(codigo__icontains=search_query)
                    )
                return queryset
            else:
                return Trazas.objects.none()
        except ObjectDoesNotExist:
            return Trazas.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay trazas de alérgenos asociados
        if not context['trazas'].exists():
            context['mensaje'] = "No tiene trazas de alergenos asociados."

        return context
    
class TrazasCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Trazas"
    model = Trazas
    form_class = TrazasForm
    template_name = 'dashuser/crear_trazas.html'
    success_url = reverse_lazy('dashuser:TrazasList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Traza creada correctamente.')
            return super().form_valid(form)  # solo guarda 1 vez
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)


    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
    
class TrazasUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Trazas"
    model = Trazas
    template_name = 'dashuser/detalle_trazas.html'
    form_class = TrazasForm
    success_url = reverse_lazy('dashuser:TrazasList')
    context_object_name = 'traza'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Trazas.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return Trazas.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Trazas de alérgeno actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   
    

class TrazasDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Trazas"
    model = Trazas
    template_name = 'dashuser/trazas_confirm_delete.html'
    success_url = reverse_lazy('dashuser:TrazasList')
    context_object_name = 'traza'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Trazas.objects.filter(centro=user_profile.centro)
        else:
            return Trazas.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.last_modified_by = request.user
        obj.save
        messages.success(self.request, 'Traza de alérgeno eliminado correctamente.')
        return super().delete(request, *args, **kwargs) 
    

######################################################################################
###############################  UNIDADES DE MEDIDA  #################################
######################################################################################    


class UnidadDeMedidaList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "UnidadDeMedida"
    model = UnidadDeMedida
    template_name = 'dashuser/listar_unidaddemedida.html'
    context_object_name = 'unidaddemedidas'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = UnidadDeMedida.objects.filter(centro=centro).order_by('id')

                # Permitir búsqueda dentro de los alérgenos del centro
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query) |
                        Q(abreviatura__icontains=search_query)
                    )
                return queryset
            else:
                return UnidadDeMedida.objects.none()
        except ObjectDoesNotExist:
            return UnidadDeMedida.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay alérgenos asociados
        if not context['unidaddemedidas'].exists():
            context['mensaje'] = "No tiene tipos de alimento asociados."

        return context
    
    
class UnidadDeMedidaCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "UnidadDeMedida"
    model = UnidadDeMedida
    form_class = UnidadDeMedidaForm
    template_name = 'dashuser/crear_unidaddemedida.html'
    success_url = reverse_lazy('dashuser:UnidadDeMedidaList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Unidad de medida creada correctamente.')
            return super().form_valid(form) 
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   
     
    
class UnidadDeMedidaUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "UnidadDeMedida"
    model = UnidadDeMedida
    template_name = 'dashuser/detalle_unidaddemedida.html'
    form_class = UnidadDeMedidaForm
    success_url = reverse_lazy('dashuser:UnidadDeMedidaList')
    context_object_name = 'unidaddemedida'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return UnidadDeMedida.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return UnidadDeMedida.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Unidad de medida actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    

class UnidadDeMedidaDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "UnidadDeMedida"
    model = UnidadDeMedida
    template_name = 'dashuser/unidaddemedida_confirm_delete.html'
    success_url = reverse_lazy('dashuser:UnidadDeMedidaList')
    context_object_name = 'unidaddemedida'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return UnidadDeMedida.objects.filter(centro=user_profile.centro)
        else:
            return UnidadDeMedida.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.last_modified_by = request.user
        obj.save
        messages.success(self.request, 'Unidad de medida eliminada correctamente.')
        return super().delete(request, *args, **kwargs)
    
         
######################################################################################
###############################  TIPO ALIMENTOS  ####################################
######################################################################################


class TipoAlimentoList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "TipoAlimento"
    model = TipoAlimento
    template_name = 'dashuser/listar_tipoalimento.html'
    context_object_name = 'tipoalimentos'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = TipoAlimento.objects.filter(centro=centro).order_by('id')

                # Permitir búsqueda dentro de los alérgenos del centro
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query)
                    )
                return queryset
            else:
                return TipoAlimento.objects.none()
        except ObjectDoesNotExist:
            return TipoAlimento.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay alérgenos asociados
        if not context['tipoalimentos'].exists():
            context['mensaje'] = "No tiene tipos de alimento asociados."

        return context
    
    
class TipoAlimentoCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "TipoAlimento"
    model = TipoAlimento
    form_class = TipoAlimentosForm
    template_name = 'dashuser/crear_tipoalimento.html'
    success_url = reverse_lazy('dashuser:TipoAlimentoList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Tipo de alimento creado correctamente.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)


    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
    
class TipoAlimentoUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "TipoAlimento"
    model = TipoAlimento
    template_name = 'dashuser/detalle_tipoalimento.html'
    form_class = TipoAlimentosForm
    success_url = reverse_lazy('dashuser:TipoAlimentoList')
    context_object_name = 'tipoalimento'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return TipoAlimento.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return TipoAlimento.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Tipo de alimento actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)  
    
class TipoAlimentoDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "TipoAlimento"
    model = TipoAlimento
    template_name = 'dashuser/tipoalimento_confirm_delete.html'
    success_url = reverse_lazy('dashuser:TipoAlimentoList')
    context_object_name = 'tipoalimento'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return TipoAlimento.objects.filter(centro=user_profile.centro)
        else:
            return TipoAlimento.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.save
        messages.success(self.request, 'Tipo e Alimento eliminado correctamente.')
        return super().delete(request, *args, **kwargs)
    
    
######################################################################################
##############################  LOCALIZACION  ########################################
######################################################################################    


class LocalizacionList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Localizacion"
    model = Localizacion
    template_name = 'dashuser/listar_localizacion.html'
    context_object_name = 'localizaciones'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Localizacion.objects.filter(centro=centro).order_by('id')


                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(localizacion__icontains=search_query) 
                    )
                return queryset
            else:
                return Localizacion.objects.none()
        except ObjectDoesNotExist:
            return Localizacion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay localizaciones asociadas
        if not context['localizaciones'].exists():
            context['mensaje'] = "No tiene localizaciones asociadas."

        return context
    
    
class LocalizacionCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Localizacion"
    model = Localizacion
    form_class = LocalizacionForm
    template_name = 'dashuser/crear_localizacion.html'
    success_url = reverse_lazy('dashuser:LocalizacionList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Localización creada correctamente.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)


    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   


class LocalizacionUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Localizacion"
    model = Localizacion
    template_name = 'dashuser/detalle_localizacion.html'
    form_class = LocalizacionForm
    success_url = reverse_lazy('dashuser:LocalizacionList')
    context_object_name = 'localizacion'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Localizacion.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return Localizacion.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Localización actualizada correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
 
class LocalizacionDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Localizacion"
    model = Localizacion
    template_name = 'dashuser/localizacion_confirm_delete.html'
    success_url = reverse_lazy('dashuser:LocalizacionList')
    context_object_name = 'localizacion'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Localizacion.objects.filter(centro=user_profile.centro)
        else:
            return Localizacion.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.last_modified_by = request.user
        obj.save(update_fields=['last_modified_by'])
        messages.success(self.request, 'Ubicación eliminada correctamente.')
        return super().delete(request, *args, **kwargs)       
    
    
######################################################################################
##############################  CONSERVACIÓN  ########################################
######################################################################################    


class ConservacionList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Conservacion"
    model = Conservacion
    template_name = 'dashuser/listar_conservacion.html'
    context_object_name = 'conservaciones'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Conservacion.objects.filter(centro=centro).order_by('id')


                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(conservacion__icontains=search_query) 
                    )
                return queryset
            else:
                return Conservacion.objects.none()
        except ObjectDoesNotExist:
            return Conservacion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay conservaciones asociadas
        if not context['conservaciones'].exists():
            context['mensaje'] = "No tiene conservaciones asociadas."

        return context
    
    
class ConservacionCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Conservacion"
    model = Conservacion
    form_class = ConservacionForm
    template_name = 'dashuser/crear_conservacion.html'
    success_url = reverse_lazy('dashuser:ConservacionList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Conservación creada correctamente.')
            return super().form_valid(form) 
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)


    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   


class ConservacionUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Conservacion"
    model = Conservacion
    template_name = 'dashuser/detalle_conservacion.html'
    form_class = ConservacionForm
    success_url = reverse_lazy('dashuser:ConservacionList')
    context_object_name = 'conservacion'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Conservacion.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return Conservacion.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Conservacion actualizada correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
 
class ConservacionDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Conservacion"
    model = Conservacion
    template_name = 'dashuser/conservacion_confirm_delete.html'
    success_url = reverse_lazy('dashuser:ConservacionList')
    context_object_name = 'conservacion'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Conservacion.objects.filter(centro=user_profile.centro)
        else:
            return Conservacion.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.save
        messages.success(self.request, 'Conservación eliminada correctamente.')
        return super().delete(request, *args, **kwargs)      
    
    
######################################################################################
##############################     ALIMENTO   ########################################
######################################################################################      

class AlimentoList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Alimento"
    model = Alimento
    template_name = 'dashuser/listar_alimentos.html'
    context_object_name = 'alimentos'
    paginate_by = 20  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Alimento.objects.filter(centro=centro).order_by('nombre')


                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query) 
                    )
                return queryset
            else:
                return Alimento.objects.none()
        except ObjectDoesNotExist:
            return Alimento.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay alimentos asociados
        if not context['alimentos'].exists():
            context['mensaje'] = "No tiene alimentos asociados."

        return context
    
    
class AlimentoCreate(LoginRequiredMixin, View):
    def get(self, request):
        user_profile = request.user.userprofile
        alimento_form = AlimentoForm(centro=user_profile.centro)  # ✅ pasamos el centro
        nutricion_form = InformacionNutricionalForm()
        
        context = {
            'alimento_form': alimento_form,
            'nutricion_form': nutricion_form
        }
        context.update(datos_centro(request))  # añadimos el contexto extra
        
        return render(request, 'dashuser/crear_alimento.html', context)
    
    def post(self, request):
        user_profile = request.user.userprofile
        alimento_form = AlimentoForm(request.POST, request.FILES, centro=user_profile.centro)  # ✅ filtrado
        nutricion_form = InformacionNutricionalForm(request.POST)

        if alimento_form.is_valid() and nutricion_form.is_valid():
            alimento = alimento_form.save(commit=False)
            alimento.centro = user_profile.centro  # ✅ asignamos el centro del usuario
            alimento.save()

            alimento_form.save_m2m()  # guarda alérgenos y trazas
            
            nutricion = nutricion_form.save(commit=False)
            nutricion.alimento = alimento
            nutricion.save()

            return redirect('dashuser:AlimentoList')

        context = {
            'alimento_form': alimento_form,
            'nutricion_form': nutricion_form
        }
        context.update(datos_centro(request))
        return render(request, 'dashuser/crear_alimento.html', context)


class AlimentoDetailView(PaginationMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "Alimento"
    model = Alimento
    template_name = 'dashuser/detalle_alimento.html'
    context_object_name = 'alimento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))  
        return context
    
    
class AlimentoUpdate(PaginationMixin, LoginRequiredMixin, View):
    permiso_modulo = "Alimento"

    def get(self, request, pk):
        user_profile = request.user.userprofile
        alimento = get_object_or_404(
            Alimento, pk=pk, centro=user_profile.centro
        )

        try:
            nutricion = alimento.nutricion
        except InformacionNutricional.DoesNotExist:
            nutricion = None

        # ✅ Pasamos el centro al formulario
        alimento_form = AlimentoForm(instance=alimento, centro=user_profile.centro)
        nutricion_form = InformacionNutricionalForm(instance=nutricion)

        context = {
            'alimento_form': alimento_form,
            'nutricion_form': nutricion_form,
            'alimento': alimento
        }
        context.update(datos_centro(request))
        return render(request, 'dashuser/editar_alimento.html', context)

    def post(self, request, pk):
        user_profile = request.user.userprofile
        alimento = get_object_or_404(
            Alimento, pk=pk, centro=user_profile.centro
        )

        try:
            nutricion = alimento.nutricion
        except InformacionNutricional.DoesNotExist:
            nutricion = None

        # ✅ Pasamos centro también en el POST
        alimento_form = AlimentoForm(request.POST, request.FILES, instance=alimento, centro=user_profile.centro)
        nutricion_form = InformacionNutricionalForm(request.POST, instance=nutricion)

        if alimento_form.is_valid() and nutricion_form.is_valid():
            alimento = alimento_form.save(commit=False)
            alimento.centro = user_profile.centro  # reforzamos centro
            alimento.save()

            alimento_form.save_m2m()  # ✅ guarda alérgenos y trazas

            nutricion = nutricion_form.save(commit=False)
            nutricion.alimento = alimento
            nutricion.save()

            return redirect('dashuser:AlimentoList')

        context = {
            'alimento_form': alimento_form,
            'nutricion_form': nutricion_form,
            'alimento': alimento
        }
        context.update(datos_centro(request))
        return render(request, 'dashuser/editar_alimento.html', context)



class AlimentoDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Alimento"
    model = Alimento
    template_name = 'dashuser/eliminar_alimento.html'
    context_object_name = 'alimento'
    success_url = reverse_lazy('dashuser:AlimentoList')

    def get_object(self, queryset=None):
        # Filtramos para que solo pueda borrar alimentos de su centro
        return get_object_or_404(
            Alimento,
            pk=self.kwargs.get('pk'),
            centro=self.request.user.userprofile.centro
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))
        return context    
    
    
def crear_etiqueta(request):
    if request.method == 'POST':
        form = EtiquetaAlimentoForm(request.POST, user=request.user)
        if form.is_valid():
            etiqueta = form.save()
            return redirect('dashuser:etiqueta_pdf', pk=etiqueta.pk)
    else:
        form = EtiquetaAlimentoForm(user=request.user)

    contexto = {'form': form}
    contexto.update(datos_centro(request))
    return render(request, 'dashuser/crear_etiqueta.html', contexto)




def etiqueta_pdf(request, pk):
    etiqueta = get_object_or_404(EtiquetaAlimento, pk=pk)

    # Generar QR con información clave
    qr_data = f"Alimento: {etiqueta.alimento.nombre}\nLote: {etiqueta.lote}\nCaducidad: {etiqueta.fecha_caducidad}"
    qr_img = qrcode.make(qr_data)
    # Guardar QR en buffer en memoria
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # Renderizar template con QR
    html_string = render_to_string('dashuser/etiqueta_pdf.html', {
        'etiqueta': etiqueta,
        'qr_base64': qr_base64
    })
    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    # CSS personalizado para tamaño de página y márgenes
    css = CSS(string='@page { size: 60mm auto; margin: 5mm; }')

    # Generar PDF con CSS
    pdf = html.write_pdf(stylesheets=[css])

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=etiqueta_{etiqueta.id}.pdf'
    return response



######################################################################################
##################################  UTENSILIOS  #######################################
######################################################################################


class UtensilioList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Utensilio"
    model = Utensilio
    template_name = 'dashuser/listar_utensilio.html'
    context_object_name = 'utensilios'
    paginate_by = 10 

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Utensilio.objects.filter(centro=centro).order_by('id')

                search_query = self.request.GET.get('buscar')
                ordering = self.request.GET.get('ordenar') 

                if search_query:
                    queryset = queryset.filter(Q(nombre__icontains=search_query))

                # Aplicamos el ordenamiento según la selección del usuario
                if ordering == 'nombre':
                    queryset = queryset.order_by('nombre')
                elif ordering == 'stock_bajo':
                    queryset = queryset.filter(stock_actual__lt=F('stock_minimo')).order_by('stock_actual')

                return queryset
            else:
                return Utensilio.objects.none()
        except ObjectDoesNotExist:
            return Utensilio.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay alérgenos asociados
        if not context['utensilios'].exists():
            context['mensaje'] = "No tiene utensilios asociados."

        return context


 
class UtensilioDetail(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "Utensilio"
    model = Utensilio
    template_name = 'dashuser/datos_utensilio.html'
    context_object_name = 'utensilio'

    def get_object(self):
        """Obtiene el utensilio asegurando que pertenece al centro del usuario."""
        user_profile = self.request.user.userprofile
        return get_object_or_404(Utensilio, id=self.kwargs['pk'], centro=user_profile.centro)
    


class UtensilioCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Utensilio"
    model = Utensilio
    form_class = UtensilioForm
    template_name = 'dashuser/crear_utensilio.html'
    success_url = reverse_lazy('dashuser:UtensilioList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Utensilio creado correctamente.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)


    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
    
class UtensilioUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Utensilio"
    model = Utensilio
    template_name = 'dashuser/detalle_utensilio.html'
    form_class = UtensilioForm
    success_url = reverse_lazy('dashuser:UtensilioList')
    context_object_name = 'utensilio'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Utensilio.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return Utensilio.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Utensilio actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)  
    
    
    
class UtensilioDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Utensilio"
    model = Utensilio
    template_name = 'dashuser/utensilio_confirm_delete.html'
    success_url = reverse_lazy('dashuser:UtensilioList')
    context_object_name = 'utensilio'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Utensilio.objects.filter(centro=user_profile.centro)
        else:
            return Utensilio.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.save
        messages.success(self.request, 'Tipo e Alimento eliminado correctamente.')
        return super().delete(request, *args, **kwargs)    
