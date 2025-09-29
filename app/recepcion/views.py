from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.views.generic.list import ListView
from app.super.models import UserProfile
from app.core.mixins import PaginationMixin
from .models import Proveedor, Recepcion
from .forms import ProveedorForm, RecepcionForm
from app.dashuser.views import datos_centro




######################################################################################
###############################  PROVEEDORES  ########################################
######################################################################################

class ProveedorList(PaginationMixin, LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = 'recepcion/listar_proveedor.html'
    context_object_name = 'proveedores'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Proveedor.objects.filter(centro=centro).order_by('id')

                # Permitir búsqueda dentro de los proveedores del centro
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query) |
                        Q(pais=search_query) |
                        Q(activo=search_query) 
                    )
                return queryset
            else:
                return Proveedor.objects.none()
        except ObjectDoesNotExist:
            return Proveedor.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay alérgenos asociados
        if not context['proveedores'].exists():
            context['mensaje'] = "No tiene proveedores asociados."

        return context
    
    
    
class ProveedorCreate(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'recepcion/crear_proveedor.html'
    success_url = reverse_lazy('recepcion:ProveedorList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            proveedores = form.save(commit=False)
            proveedores.centro = user_profile.centro
            proveedores.save()
            messages.success(self.request, 'Proveedor creado correctamente.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)


class ProveedorUpdate(LoginRequiredMixin, UpdateView):
    model = Proveedor
    template_name = 'recepcion/editar_proveedor.html'
    form_class = ProveedorForm
    success_url = reverse_lazy('recepcion:ProveedorList')
    context_object_name = 'proveedor'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Proveedor.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return Proveedor.objects.none()

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Proveedor actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   
    

class ProveedorDelete(LoginRequiredMixin, DeleteView):
    model = Proveedor
    template_name = 'recepcion/proveedor_confirm_delete.html'
    success_url = reverse_lazy('recepcion:ProveedorList')
    context_object_name = 'proveedor'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Proveedor.objects.filter(centro=user_profile.centro)
        else:
            return Proveedor.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.save
        messages.success(self.request, 'Alérgeno eliminado correctamente.')
        return super().delete(request, *args, **kwargs) 
    
    
class ProveedorDetailView(DetailView):
    model = Proveedor
    template_name = 'recepcion/detalle_proveedor.html'
    context_object_name = 'proveedor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))  # Añadimos datos del centro (usuario)
        return context
        
        

######################################################################################
###############################  RECEPCIONES  ########################################
######################################################################################


class RecepcionManualList(PaginationMixin, LoginRequiredMixin, ListView):
    model = Recepcion
    template_name = 'recepcion/listar_recepcion_manual.html'
    context_object_name = 'recepciones'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Recepcion.objects.filter(centro=centro).order_by('id')

                # Permitir búsqueda dentro de los proveedores del centro
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(alimento__icontains=search_query) |
                        Q(proveedor=search_query) |
                        Q(lote=search_query) |
                        Q(fecha_recepcion=search_query) 
                    )
                return queryset
            else:
                return Recepcion.objects.none()
        except ObjectDoesNotExist:
            return Recepcion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay alérgenos asociados
        if not context['recepciones'].exists():
            context['mensaje'] = "No tiene recepciones asociadas."

        return context
    

class RecepcionManualCreate(LoginRequiredMixin, CreateView):
    model = Recepcion
    form_class = RecepcionForm
    template_name = 'recepcion/crear_recepcion_manual.html'
    success_url = reverse_lazy('recepcion:RecepcionManualList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            recepciones = form.save(commit=False)
            recepciones.centro = user_profile.centro
            recepciones.save()
            
            # Actualizar stock automáticamente
            alimento = recepciones.alimento
            alimento.stock_actual += recepciones.cantidad
            alimento.save()
            
            messages.success(self.request, 'Recepcion entrada correctamente.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
    
    
class RecepcionManualDetail(LoginRequiredMixin, DetailView):
    model = Recepcion
    template_name = 'recepcion/detalle_recepcion_manual.html'
    context_object_name = 'recepcion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))  # Añadimos datos del centro (usuario)
        return context    
        
        
class RecepcionManualDelete(LoginRequiredMixin, DeleteView):
    model = Recepcion
    template_name = 'recepcion/recepcionmanual_confirm_delete.html'
    success_url = reverse_lazy('recepcion:RecepcionList')
    context_object_name = 'recepcion'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Recepcion.objects.filter(centro=user_profile.centro)
        else:
            return Recepcion.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.save
        messages.success(self.request, 'Recepcion eliminada correctamenta.')
        return super().delete(request, *args, **kwargs)         