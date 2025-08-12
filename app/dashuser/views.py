from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from django.utils.timezone import localtime
from django.core.exceptions import ObjectDoesNotExist
from app.core.mixins import PaginationMixin
from app.super.models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Alergenos, TipoAlimento, Alimento, localizacion, Conservacion, InformacionNutricional
from .forms import AlergenosForm, TipoAlimento, LocalizacionForm, TipoAlimentosForm, ConservacionForm, InformacionNutricionalForm, AlimentoForm


@login_required
def home(request):
    return render(request, 'dashuser/home.html')

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
    
    # obtenemos los datos asociados al perfil
    imagen = user_profile.imagen
    cargo = user_profile.cargo
    nombre = user_profile.nombre
    apellidos = user_profile.apellidos
    
     # Comprobamos si el centrousuario tiene una imagen
    if imagen and user_profile.imagen:
        imagen_user_url = user_profile.imagen.url  # obtenemos la URL de la imagen
    else:
        imagen_user_url = None  # Si no hay imagen


    # Retornar el contexto con la URL del logo
    return {'imagen_user_url': imagen_user_url,'cargo': cargo, 'nombre': nombre, 'apellidos': apellidos, 'saludo': saludo}

######################################################################################
###############################  ALERGENOS  ########################################
######################################################################################


class AlergenosList(PaginationMixin, LoginRequiredMixin, ListView):
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
    
    
class AlergenosCreate(LoginRequiredMixin, CreateView):
    model = Alergenos
    form_class = AlergenosForm
    template_name = 'dashuser/crear_alergenos.html'
    success_url = reverse_lazy('dashuser:AlergenosList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            alergenos = form.save(commit=False)
            alergenos.centro = user_profile.centro
            alergenos.save()
            messages.success(self.request, 'Alérgeno creado correctamente.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
class AlergenosUpdate(LoginRequiredMixin, UpdateView):
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
        self.object = form.save()
        messages.success(self.request, 'Alérgeno actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   
    

class AlergenosDelete(LoginRequiredMixin, DeleteView):
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
        obj.last_modified_by = request.user
        obj.save(update_fields=['last_modified_by'])
        messages.success(self.request, 'Alérgeno eliminado correctamente.')
        return super().delete(request, *args, **kwargs) 
    
     
######################################################################################
###############################  TIPO ALIMENTOS  ####################################
######################################################################################


class TipoAlimentoList(PaginationMixin, LoginRequiredMixin, ListView):
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
    
    
class TipoAlimentoCreate(LoginRequiredMixin, CreateView):
    model = TipoAlimento
    form_class = TipoAlimentosForm
    template_name = 'dashuser/crear_tipoalimento.html'
    success_url = reverse_lazy('dashuser:TipoAlimentoList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            tipoalimentos = form.save(commit=False)
            tipoalimentos.centro = user_profile.centro
            tipoalimentos.save()
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
    
    
class TipoAlimentoUpdate(LoginRequiredMixin, UpdateView):
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
        self.object = form.save()
        messages.success(self.request, 'Tipo de alimento actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)  
    
class TipoAlimentoDelete(LoginRequiredMixin, DeleteView):
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


class LocalizacionList(PaginationMixin, LoginRequiredMixin, ListView):
    model = localizacion
    template_name = 'dashuser/listar_localizacion.html'
    context_object_name = 'localizaciones'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = localizacion.objects.filter(centro=centro).order_by('id')


                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(localizacion__icontains=search_query) 
                    )
                return queryset
            else:
                return localizacion.objects.none()
        except ObjectDoesNotExist:
            return localizacion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay localizaciones asociadas
        if not context['localizaciones'].exists():
            context['mensaje'] = "No tiene localizaciones asociadas."

        return context
    
    
class LocalizacionCreate(LoginRequiredMixin, CreateView):
    model = localizacion
    form_class = LocalizacionForm
    template_name = 'dashuser/crear_localizacion.html'
    success_url = reverse_lazy('dashuser:LocalizacionList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            localizacion = form.save(commit=False)
            localizacion.centro = user_profile.centro
            localizacion.save()
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


class LocalizacionUpdate(LoginRequiredMixin, UpdateView):
    model = localizacion
    template_name = 'dashuser/detalle_localizacion.html'
    form_class = LocalizacionForm
    success_url = reverse_lazy('dashuser:LocalizacionList')
    context_object_name = 'localizacion'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return localizacion.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return localizacion.objects.none()

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Localización actualizada correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
 
class LocalizacionDelete(LoginRequiredMixin, DeleteView):
    model = localizacion
    template_name = 'dashuser/localizacion_confirm_delete.html'
    success_url = reverse_lazy('dashuser:LocalizacionList')
    context_object_name = 'localizacion'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return localizacion.objects.filter(centro=user_profile.centro)
        else:
            return localizacion.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.last_modified_by = request.user
        obj.save(update_fields=['last_modified_by'])
        messages.success(self.request, 'Ubicación eliminada correctamente.')
        return super().delete(request, *args, **kwargs)       
    
    
######################################################################################
##############################  CONSERVACIÓN  ########################################
######################################################################################    


class ConservacionList(PaginationMixin, LoginRequiredMixin, ListView):
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
    
    
class ConservacionCreate(LoginRequiredMixin, CreateView):
    model = Conservacion
    form_class = ConservacionForm
    template_name = 'dashuser/crear_conservacion.html'
    success_url = reverse_lazy('dashuser:ConservacionList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            conservacion = form.save(commit=False)
            conservacion.centro = user_profile.centro
            conservacion.save()
            messages.success(self.request, 'Conservacion creada correctamente.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   


class ConservacionUpdate(LoginRequiredMixin, UpdateView):
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
        self.object = form.save()
        messages.success(self.request, 'Conservacion actualizada correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
 
class ConservacionDelete(LoginRequiredMixin, DeleteView):
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

class AlimentoList(PaginationMixin, LoginRequiredMixin, ListView):
    model = Alimento
    template_name = 'dashuser/listar_alimentos.html'
    context_object_name = 'alimentos'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Alimento.objects.filter(centro=centro).order_by('id')


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
    
    
class AlimentoCreate(View):
    def get(self, request):
        alimento_form = AlimentoForm()
        nutricion_form = InformacionNutricionalForm()
        
        context = {
            'alimento_form': alimento_form,
            'nutricion_form': nutricion_form
        }
        context.update(datos_centro(request))  # añadimos el contexto extra
        
        return render(request, 'dashuser/crear_alimento.html', context)
    
    def post(self, request):
        alimento_form = AlimentoForm(request.POST, request.FILES)
        nutricion_form = InformacionNutricionalForm(request.POST)

        if alimento_form.is_valid() and nutricion_form.is_valid():
            alimento = alimento_form.save(commit=False)  # No guardamos aún
            alimento.centro = request.user.userprofile.centro  # asignamos el centro del usuario
            alimento.save()
            
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


class AlimentoDetailView(DetailView):
    model = Alimento
    template_name = 'dashuser/detalle_alimento.html'
    context_object_name = 'alimento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))  # Añadimos datos del centro (usuario)
        return context