from django.shortcuts import render
from app.super.models import UserProfile
from django.utils.timezone import localtime
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from app.core.mixins import PaginationMixin
from .models import TipoPlato, Plato
from .forms import TipoPlatoForm, PlatoForm, AlimentoPlatoFormSet



def datos_centro(request):
    hora_actual = localtime().hour  # Obtiene la hora actual en la zona horaria configurada
    if 5 <= hora_actual < 12:
        saludo = "Buenos días"
    elif 12 <= hora_actual < 18:
        saludo = "Buenas tardes"
    else:
        saludo = "Buenas noches"
        
    # obtenemos el perfil del usuario logueado
    user_profile = UserProfile.objects.get(user=request.user)
    
    # obtenemos el centro asociado al perfil
    centro = user_profile.centro
    imagen = user_profile.imagen
    cargo = user_profile.cargo
    nombre = user_profile.nombre
    apellidos = user_profile.apellidos
    
     # Comprobamos si el centro tiene una imagen
    if imagen and user_profile.imagen:
        imagen_user_url = user_profile.imagen.url  # obtenemos la URL de la imagen
    else:
        imagen_user_url = None  # Si no hay imagen
        
    # Comprobamos si el centro tiene una imagen
    if centro and centro.imagen:
        imagen_centro_url = centro.imagen.url  # obtenemos la URL de la imagen
    else:
        imagen_centro_url = None  # Si no hay imagen

    # Retornar el contexto con la URL del logo
    return {'imagen_centro_url': imagen_centro_url, 'imagen_user_url': imagen_user_url, 'centro': centro, 'cargo': cargo, 'nombre': nombre, 'apellidos': apellidos, 'saludo': saludo}



######################################################################################
###############################     TIPO PLATOS   ####################################
######################################################################################


class TipoPlatoList(PaginationMixin, LoginRequiredMixin, ListView):
    model = TipoPlato
    template_name = 'platos/listar_tipoplato.html'
    context_object_name = 'tipoplatos'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = TipoPlato.objects.filter(centro=centro).order_by('id')

                
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query)
                    )
                return queryset
            else:
                return TipoPlato.objects.none()
        except ObjectDoesNotExist:
            return TipoPlato.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay alérgenos asociados
        if not context['tipoplatos'].exists():
            context['mensaje'] = "No tiene tipos de utensilio asociados."

        return context
    
    
class TipoPlatoCreate(LoginRequiredMixin, CreateView):
    model = TipoPlato
    form_class = TipoPlatoForm
    template_name = 'platos/crear_tipoplato.html'
    success_url = reverse_lazy('platos:TipoPlatoList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            tipoplatos = form.save(commit=False)
            tipoplatos.centro = user_profile.centro
            tipoplatos.save()
            messages.success(self.request, 'Tipo de plato creado correctamente.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
    
class TipoPlatoUpdate(LoginRequiredMixin, UpdateView):
    model = TipoPlato
    template_name = 'platos/detalle_tipoplato.html'
    form_class = TipoPlatoForm
    context_object_name = 'tipoplato'  
    pk_url_kwarg = 'pk' 

    def get_success_url(self):
        messages.success(self.request, 'Tipo de plato actualizado correctamente.')
        return reverse_lazy('platos:TipoPlatoList')

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if not user_profile.centro:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return TipoPlato.objects.none()
        return TipoPlato.objects.filter(centro=user_profile.centro)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_url'] = reverse('platos:TipoPlatoUpdate', kwargs={'pk': self.object.pk})
        return context

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    

class TipoPlatoDelete(LoginRequiredMixin, DeleteView):
    model = TipoPlato
    template_name = 'platos/tipoplato_confirm_delete.html'
    success_url = reverse_lazy('platos:TipoPlatoList')
    context_object_name = 'tipoplato'  # Cambiado a singular para consistencia
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        """Filtra los tipos de plato por centro del usuario"""
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if not user_profile.centro:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return TipoPlato.objects.none()
        return TipoPlato.objects.filter(centro=user_profile.centro)

    def delete(self, request, *args, **kwargs):
        """Maneja la eliminación y muestra mensaje de éxito"""
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Tipo de plato eliminado correctamente.')
        return response

    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto"""
        context = super().get_context_data(**kwargs)
        context['action_url'] = reverse('menu:TipoPlatoDelete', kwargs={'pk': self.object.pk})
        return context
    
    
    
######################################################################################
###############################       PLATOS      ####################################
######################################################################################    

class PlatoList(PaginationMixin, LoginRequiredMixin, ListView):
    model = Plato
    template_name = 'platos/listar_platos.html'
    context_object_name = 'platos'
    paginate_by = 12

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            queryset = Plato.objects.filter(centro=user_profile.centro).order_by('nombre')
            
            search_query = self.request.GET.get('buscar')
            if search_query:
                queryset = queryset.filter(nombre__icontains=search_query)
            
            return queryset
        return Plato.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))
        if not context['platos'].exists():
            context['mensaje'] = "No tiene platos registrados."
        return context
    
    
    
class PlatoCreate(LoginRequiredMixin, CreateView):
    model = Plato
    form_class = PlatoForm
    template_name = 'platos/crear_plato.html'
    success_url = reverse_lazy('platos:PlatoList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ingredientes_formset'] = AlimentoPlatoFormSet(
                self.request.POST, 
                self.request.FILES,
                prefix='ingredientes'
            )
        else:
            context['ingredientes_formset'] = AlimentoPlatoFormSet(
                prefix='ingredientes'
            )
        return context

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if not user_profile.centro:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)
        
        context = self.get_context_data()
        ingredientes_formset = context['ingredientes_formset']
        
        self.object = form.save(commit=False)
        self.object.centro = user_profile.centro
        self.object.save()
        
        if ingredientes_formset.is_valid():
            ingredientes = ingredientes_formset.save(commit=False)
            for ingrediente in ingredientes:
                ingrediente.plato = self.object
                ingrediente.centro = user_profile.centro
                ingrediente.save()
            
            for obj in ingredientes_formset.deleted_objects:
                obj.delete()
            
            messages.success(self.request, 'Plato creado correctamente.')
            return super().form_valid(form)
        else:
            # Mostrar errores específicos del formset
            for form_ing in ingredientes_formset:
                if form_ing.errors:
                    for field, errors in form_ing.errors.items():
                        for error in errors:
                            messages.error(self.request, f"Ingrediente: {field} - {error}")
            return self.form_invalid(form)    
        
        
class PlatoUpdate(LoginRequiredMixin, UpdateView):
    model = Plato
    form_class = PlatoForm
    template_name = 'platos/detalle_plato.html'
    success_url = reverse_lazy('platos:PlatoList')
    context_object_name = 'plato'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Plato.objects.filter(centro=user_profile.centro)
        return Plato.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ingredientes_formset'] = AlimentoPlatoFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['ingredientes_formset'] = AlimentoPlatoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ingredientes_formset = context['ingredientes_formset']
        
        if ingredientes_formset.is_valid():
            self.object = form.save()
            ingredientes = ingredientes_formset.save(commit=False)
            
            for ingrediente in ingredientes:
                ingrediente.centro = self.object.centro
                ingrediente.save()
            
            for obj in ingredientes_formset.deleted_objects:
                obj.delete()
            
            messages.success(self.request, 'Plato actualizado correctamente.')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
        

class PlatoDetail(LoginRequiredMixin, DetailView):
    model = Plato
    template_name = 'platos/datos_plato.html'
    context_object_name = 'plato'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Plato.objects.filter(centro=user_profile.centro)
        return Plato.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ingredientes = self.object.ingredientes.all().select_related('alimento', 'unidad_medida')
        context['ingredientes'] = ingredientes
        context['alergenos'] = self.object.get_alergenos()

        return context

    
    

class PlatoDelete(LoginRequiredMixin, DeleteView):
    model = Plato
    template_name = 'platos/plato_confirm_delete.html'
    success_url = reverse_lazy('platos:PlatoList')
    context_object_name = 'plato'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Plato.objects.filter(centro=user_profile.centro)
        else:
            return Plato.objects.none()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Plato eliminado correctamente.')
        return super().delete(request, *args, **kwargs)        