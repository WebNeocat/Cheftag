from django.shortcuts import render, redirect
from app.super.models import UserProfile
from django.utils.timezone import localtime
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.db.models import Q
from io import BytesIO
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from app.core.mixins import PaginationMixin
from .models import TipoPlato, Plato, Salsa, Receta, EtiquetaPlato
from .forms import TipoPlatoForm, PlatoForm, AlimentoPlatoFormSet, SalsaForm, AlimentoSalsaFormSet, RecetaForm, GenerarEtiquetaForm
import qrcode
import json
import base64



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
        context['action_url'] = reverse('platos:TipoPlatoDelete', kwargs={'pk': self.object.pk})
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

        # Ingredientes de la salsa (si el plato tiene salsa)
        if self.object.salsa:
            ingredientes_salsa = self.object.salsa.ingredientes.all().select_related('alimento', 'unidad_medida')
        else:
            ingredientes_salsa = []
        context['ingredientes_salsa'] = ingredientes_salsa
        
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
    
    
######################################################################################
##############################   SALSAS Y FONDOS   ###################################
######################################################################################


class SalsaList(PaginationMixin, LoginRequiredMixin, ListView):
    model = Salsa
    template_name = 'platos/listar_salsas.html'
    context_object_name = 'salsas'
    paginate_by = 10

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            queryset = Salsa.objects.filter(centro=user_profile.centro).order_by('nombre')
            
            search_query = self.request.GET.get('buscar')
            if search_query:
                queryset = queryset.filter(nombre__icontains=search_query)
            
            return queryset
        return Plato.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))
        if not context['salsas'].exists():
            context['mensaje'] = "No tiene salsas registradas."
        return context
    

class SalsaCreate(LoginRequiredMixin, CreateView):
    model = Salsa
    form_class = SalsaForm
    template_name = 'platos/crear_salsa.html'
    success_url = reverse_lazy('platos:SalsaList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ingredientes_formset'] = AlimentoSalsaFormSet(
                self.request.POST, 
                self.request.FILES,
                prefix='ingredientes'
            )
        else:
            context['ingredientes_formset'] = AlimentoSalsaFormSet(
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
                ingrediente.salsa = self.object
                ingrediente.centro = user_profile.centro
                ingrediente.save()
            
            for obj in ingredientes_formset.deleted_objects:
                obj.delete()
            
            messages.success(self.request, 'Salsa creada correctamente.')
            return super().form_valid(form)
        else:
            # Mostrar errores específicos del formset
            for form_ing in ingredientes_formset:
                if form_ing.errors:
                    for field, errors in form_ing.errors.items():
                        for error in errors:
                            messages.error(self.request, f"Ingrediente: {field} - {error}")
            return self.form_invalid(form)


class SalsaUpdate(LoginRequiredMixin, UpdateView):
    model = Salsa
    form_class = SalsaForm
    template_name = 'platos/detalle_salsa.html'
    success_url = reverse_lazy('platos:SalsaList')
    context_object_name = 'salsa'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Salsa.objects.filter(centro=user_profile.centro)
        return Salsa.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ingredientes_formset'] = AlimentoSalsaFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['ingredientes_formset'] = AlimentoSalsaFormSet(instance=self.object)
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
            
            messages.success(self.request, 'Salsa actualizada correctamente.')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
        

class SalsaDetail(LoginRequiredMixin, DetailView):
    model = Salsa
    template_name = 'platos/datos_salsa.html'
    context_object_name = 'salsa'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Salsa.objects.filter(centro=user_profile.centro)
        return Salsa.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ingredientes = self.object.ingredientes.all().select_related('alimento', 'unidad_medida')
        context['ingredientes'] = ingredientes
        context['alergenos'] = self.object.get_alergenos()
        return context
    
    

class SalsaDelete(LoginRequiredMixin, DeleteView):
    model = Salsa
    template_name = 'platos/salsa_confirm_delete.html'
    success_url = reverse_lazy('platos:SalsaList')
    context_object_name = 'salsa'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Salsa.objects.filter(centro=user_profile.centro)
        else:
            return Salsa.objects.none()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Salsa eliminada correctamente.')
        return super().delete(request, *args, **kwargs)
    
    
######################################################################################
###############################       RECETAS     ####################################
######################################################################################


class RecetaCreate(LoginRequiredMixin, CreateView):
    model = Receta
    form_class = RecetaForm
    template_name = 'platos/crear_receta.html'

    def get_form_kwargs(self):
        """Pasamos el plato_id al formulario"""
        kwargs = super().get_form_kwargs()
        kwargs['plato_id'] = self.kwargs['plato_id']
        return kwargs

    def get_context_data(self, **kwargs):
        """Aseguramos que el plato existe y pertenece al centro"""
        context = super().get_context_data(**kwargs)
        plato = get_object_or_404(
            Plato,
            pk=self.kwargs['plato_id'],
            centro=self.request.user.userprofile.centro
        )
        context['plato'] = plato
        return context

    def form_valid(self, form):
        """Procesamos el formulario válido"""
        try:
            # Asignamos centro y plato antes de guardar
            form.instance.centro = self.request.user.userprofile.centro
            form.instance.plato_id = self.kwargs['plato_id']
            
            # Llamamos al form_valid del padre que incluye el AuditMixin
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'Error al guardar: {str(e)}')
            return self.form_invalid(form)

    def get_success_url(self):
        """URL a la que redirigir después de guardar"""
        return reverse('platos:PlatoList')

    def form_invalid(self, form):
        """Manejo de errores de validación"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Error en {field}: {error}')
        return super().form_invalid(form)
    
    
class RecetaDetailView(LoginRequiredMixin, DetailView):
    model = Receta
    template_name = 'platos/detalle_receta.html'
    context_object_name = 'receta'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Receta.objects.filter(centro=user_profile.centro)
        return Receta.objects.none()

    def get_object(self, queryset=None):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return get_object_or_404(
            Receta,
            pk=self.kwargs['pk'],
            centro=user_profile.centro
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))
        receta = self.get_object()
        
        # Agregar ingredientes al contexto
        context['ingredientes'] = receta.plato.ingredientes.all()
        
        # Calcular tiempo total
        context['tiempo_total'] = receta.tiempo_preparacion + receta.tiempo_coccion
        
        return context
    
class RecetaUpdate(LoginRequiredMixin, UpdateView):
    model = Receta
    form_class = RecetaForm
    template_name = 'platos/editar_receta.html'
    context_object_name = 'receta'

    def get_queryset(self):
        """Limita recetas solo del centro del usuario"""
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return Receta.objects.filter(centro=user_profile.centro)

    def get_object(self, queryset=None):
        """Obtiene receta asegurando que pertenece al centro del usuario"""
        receta = super().get_object(queryset)

        return receta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))
        context['plato'] = self.object.plato
        return context

    def get_form_kwargs(self):
        """Agrega el plato_id al form"""
        kwargs = super().get_form_kwargs()
        kwargs['plato_id'] = self.object.plato_id
        return kwargs

    def form_valid(self, form):
        try:
            # Ya está asociada a un plato y centro, solo guardamos llamando al padre
            response = super().form_valid(form)  # Esto ejecutará el form_valid de AuditMixin
            messages.success(self.request, 'Receta actualizada correctamente.')
            return response
        except Exception as e:
            messages.error(self.request, f'Error al actualizar: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Error en {field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('platos:PlatoList')
    
    
######################################################################################
###############################     ETIQUETAS     ####################################
######################################################################################    


# Añade esto en tu archivo views.py de la app platos
class EtiquetaDetail(LoginRequiredMixin, DetailView):
    model = Plato
    template_name = 'platos/etiqueta_plato.html'
    context_object_name = 'plato'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Plato.objects.filter(centro=user_profile.centro)
        return Plato.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el plato
        plato = self.object
        
        # Obtener ingredientes del plato
        ingredientes = plato.ingredientes.all().select_related('alimento', 'unidad_medida')
        context['ingredientes'] = ingredientes
        
        # Obtener ingredientes de la salsa (si el plato tiene salsa)
        if plato.salsa:
            ingredientes_salsa = plato.salsa.ingredientes.all().select_related('alimento', 'unidad_medida')
        else:
            ingredientes_salsa = []
        context['ingredientes_salsa'] = ingredientes_salsa
        
        # Obtener alérgenos del plato
        context['alergenos'] = plato.get_alergenos()
        
        # Calcular información nutricional total
        info_nutricional_total = self.calcular_info_nutricional_total(ingredientes, ingredientes_salsa)
        context['info_nutricional_total'] = info_nutricional_total
        
        # Calcular información nutricional por porción
        if plato.receta and plato.receta.rendimiento > 0:
            info_nutricional_porcion = self.calcular_info_nutricional_porcion(info_nutricional_total, plato.receta.rendimiento)
            context['info_nutricional_porcion'] = info_nutricional_porcion
        
        # Añadir datos del centro
        context.update(datos_centro(self.request))
        
        return context

    def calcular_info_nutricional_total(self, ingredientes, ingredientes_salsa):
        """
        Calcula la información nutricional total sumando todos los ingredientes
        tanto del plato como de la salsa (si existe), considerando que los valores
        nutricionales en la BD están expresados por 100g/100ml
        """
        # Inicializar todos los valores en 0
        totales = {
            'energia': 0,
            'carbohidratos': 0,
            'proteinas': 0,
            'grasas': 0,
            'azucares': 0,
            'sal_mg': 0,
            'acido_folico': 0,
            'vitamina_c': 0,
            'vitamina_a': 0,
            'zinc': 0,
            'hierro': 0,
            'calcio': 0,
            'colesterol': 0,
            'acidos_grasos_polinsaturados': 0,
            'acidos_grasos_monoinsaturados': 0,
            'acidos_grasos_saturados': 0,
            'fibra': 0,
        }
        
        # Función para procesar cada ingrediente
        def procesar_ingrediente(ingrediente):
            if hasattr(ingrediente.alimento, 'nutricion') and ingrediente.alimento.nutricion:
                nutricion = ingrediente.alimento.nutricion
                # Calcular factor de conversión según la cantidad y unidad de medida
                factor = self.calcular_factor_conversion(ingrediente)
                
                # Sumar cada valor nutricional multiplicado por el factor de conversión
                totales['energia'] += float(nutricion.energia or 0) * factor
                totales['carbohidratos'] += float(nutricion.carbohidratos or 0) * factor
                totales['proteinas'] += float(nutricion.proteinas or 0) * factor
                totales['grasas'] += float(nutricion.grasas or 0) * factor
                totales['azucares'] += float(nutricion.azucares or 0) * factor
                totales['sal_mg'] += float(nutricion.sal_mg or 0) * factor
                totales['acido_folico'] += float(nutricion.acido_folico or 0) * factor
                totales['vitamina_c'] += float(nutricion.vitamina_c or 0) * factor
                totales['vitamina_a'] += float(nutricion.vitamina_a or 0) * factor
                totales['zinc'] += float(nutricion.zinc or 0) * factor
                totales['hierro'] += float(nutricion.hierro or 0) * factor
                totales['calcio'] += float(nutricion.calcio or 0) * factor
                totales['colesterol'] += float(nutricion.colesterol or 0) * factor
                totales['acidos_grasos_polinsaturados'] += float(nutricion.acidos_grasos_polinsaturados or 0) * factor
                totales['acidos_grasos_monoinsaturados'] += float(nutricion.acidos_grasos_monoinsaturados or 0) * factor
                totales['acidos_grasos_saturados'] += float(nutricion.acidos_grasos_saturados or 0) * factor
                totales['fibra'] += float(nutricion.fibra or 0) * factor
        
        # Procesar ingredientes del plato
        for ingrediente in ingredientes:
            procesar_ingrediente(ingrediente)
        
        # Procesar ingredientes de la salsa
        for ingrediente in ingredientes_salsa:
            procesar_ingrediente(ingrediente)
        
        # Redondear todos los valores a 2 decimales
        for key in totales:
            totales[key] = round(totales[key], 2)
        
        return totales

    def calcular_factor_conversion(self, ingrediente):
        """
        Calcula el factor de conversión para ajustar los valores nutricionales
        según la cantidad real utilizada del ingrediente.
        
        Los valores nutricionales en la BD están por 100g/100ml,
        así que calculamos: (cantidad / 100) * factor_unidad
        """
        cantidad = float(ingrediente.cantidad or 0)
        unidad = ingrediente.unidad_medida.abreviatura.lower()
        
        # Factores de conversión según el tipo de unidad
        # Para unidades de peso (g, kg) y volumen (ml, l)
        factores = {
            'g': 1.0,          # gramos - mismo factor
            'kg': 1000.0,      # kilogramos a gramos
            'mg': 0.001,       # miligramos a gramos
            'ml': 1.0,         # mililitros - mismo factor (asumiendo densidad ~1g/ml)
            'l': 1000.0,       # litros a mililitros
            'cl': 10.0,        # centilitros a mililitros
            'dl': 100.0,       # decilitros a mililitros
        }
        
        # Obtener factor de conversión o usar 1.0 por defecto
        factor_unidad = factores.get(unidad, 1.0)
        
        # Calcular factor total: (cantidad * factor_unidad) / 100
        # porque los valores nutricionales son por 100g/100ml
        return (cantidad * factor_unidad) / 100.0

    def calcular_info_nutricional_porcion(self, info_nutricional_total, rendimiento):
        """
        Calcula la información nutricional por porción
        """
        porcion = {}
        for key, value in info_nutricional_total.items():
            porcion[key] = round(value / rendimiento, 2)
        return porcion
    


def generar_etiqueta(request):
    etiqueta = None

    if request.method == "POST":
        form = GenerarEtiquetaForm(request.POST)
        if form.is_valid():
            plato = form.cleaned_data["plato"]
            peso = form.cleaned_data["peso"]

            # Usamos el método del modelo Plato que calculamos antes
            nutricion = plato.calcular_nutricion(peso)

            # Guardamos la etiqueta
            etiqueta = EtiquetaPlato.objects.create(
                plato=plato,
                peso=peso,
                energia=nutricion["energia"],
                carbohidratos=nutricion["carbohidratos"],
                proteinas=nutricion["proteinas"],
                grasas=nutricion["grasas"],
                azucares=nutricion["azucares"],
                sal_mg=nutricion["sal_mg"],
                fibra=nutricion["fibra"],
                centro=plato.centro  # porque hereda de ModeloBaseCentro
            )

            return redirect("platos:preview_etiqueta", etiqueta_id=etiqueta.id)
    else:
        form = GenerarEtiquetaForm()

    return render(request, "platos/generar_etiqueta.html", {
        "form": form,
        "etiqueta": etiqueta
    }) 
    


def preview_etiqueta(request, etiqueta_id):
    etiqueta = get_object_or_404(EtiquetaPlato, id=etiqueta_id)
    plato = etiqueta.plato

    ingredientes_info = plato.get_ingredientes_con_info()

    # Recopilar todos los alérgenos y trazas
    todos_alergenos = set()
    todas_trazas = set()
    for ing in ingredientes_info:
        if ing.get("alergenos"):
            todos_alergenos.update(ing["alergenos"])
        if ing.get("trazas"):
            todas_trazas.update(ing["trazas"])

    # Crear contenido del QR
    qr_data = {
        "nombre": plato.nombre,
        "peso": float(etiqueta.peso),
        "ingredientes": [
            {"nombre": i["nombre"], "alergenos": i["alergenos"]}
            for i in ingredientes_info
        ],
        "alergenos_totales": list(todos_alergenos),
        "trazas": list(todas_trazas),
        "nutricion": {
            "energia": float(etiqueta.energia),
            "proteinas": float(etiqueta.proteinas),
            "grasas": float(etiqueta.grasas),
            "carbohidratos": float(etiqueta.carbohidratos),
            "azucares": float(etiqueta.azucares),
            "sal": float(etiqueta.sal_mg)
        },
        #"caducidad": etiqueta.caducidad.isoformat() if etiqueta.caducidad else "",
        "lote": str(etiqueta.lote) if etiqueta.lote else ""
    }

    qr_json = json.dumps(qr_data, ensure_ascii=False)

    # Generar QR
    qr_img = qrcode.make(qr_json)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        "etiqueta": etiqueta,
        "ingredientes_info": ingredientes_info,
        "todos_alergenos": list(todos_alergenos),
        "todas_trazas": list(todas_trazas),
        "qr_base64": qr_base64
    }

    return render(request, "platos/preview_etiqueta.html", context)

    