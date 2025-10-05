from django.shortcuts import render, redirect
from app.super.models import UserProfile
from django.utils.timezone import localtime
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Q
from decimal import Decimal
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from PyPDF2 import PdfMerger
import weasyprint
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from app.dashuser.views import datos_centro
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from app.core.mixins import PaginationMixin, PermisoMixin
from .models import TipoPlato, Plato, Salsa, Receta, EtiquetaPlato, TextoModo, NuticionalesSalsa, DatosNuticionales
from .forms import TipoPlatoForm, PlatoForm, AlimentoPlatoFormSet, SalsaForm, AlimentoSalsaFormSet, RecetaForm, GenerarEtiquetaForm, DatosNuticionalesForm, TextoModoForm
import qrcode
import json
import base64




######################################################################################
###############################     TIPO PLATOS   ####################################
######################################################################################


class TipoPlatoList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "TipoPlato"
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
    
    
class TipoPlatoCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "TipoPlato"
    model = TipoPlato
    form_class = TipoPlatoForm
    template_name = 'platos/crear_tipoplato.html'
    success_url = reverse_lazy('platos:TipoPlatoList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Tipo de plato creado correctamente.')
            return super().form_valid(form)  # solo guarda 1 vez
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)


    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
    
class TipoPlatoUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "TipoPlato"
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
    

class TipoPlatoDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "TipoPlato"
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


class TextoModoList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "TextoModo"
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
    
    
class TextoModoCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "TextoModo"
    model = TextoModo
    form_class = TextoModoForm
    template_name = 'platos/crear_textomodo.html'
    success_url = reverse_lazy('platos:TextoModoList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Texto de modo de uso creado correctamente.')
            return super().form_valid(form)  # solo guarda 1 vez
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
        messages.success(self.request, 'Texto de modo de uso actualizados correctamente.')
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
    

class TextoModoDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "TextoModo"
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

class PlatoList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Plato"
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
    
    
    
class PlatoCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Plato"
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
        else:
            context['ingredientes_formset'] = AlimentoPlatoFormSet(prefix='ingredientes')

        return context

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if not user_profile.centro:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

        context = self.get_context_data()
        ingredientes_formset = context['ingredientes_formset']

        # Guardamos plato primero sin commit
        self.object = form.save(commit=False)
        self.object.centro = user_profile.centro
        self.object.save()

        # Ingredientes
        if ingredientes_formset.is_valid():
            ingredientes = ingredientes_formset.save(commit=False)
            total_cantidad = 0
            for ingrediente in ingredientes:
                ingrediente.plato = self.object
                ingrediente.centro = user_profile.centro
                ingrediente.save()
                total_cantidad += float(ingrediente.cantidad)

            for obj in ingredientes_formset.deleted_objects:
                obj.delete()

            # Recalcular datos nutricionales
            nutricion_data = {
                'energia': 0,
                'grasas_totales': 0,
                'grasas_saturadas': 0,
                'hidratosdecarbono': 0,
                'azucares': 0,
                'proteinas': 0,
                'sal': 0
            }

            # Ingredientes del plato
            if total_cantidad > 0:
                for ingrediente in self.object.ingredientes.all():
                    if hasattr(ingrediente.alimento, 'nutricion'):
                        factor = float(ingrediente.cantidad) / total_cantidad
                        n = ingrediente.alimento.nutricion
                        nutricion_data['energia'] += float(n.energia) * factor
                        nutricion_data['grasas_totales'] += float(n.grasas_totales) * factor
                        nutricion_data['grasas_saturadas'] += float(n.grasas_saturadas) * factor
                        nutricion_data['hidratosdecarbono'] += float(n.hidratosdecarbono) * factor
                        nutricion_data['azucares'] += float(n.azucares) * factor
                        nutricion_data['proteinas'] += float(n.proteinas) * factor
                        nutricion_data['sal'] += float(n.sal) * factor

            # Ingredientes de la salsa si existe
            if self.object.salsa and hasattr(self.object.salsa, 'nutricion'):
                s = self.object.salsa.nutricion
                # Suponemos que la salsa entra como 100% de su aporte (podrías ajustar si quieres %)
                for key in nutricion_data.keys():
                    nutricion_data[key] += float(getattr(s, key))

            # Guardar datos nutricionales del plato
            datos_nutricionales, created = DatosNuticionales.objects.get_or_create(
                plato=self.object,
                defaults={'centro': user_profile.centro, **nutricion_data}
            )
            if not created:
                for key, value in nutricion_data.items():
                    setattr(datos_nutricionales, key, value)
                datos_nutricionales.save()

            messages.success(self.request, 'Plato creado correctamente.')
            return super().form_valid(form)
        else:
            # errores ingredientes
            for form_ing in ingredientes_formset:
                if form_ing.errors:
                    for field, errors in form_ing.errors.items():
                        for error in errors:
                            messages.error(self.request, f"Ingrediente: {field} - {error}")

            return self.form_invalid(form)

        
        
class PlatoUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Plato"
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

        # Formset de ingredientes (sin form de nutrición)
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

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ingredientes_formset = context['ingredientes_formset']

        if ingredientes_formset.is_valid():
            user_profile = get_object_or_404(UserProfile, user=self.request.user)

            # Guardar plato
            self.object = form.save(commit=False)
            self.object.centro = user_profile.centro
            self.object.save()

            # Guardar ingredientes
            ingredientes = ingredientes_formset.save(commit=False)
            total_cantidad = 0
            for ingrediente in ingredientes:
                ingrediente.plato = self.object
                ingrediente.centro = user_profile.centro
                ingrediente.save()
                total_cantidad += float(ingrediente.cantidad)
            for obj in ingredientes_formset.deleted_objects:
                obj.delete()

            # Recalcular datos nutricionales
            nutricion_data = {
                'energia': 0,
                'grasas_totales': 0,
                'grasas_saturadas': 0,
                'hidratosdecarbono': 0,
                'azucares': 0,
                'proteinas': 0,
                'sal': 0
            }

            # Ingredientes del plato
            if total_cantidad > 0:
                for ingrediente in self.object.ingredientes.all():
                    if hasattr(ingrediente.alimento, 'nutricion'):
                        factor = float(ingrediente.cantidad) / total_cantidad
                        n = ingrediente.alimento.nutricion
                        nutricion_data['energia'] += float(n.energia) * factor
                        nutricion_data['grasas_totales'] += float(n.grasas_totales) * factor
                        nutricion_data['grasas_saturadas'] += float(n.grasas_saturadas) * factor
                        nutricion_data['hidratosdecarbono'] += float(n.hidratosdecarbono) * factor
                        nutricion_data['azucares'] += float(n.azucares) * factor
                        nutricion_data['proteinas'] += float(n.proteinas) * factor
                        nutricion_data['sal'] += float(n.sal) * factor

            # Ingredientes de la salsa si existe
            if self.object.salsa and hasattr(self.object.salsa, 'nutricion'):
                s = self.object.salsa.nutricion
                for key in nutricion_data.keys():
                    nutricion_data[key] += float(getattr(s, key))

            # Guardar o actualizar datos nutricionales del plato
            datos_nutricionales, created = DatosNuticionales.objects.get_or_create(
                plato=self.object,
                defaults={'centro': user_profile.centro, **nutricion_data}
            )
            if not created:
                for key, value in nutricion_data.items():
                    setattr(datos_nutricionales, key, value)
                datos_nutricionales.save()

            messages.success(self.request, 'Plato actualizado correctamente.')
            return redirect(self.get_success_url())
        else:
            # Mostrar errores si los hay
            for form_ing in ingredientes_formset:
                if form_ing.errors:
                    for field, errors in form_ing.errors.items():
                        for error in errors:
                            messages.error(self.request, f"Ingrediente: {field} - {error}")
            return self.form_invalid(form)


        

class PlatoDetail(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "Plato"
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


    
    

class PlatoDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Plato"
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


class SalsaList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Salsa"
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
    

class SalsaCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Salsa"
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
            total_cantidad = Decimal(0)
            
            # Guardamos ingredientes y calculamos cantidad total de salsa
            for ingrediente in ingredientes:
                ingrediente.salsa = self.object
                ingrediente.centro = user_profile.centro
                ingrediente.save()
                total_cantidad += ingrediente.cantidad
            
            for obj in ingredientes_formset.deleted_objects:
                obj.delete()
            
            # 🔹 Calcular y guardar nutrición proporcional
            self._calcular_nutricion(total_cantidad)
            
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
    
    def _calcular_nutricion(self, total_cantidad):
        """Calcula los datos nutricionales de la salsa por 100g"""
        from decimal import Decimal
        
        # Inicializamos acumuladores
        nutrientes = {
            'energia': Decimal(0),
            'grasas_totales': Decimal(0),
            'grasas_saturadas': Decimal(0),
            'hidratosdecarbono': Decimal(0),
            'azucares': Decimal(0),
            'proteinas': Decimal(0),
            'sal': Decimal(0),
        }
        
        if total_cantidad == 0:
            return  # Evitamos división por cero

        for ingrediente in self.object.ingredientes.all():
            factor = ingrediente.cantidad / total_cantidad  # Proporción de 100g
            nut = ingrediente.alimento.nutricion  # InformacionNutricional del alimento

            nutrientes['energia'] += nut.energia * factor
            nutrientes['grasas_totales'] += nut.grasas_totales * factor
            nutrientes['grasas_saturadas'] += nut.grasas_saturadas * factor
            nutrientes['hidratosdecarbono'] += nut.hidratosdecarbono * factor
            nutrientes['azucares'] += nut.azucares * factor
            nutrientes['proteinas'] += nut.proteinas * factor
            nutrientes['sal'] += nut.sal * factor
        
        # Guardamos o actualizamos en NuticionalesSalsa
        NuticionalesSalsa.objects.update_or_create(
            salsa=self.object,
            defaults={
                'centro': self.object.centro,
                **nutrientes
            }
        )


class SalsaUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Salsa"
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
                instance=self.object,
                prefix='ingredientes'
            )
        else:
            context['ingredientes_formset'] = AlimentoSalsaFormSet(
                instance=self.object,
                prefix='ingredientes'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ingredientes_formset = context['ingredientes_formset']

        if ingredientes_formset.is_valid():
            user_profile = get_object_or_404(UserProfile, user=self.request.user)
            
            # Guardamos salsa
            self.object = form.save(commit=False)
            self.object.centro = user_profile.centro
            self.object.save()

            # Guardamos ingredientes
            ingredientes = ingredientes_formset.save(commit=False)
            total_cantidad = 0  # para calcular proporción
            for ingrediente in ingredientes:
                ingrediente.salsa = self.object
                ingrediente.centro = user_profile.centro
                ingrediente.save()
                total_cantidad += float(ingrediente.cantidad)
            
            for obj in ingredientes_formset.deleted_objects:
                obj.delete()
            
            # Recalcular datos nutricionales
            if total_cantidad > 0:
                nutricion_data = {
                    'energia': 0,
                    'grasas_totales': 0,
                    'grasas_saturadas': 0,
                    'hidratosdecarbono': 0,
                    'azucares': 0,
                    'proteinas': 0,
                    'sal': 0
                }
                
                for ingrediente in self.object.ingredientes.all():
                    if hasattr(ingrediente.alimento, 'nutricion'):
                        factor = float(ingrediente.cantidad) / total_cantidad
                        n = ingrediente.alimento.nutricion
                        nutricion_data['energia'] += float(n.energia) * factor
                        nutricion_data['grasas_totales'] += float(n.grasas_totales) * factor
                        nutricion_data['grasas_saturadas'] += float(n.grasas_saturadas) * factor
                        nutricion_data['hidratosdecarbono'] += float(n.hidratosdecarbono) * factor
                        nutricion_data['azucares'] += float(n.azucares) * factor
                        nutricion_data['proteinas'] += float(n.proteinas) * factor
                        nutricion_data['sal'] += float(n.sal) * factor

                # Guardar o actualizar objeto NuticionalesSalsa
                nutricion_obj, created = NuticionalesSalsa.objects.get_or_create(
                    salsa=self.object,
                    defaults={'centro': user_profile.centro, **nutricion_data}
                )
                if not created:
                    for key, value in nutricion_data.items():
                        setattr(nutricion_obj, key, value)
                    nutricion_obj.save()

            messages.success(self.request, 'Salsa actualizada correctamente.')
            return redirect(self.get_success_url())
        else:
            # Mostrar errores específicos del formset
            for form_ing in ingredientes_formset:
                if form_ing.errors:
                    for field, errors in form_ing.errors.items():
                        for error in errors:
                            messages.error(self.request, f"Ingrediente: {field} - {error}")
            return self.form_invalid(form)

        

class SalsaDetail(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "Salsa"
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
    
    

class SalsaDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Salsa"
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


class RecetaCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Receta"
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
    
    
class RecetaDetailView(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "Receta"
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
    
class RecetaUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Receta"
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


class EtiquetaDetail(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "EtiquetaPlato"
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
        
        context['texto'] = plato.texto.texto if plato.texto else ''
        
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
        accion = request.POST.get("accion")
        etiquetas_ids = request.POST.getlist("etiquetas")

        if accion == "imprimir":
            if not etiquetas_ids:
                messages.warning(request, "⚠️ Debes seleccionar al menos una etiqueta para imprimir.")
                return redirect("platos:generar_etiqueta")

            request.session["etiquetas_a_imprimir"] = etiquetas_ids
            return redirect("platos:imprimir_etiquetas")

        elif accion == "eliminar":
            if not etiquetas_ids:
                messages.warning(request, "⚠️ Debes seleccionar al menos una etiqueta para eliminar.")
                return redirect("platos:generar_etiqueta")

            # Eliminar etiquetas seleccionadas
            EtiquetaPlato.objects.filter(id__in=etiquetas_ids).delete()

            # También eliminarlas de la sesión
            session_ids = request.session.get("etiquetas_ids", [])
            request.session["etiquetas_ids"] = [eid for eid in session_ids if str(eid) not in etiquetas_ids]
            request.session.modified = True

            messages.success(request, f"✅ Se eliminaron {len(etiquetas_ids)} etiqueta(s).")
            return redirect("platos:generar_etiqueta")

        # Si no es acción de imprimir ni eliminar, asumimos que es creación
        form = GenerarEtiquetaForm(request.POST)
        cantidad = int(request.POST.get("cantidad", 1))

        if form.is_valid():
            plato = form.cleaned_data["plato"]
            peso = form.cleaned_data["peso"]

            for _ in range(cantidad):
                nutricion = getattr(plato, 'nutricion', None)
                etiqueta = EtiquetaPlato.objects.create(
                    plato=plato,
                    peso=peso,
                    energia=getattr(nutricion, 'energia', 0),
                    carbohidratos=getattr(nutricion, 'hidratosdecarbono', 0),
                    proteinas=getattr(nutricion, 'proteinas', 0),
                    grasas_totales=getattr(nutricion, 'grasas_totales', 0),
                    azucares=getattr(nutricion, 'azucares', 0),
                    sal=getattr(nutricion, 'sal', 0),
                    grasas_saturadas=getattr(nutricion, 'grasas_saturadas', 0),
                    centro=plato.centro
                )

                # Guardar en sesión
                if "etiquetas_ids" not in request.session:
                    request.session["etiquetas_ids"] = []
                request.session["etiquetas_ids"].append(etiqueta.id)

            request.session.modified = True
            messages.success(request, f"✅ Se generaron {cantidad} etiqueta(s).")
            return redirect("platos:generar_etiqueta")

    else:
        form = GenerarEtiquetaForm()

    etiquetas_ids = request.session.get("etiquetas_ids", [])
    etiquetas = EtiquetaPlato.objects.filter(
        id__in=etiquetas_ids, impresa=False
    ).select_related('plato')

    contexto_centro = datos_centro(request)
    return render(request, "platos/generar_etiqueta.html", {
        "form": form,
        "etiquetas": etiquetas,
        **contexto_centro
    })
    
    
def generar_etiqueta(request):
    # Recuperar lista de IDs de etiquetas pendientes en sesión
    etiquetas_ids = request.session.get("etiquetas_ids", [])

    # Instanciar formulario con platos filtrados por centro
    if request.method == "POST":
        form = GenerarEtiquetaForm(request.POST, user=request.user)
        accion = request.POST.get("accion")
        selected_ids = request.POST.getlist("etiquetas")
        cantidad = int(request.POST.get("cantidad", 1))

        # 🔹 ACCIÓN: ELIMINAR
        if accion == "eliminar" and selected_ids:
            EtiquetaPlato.objects.filter(id__in=selected_ids).delete()
            # Actualizar sesión
            request.session["etiquetas_ids"] = [i for i in etiquetas_ids if str(i) not in selected_ids]
            request.session.modified = True
            return redirect("platos:generar_etiqueta")

        # 🔹 ACCIÓN: IMPRIMIR
        elif accion == "imprimir" and selected_ids:
            etiquetas = EtiquetaPlato.objects.filter(id__in=selected_ids).select_related("plato")
            merger = PdfMerger()

            for etiqueta in etiquetas:
                plato = etiqueta.plato
                ingredientes_info = plato.get_ingredientes_con_info()

                # Recolectar alérgenos y trazas
                todos_alergenos = set()
                todas_trazas = set()
                for ing in ingredientes_info:
                    todos_alergenos.update(ing.get("alergenos", []))
                    todas_trazas.update(ing.get("trazas", []))

                # Generar QR
                url = request.build_absolute_uri(reverse('platos:etiqueta_qr', args=[etiqueta.pk]))
                qr_img = qrcode.make(url)
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")
                qr_base64 = base64.b64encode(buffer.getvalue()).decode()

                context = {
                    "etiqueta": etiqueta,
                    "ingredientes_info": ingredientes_info,
                    "todos_alergenos": list(todos_alergenos),
                    "todas_trazas": list(todas_trazas),
                    "texto_modo_empleo": plato.texto.texto if plato.texto else "",
                    "qr_base64": qr_base64,
                }

                html = render_to_string("platos/preview_etiqueta.html", context)
                pdf_buffer = BytesIO()
                html_obj = HTML(string=html, base_url=request.build_absolute_uri())
                css = CSS(string='@page { size: 100mm auto; margin: 5mm; }')
                html_obj.write_pdf(pdf_buffer, stylesheets=[css])
                pdf_buffer.seek(0)
                merger.append(pdf_buffer)

                # Marcar como impresa
                etiqueta.impresa = True
                etiqueta.save()

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = 'inline; filename="etiquetas.pdf"'
            merger.write(response)
            merger.close()
            return response

        # 🔹 ACCIÓN: GENERAR NUEVAS ETIQUETAS
        elif form.is_valid():
            plato = form.cleaned_data["plato"]
            peso = form.cleaned_data["peso"]

            for _ in range(cantidad):
                nutricion = getattr(plato, "nutricion", None)
                etiqueta = EtiquetaPlato.objects.create(
                    plato=plato,
                    peso=peso,
                    energia=getattr(nutricion, "energia", 0) if nutricion else 0,
                    carbohidratos=getattr(nutricion, "hidratosdecarbono", 0) if nutricion else 0,
                    proteinas=getattr(nutricion, "proteinas", 0) if nutricion else 0,
                    grasas_totales=getattr(nutricion, "grasas_totales", 0) if nutricion else 0,
                    azucares=getattr(nutricion, "azucares", 0) if nutricion else 0,
                    sal=getattr(nutricion, "sal", 0) if nutricion else 0,
                    grasas_saturadas=getattr(nutricion, "grasas_saturadas", 0) if nutricion else 0,
                    centro=plato.centro
                )
                # Guardar en sesión
                etiquetas_ids.append(etiqueta.id)

            request.session["etiquetas_ids"] = etiquetas_ids
            request.session.modified = True
            return redirect("platos:generar_etiqueta")

    else:
        form = GenerarEtiquetaForm(user=request.user)

    # Consultar etiquetas pendientes
    etiquetas = EtiquetaPlato.objects.filter(id__in=etiquetas_ids, impresa=False).select_related("plato")
    contexto = datos_centro(request)

    return render(request, "platos/generar_etiqueta.html", {
        "form": form,
        "etiquetas": etiquetas,
        **contexto
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
    
    texto_modo_empleo = plato.texto.texto if plato.texto else ""

    context = {
        "etiqueta": etiqueta,
        "ingredientes_info": ingredientes_info,
        "todos_alergenos": list(todos_alergenos),
        "todas_trazas": list(todas_trazas),
        "qr_base64": qr_base64,
        "texto_modo_empleo": texto_modo_empleo,
    }

    print("Texto modo empleo:", plato.texto.texto if plato.texto else "Sin texto")
    print("Contexto PDF:", context)
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
            plato = etiqueta.plato
            ingredientes_info = plato.get_ingredientes_con_info()

            todos_alergenos = set()
            todas_trazas = set()
            for ing in ingredientes_info:
                if ing.get("alergenos"):
                    todos_alergenos.update(ing["alergenos"])
                if ing.get("trazas"):
                    todas_trazas.update(ing["trazas"])

            url = request.build_absolute_uri(
                reverse('platos:etiqueta_qr', args=[etiqueta.pk])
            )

            qr_img = qrcode.make(url)
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()

            texto_modo_empleo = plato.texto.texto if plato.texto else ""

            context = {
                "etiqueta": etiqueta,
                "ingredientes_info": ingredientes_info,
                "todos_alergenos": list(todos_alergenos),
                "todas_trazas": list(todas_trazas),
                "texto_modo_empleo": texto_modo_empleo,
                "qr_base64": qr_base64
            }

            html = render_to_string("platos/preview_etiqueta.html", context)

            etiqueta.impresa = True
            etiqueta.save()

            pdf_buffer = BytesIO()
            html_obj = HTML(string=html, base_url=request.build_absolute_uri())
            css = CSS(string='@page { size: 100mm auto; margin: 5mm; }')

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

    # 👇 Si llega por GET (o sin etiquetas seleccionadas), redirigir con mensaje
    messages.warning(request, "⚠️ Debes seleccionar al menos una etiqueta para imprimir.")
    return redirect("platos:generar_etiqueta")

    

######################################################################################
##################################     LOTES   #######################################
######################################################################################

class LotesResumenListView(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "EtiquetaPlato"
    template_name = "platos/lotes_resumen.html"
    context_object_name = "lotes_agrupados"
    paginate_by = 10

    def get_queryset(self):
        # Parámetros GET
        sort_field = self.request.GET.get("sort", "fecha")
        sort_order = self.request.GET.get("order", "desc")
        buscar = self.request.GET.get("buscar", "").strip().lower()

        # Recuperar etiquetas impresas del centro del usuario
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile and user_profile.centro:
            centro = user_profile.centro
            etiquetas = EtiquetaPlato.objects.filter(
                impresa=True, plato__centro=centro
            ).order_by("-fecha")
        else:
            etiquetas = EtiquetaPlato.objects.none()

        # Agrupar en lista plana
        lotes_agrupados = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"cantidad_total": 0, "num_platos": 0})))
        for e in etiquetas:
            fecha_str = e.fecha.strftime("%d/%m/%Y") if e.fecha else "Sin fecha"
            turno = "A"
            if e.lote and "-" in e.lote:
                partes = e.lote.split("-")
                if len(partes) >= 3:
                    turno = partes[-2]
            plato_nombre = e.plato.nombre
            lote_agrupado = e.lote[:-4] if e.lote and len(e.lote) > 4 else e.lote

            lotes_agrupados[fecha_str][plato_nombre][turno]["cantidad_total"] += float(e.peso)
            lotes_agrupados[fecha_str][plato_nombre][turno]["num_platos"] += 1
            lotes_agrupados[fecha_str][plato_nombre][turno]["lote"] = lote_agrupado

        # Convertir a lista plana
        lotes_list = []
        for fecha, platos in lotes_agrupados.items():
            for plato_nombre, turnos in platos.items():
                for turno, datos in turnos.items():
                    lotes_list.append({
                        "fecha": fecha,
                        "plato": plato_nombre,
                        "turno": turno,
                        "lote": datos.get("lote", ""),
                        "cantidad_total": datos["cantidad_total"],
                        "num_platos": datos["num_platos"]
                    })

        # Filtrar por búsqueda
        if buscar:
            lotes_list = [
                lote for lote in lotes_list
                if buscar in lote["plato"].lower() 
                   or buscar in lote["lote"].lower()
                   or buscar in lote["turno"].lower()
            ]

        # Ordenar según GET
        reverse = sort_order == "desc"
        if sort_field == "fecha":
            lotes_list.sort(key=lambda x: datetime.strptime(x["fecha"], "%d/%m/%Y") if x["fecha"] != "Sin fecha" else datetime.min, reverse=reverse)
        elif sort_field == "plato":
            lotes_list.sort(key=lambda x: x["plato"], reverse=reverse)

        return lotes_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Parámetros para la plantilla
        context["current_sort"] = self.request.GET.get("sort", "fecha")
        context["current_order"] = self.request.GET.get("order", "desc")
        context["buscar"] = self.request.GET.get("buscar", "")
        return context

 
    
class LoteDetalleListView(PermisoMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "EtiquetaPlato"
    model = EtiquetaPlato
    template_name = "platos/lote_detalle.html"
    context_object_name = "raciones"

    def get_queryset(self):
        lote = self.kwargs.get("lote")

        # Recuperar centro del usuario
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile and user_profile.centro:
            centro = user_profile.centro
            queryset = EtiquetaPlato.objects.filter(
                lote__startswith=lote,
                impresa=True,
                plato__centro=centro
            ).order_by("plato__nombre", "fecha")
        else:
            queryset = EtiquetaPlato.objects.none()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos el lote agrupado para mostrar en el título del modal
        lote = self.kwargs.get("lote")
        context['lote'] = lote
        return context



def reimprimir_etiqueta(request, pk):
    etiqueta = get_object_or_404(EtiquetaPlato, pk=pk)
    plato = etiqueta.plato
    ingredientes_info = plato.get_ingredientes_con_info()

    todos_alergenos = set()
    todas_trazas = set()
    for ing in ingredientes_info:
        todos_alergenos.update(ing["alergenos"])
        todas_trazas.update(ing["trazas"])

    # URL pública de la vista de la ración (nuevo QR)
    url = request.build_absolute_uri(
        reverse('platos:etiqueta_qr', args=[etiqueta.pk])
    )

    qr_img = qrcode.make(url)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    texto_modo_empleo = plato.texto.texto if plato.texto else ""

    context = {
        "etiqueta": etiqueta,
        "plato": plato,
        "ingredientes_info": ingredientes_info,
        "todos_alergenos": list(todos_alergenos),
        "todas_trazas": list(todas_trazas),
        "texto_modo_empleo": texto_modo_empleo,
        "qr_base64": qr_base64
    }

    html = render_to_string("platos/preview_etiqueta.html", context)
    pdf_buffer = BytesIO()
    html_obj = HTML(string=html, base_url=request.build_absolute_uri())
    css = CSS(string='@page { size: 60mm auto; margin: 0; }')
    html_obj.write_pdf(pdf_buffer, stylesheets=[css], presentational_hints=True)
    pdf_buffer.seek(0)

    response = HttpResponse(pdf_buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="etiqueta_{etiqueta.id}.pdf"'
    return response



def reimprimir_etiquetas(request):
    if request.method == "POST":
        accion = request.POST.get("accion")
        ids = request.POST.getlist("etiquetas")
        etiquetas = EtiquetaPlato.objects.filter(id__in=ids)

        if not etiquetas.exists():
            return HttpResponse("No se seleccionaron etiquetas.", status=400)

        if accion == "eliminar":
            etiquetas.delete()
            # Redirigir a la misma página para refrescar el listado
            return redirect(request.META.get('HTTP_REFERER', '/'))

        elif accion == "imprimir":
            merger = PdfMerger()

            for etiqueta in etiquetas:
                plato = etiqueta.plato
                ingredientes_info = plato.get_ingredientes_con_info()

                todos_alergenos = set()
                todas_trazas = set()
                for ing in ingredientes_info:
                    if ing.get("alergenos"):
                        todos_alergenos.update(ing["alergenos"])
                    if ing.get("trazas"):
                        todas_trazas.update(ing["trazas"])

                url = request.build_absolute_uri(
                    reverse('platos:etiqueta_qr', args=[etiqueta.pk])
                )

                qr_img = qrcode.make(url)
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")
                qr_base64 = base64.b64encode(buffer.getvalue()).decode()

                texto_modo_empleo = plato.texto.texto if plato.texto else ""

                context = {
                    "etiqueta": etiqueta,
                    "plato": plato,
                    "ingredientes_info": ingredientes_info,
                    "todos_alergenos": list(todos_alergenos),
                    "todas_trazas": list(todas_trazas),
                    "texto_modo_empleo": texto_modo_empleo,
                    "qr_base64": qr_base64
                }

                html = render_to_string("platos/preview_etiqueta.html", context)
                pdf_buffer = BytesIO()
                html_obj = HTML(string=html, base_url=request.build_absolute_uri())
                css = CSS(string='@page { size: 60mm auto; margin: 0; }')
                html_obj.write_pdf(pdf_buffer, stylesheets=[css], presentational_hints=True)
                pdf_buffer.seek(0)
                merger.append(pdf_buffer)

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = 'inline; filename="etiquetas.pdf"'
            merger.write(response)
            merger.close()
            return response

        else:
            return HttpResponse("Acción no reconocida.", status=400)



def etiqueta_qr_view(request, pk):
    etiqueta = get_object_or_404(EtiquetaPlato, pk=pk)
    plato = etiqueta.plato
    ingredientes_info = plato.get_ingredientes_con_info()

    # Cálculo caducidad
    fecha_caducidad = None
    if plato.vida_util and etiqueta.fecha:
        fecha_caducidad = etiqueta.fecha + timedelta(days=plato.vida_util)

    # Receta asociada (si existe)
    receta = plato.receta

    todos_alergenos = set()
    todas_trazas = set()
    for ing in ingredientes_info:
        todos_alergenos.update(ing["alergenos"])
        todas_trazas.update(ing["trazas"])

    return render(request, "platos/etiqueta_qr.html", {
        "etiqueta": etiqueta,
        "plato": plato,
        "ingredientes_info": ingredientes_info,
        "todos_alergenos": list(todos_alergenos),
        "todas_trazas": list(todas_trazas),
        "fecha_caducidad": fecha_caducidad,
        "receta": receta,
    })
