from django.shortcuts import render, redirect
from app.super.models import UserProfile
from django.utils.timezone import localtime
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from collections import defaultdict
from django.db.models import Q
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from PyPDF2 import PdfMerger
import weasyprint
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from app.core.mixins import PaginationMixin
from .models import TipoPlato, Plato, Salsa, Receta, EtiquetaPlato, TextoModo
from .forms import TipoPlatoForm, PlatoForm, AlimentoPlatoFormSet, SalsaForm, AlimentoSalsaFormSet, RecetaForm, GenerarEtiquetaForm, DatosNuticionalesForm, TextoModoForm
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
###########################     TEXTO MODO DE USO    #################################
######################################################################################


class TextoModoList(PaginationMixin, LoginRequiredMixin, ListView):
    model = TextoModo
    template_name = 'platos/listar_textomodo.html'
    context_object_name = 'textomodos'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = TextoModo.objects.filter(centro=centro).order_by('id')

                
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query)
                    )
                return queryset
            else:
                return TextoModo.objects.none()
        except ObjectDoesNotExist:
            return TextoModo.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay textos de uso asociados
        if not context['textomodos'].exists():
            context['mensaje'] = "No tiene tipos de textos de uso asociados."

        return context
    
    
class TextoModoCreate(LoginRequiredMixin, CreateView):
    model = TextoModo
    form_class = TextoModoForm
    template_name = 'platos/crear_textomodo.html'
    success_url = reverse_lazy('platos:TextoModoList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            textomodos = form.save(commit=False)
            textomodos.centro = user_profile.centro
            textomodos.save()
            messages.success(self.request, 'Texto de modo de uso creado correctamente.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
    
class TextoModoUpdate(LoginRequiredMixin, UpdateView):
    model = TextoModo
    template_name = 'platos/detalle_textomodo.html'
    form_class = TextoModoForm
    context_object_name = 'textomodo'  
    pk_url_kwarg = 'pk' 

    def get_success_url(self):
        messages.success(self.request, 'Texto de modo de uso actualizado correctamente.')
        return reverse_lazy('platos:TextoModoList')

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if not user_profile.centro:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return TextoModo.objects.none()
        return TextoModo.objects.filter(centro=user_profile.centro)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_url'] = reverse('platos:TextoModoUpdate', kwargs={'pk': self.object.pk})
        return context

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    

class TextoModoDelete(LoginRequiredMixin, DeleteView):
    model = TextoModo
    template_name = 'platos/textomodo_confirm_delete.html'
    success_url = reverse_lazy('platos:TextoModoList')
    context_object_name = 'textomodo' 
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        """Filtra los tipos de plato por centro del usuario"""
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if not user_profile.centro:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return TextoModo.objects.none()
        return TextoModo.objects.filter(centro=user_profile.centro)

    def delete(self, request, *args, **kwargs):
        """Maneja la eliminación y muestra mensaje de éxito"""
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Texto de modo de uso eliminado correctamente.')
        return response

    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto"""
        context = super().get_context_data(**kwargs)
        context['action_url'] = reverse('platos:TextoModoDelete', kwargs={'pk': self.object.pk})
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
        try: 
            user_profile = get_object_or_404(UserProfile, user=self.request.user)
            if user_profile.centro:
                queryset = Plato.objects.filter(centro=user_profile.centro).order_by('nombre')
                
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query)
                    )         
                return queryset
            else:
                return Plato.objects.none()
        except ObjectDoesNotExist:
            return Plato.objects.none()    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))
        
        # Añadir un mensaje si no hay platos asociados
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

        # formset de ingredientes
        if self.request.POST:
            context['ingredientes_formset'] = AlimentoPlatoFormSet(
                self.request.POST, self.request.FILES, prefix='ingredientes'
            )
            context['nutricion_form'] = DatosNuticionalesForm(self.request.POST, prefix='nutricion')
        else:
            context['ingredientes_formset'] = AlimentoPlatoFormSet(prefix='ingredientes')
            context['nutricion_form'] = DatosNuticionalesForm(prefix='nutricion')

        return context

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if not user_profile.centro:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

        context = self.get_context_data()
        ingredientes_formset = context['ingredientes_formset']
        nutricion_form = context['nutricion_form']

        # Guardamos plato primero sin commit
        self.object = form.save(commit=False)
        self.object.centro = user_profile.centro
        self.object.save()

        # Ingredientes
        if ingredientes_formset.is_valid() and nutricion_form.is_valid():
            ingredientes = ingredientes_formset.save(commit=False)
            for ingrediente in ingredientes:
                ingrediente.plato = self.object
                ingrediente.centro = user_profile.centro
                ingrediente.save()

            for obj in ingredientes_formset.deleted_objects:
                obj.delete()

            # Guardar datos nutricionales
            nutricion = nutricion_form.save(commit=False)
            nutricion.plato = self.object
            nutricion.centro = user_profile.centro
            nutricion.save()

            messages.success(self.request, 'Plato creado correctamente.')
            return super().form_valid(form)
        else:
            # errores ingredientes
            for form_ing in ingredientes_formset:
                if form_ing.errors:
                    for field, errors in form_ing.errors.items():
                        for error in errors:
                            messages.error(self.request, f"Ingrediente: {field} - {error}")
            # errores nutricion
            for field, errors in nutricion_form.errors.items():
                for error in errors:
                    messages.error(self.request, f"Nutrición: {field} - {error}")

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

        # Formset de ingredientes
        if self.request.POST:
            context['ingredientes_formset'] = AlimentoPlatoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix='ingredientes'
            )
        else:
            context['ingredientes_formset'] = AlimentoPlatoFormSet(
                instance=self.object,
                prefix='ingredientes'
            )

        # Form de datos nutricionales
        if self.request.POST:
            if hasattr(self.object, 'nutricion'):
                context['nutricion_form'] = DatosNuticionalesForm(
                    self.request.POST,
                    instance=self.object.nutricion
                )
            else:
                context['nutricion_form'] = DatosNuticionalesForm(self.request.POST)
        else:
            if hasattr(self.object, 'nutricion'):
                context['nutricion_form'] = DatosNuticionalesForm(instance=self.object.nutricion)
            else:
                context['nutricion_form'] = DatosNuticionalesForm()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ingredientes_formset = context['ingredientes_formset']
        nutricion_form = context['nutricion_form']

        if ingredientes_formset.is_valid() and nutricion_form.is_valid():
            self.object = form.save(commit=False)
            user_profile = get_object_or_404(UserProfile, user=self.request.user)
            self.object.centro = user_profile.centro
            self.object.save()

            # Guardar ingredientes
            ingredientes = ingredientes_formset.save(commit=False)
            for ingrediente in ingredientes:
                ingrediente.plato = self.object
                ingrediente.centro = user_profile.centro
                ingrediente.save()
            for obj in ingredientes_formset.deleted_objects:
                obj.delete()

            # Guardar datos nutricionales
            nutricion = nutricion_form.save(commit=False)
            nutricion.plato = self.object
            # Asignar centro siempre
            if not nutricion.centro_id:
                nutricion.centro = self.object.centro
            nutricion.save()

            messages.success(self.request, 'Plato actualizado correctamente.')
            return super().form_valid(form)
        else:
            # Mostrar errores si los hay
            for formset in [ingredientes_formset, nutricion_form]:
                for f in getattr(formset, 'forms', [formset]):
                    if f.errors:
                        for field, errors in f.errors.items():
                            for error in errors:
                                messages.error(self.request, f"{field}: {error}")
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

        # Ingredientes del plato
        ingredientes = self.object.ingredientes.all().select_related('alimento', 'unidad_medida')
        context['ingredientes'] = ingredientes
        context['alergenos'] = self.object.get_alergenos()

        # Ingredientes de la salsa (si el plato tiene salsa)
        if self.object.salsa:
            ingredientes_salsa = self.object.salsa.ingredientes.all().select_related('alimento', 'unidad_medida')
        else:
            ingredientes_salsa = []
        context['ingredientes_salsa'] = ingredientes_salsa

        # Datos Nutricionales (puede ser None si no los hemos creado aún)
        context['nutricion'] = getattr(self.object, 'nutricion', None)

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
        
        # Obtener datos nutricionales directamente del modelo
        if hasattr(plato, 'nutricion') and plato.nutricion:
            info_nutricional_total = self.obtener_info_nutricional_total(plato.nutricion)
            context['info_nutricional_total'] = info_nutricional_total
            
            # Calcular información nutricional por porción si hay receta
            if plato.receta and plato.receta.rendimiento > 0:
                info_nutricional_porcion = self.calcular_info_nutricional_porcion(
                    info_nutricional_total, plato.receta.rendimiento
                )
                context['info_nutricional_porcion'] = info_nutricional_porcion
        
        # Añadir datos del centro
        context.update(datos_centro(self.request))
        
        return context

    def obtener_info_nutricional_total(self, nutricion):
        return {
            'energia': float(nutricion.energia or 0),
            'grasas_totales': float(nutricion.grasas_totales or 0),
            'grasas_saturadas': float(nutricion.grasas_saturadas or 0),
            'carbohidratos': float(nutricion.hidratosdecarbono or 0),
            'azucares': float(nutricion.azucares or 0),
            'proteinas': float(nutricion.proteinas or 0),
            'sal': float(nutricion.sal or 0),
        }
    

def generar_etiqueta(request):
    if request.method == "POST":
        form = GenerarEtiquetaForm(request.POST)
        if form.is_valid():
            plato = form.cleaned_data["plato"]
            peso = form.cleaned_data["peso"]

            # Obtener datos nutricionales directamente del modelo
            if hasattr(plato, 'nutricion') and plato.nutricion:
                nutricion = plato.nutricion
                try:
                    etiqueta = EtiquetaPlato.objects.create(
                        plato=plato,
                        peso=peso,
                        energia=nutricion.energia,
                        carbohidratos=nutricion.hidratosdecarbono,
                        proteinas=nutricion.proteinas,
                        grasas_totales=nutricion.grasas_totales,
                        azucares=nutricion.azucares,
                        sal=nutricion.sal,
                        grasas_saturadas=nutricion.grasas_saturadas,
                        centro=plato.centro
                    )

                    # Guardar en sesión
                    if "etiquetas_ids" not in request.session:
                        request.session["etiquetas_ids"] = []
                    
                    request.session["etiquetas_ids"].append(etiqueta.id)
                    request.session.modified = True

                except Exception as e:
                    print(f"Error al crear etiqueta: {e}")
            else:
                # Crear etiqueta con valores por defecto si no hay datos nutricionales
                try:
                    etiqueta = EtiquetaPlato.objects.create(
                        plato=plato,
                        peso=peso,
                        energia=0,
                        carbohidratos=0,
                        proteinas=0,
                        grasas_totales=0,
                        azucares=0,
                        sal=0,
                        grasas_saturadas=0,
                        centro=plato.centro
                    )

                    # Guardar en sesión
                    if "etiquetas_ids" not in request.session:
                        request.session["etiquetas_ids"] = []
                    
                    request.session["etiquetas_ids"].append(etiqueta.id)
                    request.session.modified = True

                except Exception as e:
                    print(f"Error al crear etiqueta con valores por defecto: {e}")

            return redirect("platos:generar_etiqueta")
    else:
        form = GenerarEtiquetaForm()

    # Recuperar etiquetas en sesión
    etiquetas_ids = request.session.get("etiquetas_ids", [])
    etiquetas = EtiquetaPlato.objects.filter(id__in=etiquetas_ids, impresa=False).select_related('plato')
    
    
    # Obtener datos del centro para el contexto
    contexto_centro = datos_centro(request)

    return render(request, "platos/generar_etiqueta.html", {
        "form": form,
        "etiquetas": etiquetas,
        **contexto_centro
    })
    
    
    
def preview_etiqueta(request, etiqueta_id):
    etiqueta = get_object_or_404(EtiquetaPlato, id=etiqueta_id)
    plato = etiqueta.plato
    
    # Marcar como impresas inmediatamente
    etiqueta.update(impresa=True)

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
            "grasas_totales": float(etiqueta.grasas_totales),
            "carbohidratos": float(etiqueta.carbohidratos),
            "azucares": float(etiqueta.azucares),
            "sal": float(etiqueta.sal),  # CAMBIADO: sal_mg -> sal
            "grasas_saturadas": float(etiqueta.grasas_saturadas)  # AÑADIDO
        },
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

    # Renderizamos la plantilla como HTML
    html = render_to_string("platos/preview_etiqueta.html", context)

    # Creamos respuesta PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="etiqueta_{etiqueta.id}.pdf"'

    # Generamos PDF
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)
    
    

    return response


def imprimir_etiquetas(request):
    if request.method == "POST":
        ids = request.POST.getlist("etiquetas")
        etiquetas = EtiquetaPlato.objects.filter(id__in=ids)
        
        # Marcar como impresas inmediatamente
        etiquetas.update(impresa=True)

        merger = PdfMerger()

        for etiqueta in etiquetas:
            # Reutilizamos preview_etiqueta pero generando string
            plato = etiqueta.plato
            ingredientes_info = plato.get_ingredientes_con_info()

            todos_alergenos = set()
            todas_trazas = set()
            for ing in ingredientes_info:
                if ing.get("alergenos"):
                    todos_alergenos.update(ing["alergenos"])
                if ing.get("trazas"):
                    todas_trazas.update(ing["trazas"])

            qr_data = {
                "nombre": plato.nombre,
                "peso": float(etiqueta.peso),
                "nutricion": {
                    "energia": float(etiqueta.energia),
                    "proteinas": float(etiqueta.proteinas),
                    "grasas_totales": float(etiqueta.grasas_totales),
                    "carbohidratos": float(etiqueta.carbohidratos),
                    "azucares": float(etiqueta.azucares),
                    "sal": float(etiqueta.sal),  # CAMBIADO: sal_mg -> sal
                    "grasas_saturadas": float(etiqueta.grasas_saturadas)  # AÑADIDO
                },
                "lote": str(etiqueta.lote) if etiqueta.lote else ""
            }

            qr_json = json.dumps(qr_data, ensure_ascii=False)
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

            html = render_to_string("platos/preview_etiqueta.html", context)
            
            # ✅ marcar como impresa
            etiqueta.impresa = True
            etiqueta.save()
            
            pdf_buffer = BytesIO()
            
            # Configuración específica para WeasyPrint con tamaño personalizado
            html_obj = HTML(string=html, base_url=request.build_absolute_uri())
            css = CSS(string='@page { size: 60mm auto; margin: 0; }')
            
            html_obj.write_pdf(
                pdf_buffer,
                stylesheets=[css],
                presentational_hints=True
            )
            
            pdf_buffer.seek(0)
            merger.append(pdf_buffer)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="etiquetas.pdf"'
        merger.write(response)
        merger.close()
        return response
    

######################################################################################
##################################     LOTES   #######################################
######################################################################################


    
class LotesPorDiaTurnoListView(ListView):
    model = EtiquetaPlato
    template_name = "platos/lotes_por_dia_turno.html"
    context_object_name = "lotes"

    def get_queryset(self):
        # Obtener todas las etiquetas ordenadas por fecha
        return EtiquetaPlato.objects.all().order_by("-fecha", "lote")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        etiquetas = context["lotes"]

        # Agrupar por fecha y turno
        lotes_agrupados = defaultdict(lambda: {"A": [], "B": []})

        for e in etiquetas:
            fecha_str = e.fecha.strftime("%Y-%m-%d")
            turno = "A" if e.fecha.hour < 12 else "B"
            lotes_agrupados[fecha_str][turno].append(e)

        context["lotes_agrupados"] = dict(lotes_agrupados)
        return context    
    
class LotesResumenListView(ListView):
    model = EtiquetaPlato
    template_name = "platos/lotes_resumen.html"
    context_object_name = "etiquetas"

    def get_queryset(self):
        # Recuperamos TODAS las etiquetas impresas, no solo de hoy
        return EtiquetaPlato.objects.filter(impresa=True).order_by("fecha", "lote")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        etiquetas = EtiquetaPlato.objects.all().order_by("-fecha")

        from collections import defaultdict
        lotes_agrupados = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"cantidad_total": 0, "num_platos": 0})))

        for e in etiquetas:
            # usamos la fecha de creación o la fecha guardada en etiqueta
            fecha_str = e.fecha.strftime("%d/%m/%Y") if e.fecha else "Sin fecha"

            # extraemos turno correctamente del lote
            turno = "A"
            if e.lote and "-" in e.lote:
                partes = e.lote.split("-")
                if len(partes) >= 3:
                    turno = partes[-2]  # el turno siempre está antes del número

            plato_nombre = e.plato.nombre

            lotes_agrupados[fecha_str][turno][plato_nombre]["cantidad_total"] += float(e.peso)
            lotes_agrupados[fecha_str][turno][plato_nombre]["num_platos"] += 1

        # Convertimos defaultdict a dict
        def recursive_dict(d):
            if isinstance(d, defaultdict):
                return {k: recursive_dict(v) for k, v in d.items()}
            return d

        context["lotes_agrupados"] = recursive_dict(lotes_agrupados)

        context.update(datos_centro(self.request))

        return context
