from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, TemplateView, FormView
from django.views.generic.list import ListView
from django.views import View
from app.super.models import UserProfile
from app.core.mixins import PaginationMixin, PermisoMixin
from .models import Proveedor, Recepcion, TipoDeMerma, Merma
from .forms import ProveedorForm, RecepcionForm, TipoDeMermaForm, MermaForm, RecepcionFormSet, RecepcionEliminarForm
from app.dashuser.views import datos_centro
from app.dashuser.models import Alimento
import re




######################################################################################
###############################  PROVEEDORES  ########################################
######################################################################################

class ProveedorList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Proveedor"
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
    
    
    
class ProveedorCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Proveedor"
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'recepcion/crear_proveedor.html'
    success_url = reverse_lazy('recepcion:ProveedorList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Proveedor creado correctamente.')
            return super().form_valid(form)  # solo guarda 1 vez
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)


    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)


class ProveedorUpdate(PermisoMixin,LoginRequiredMixin, UpdateView):
    permiso_modulo = "Proveedor"
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
        messages.success(self.request, 'Proveedor actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   
    

class ProveedorDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Proveedor"
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
    
    
class ProveedorDetailView(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "Proveedor"
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


class RecepcionManualList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Recepcion"
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
    

class RecepcionManualCreate(PermisoMixin, LoginRequiredMixin, View):
    permiso_modulo = "Recepcion"
    template_name = 'recepcion/crear_recepcion_manual.html'
    success_url = 'recepcion:RecepcionManualList' 

    def get(self, request, *args, **kwargs):
        formset = RecepcionFormSet(queryset=Recepcion.objects.none())
        return render(request, self.template_name, {'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = RecepcionFormSet(request.POST, queryset=Recepcion.objects.none())
        user_profile = get_object_or_404(UserProfile, user=request.user)

        if formset.is_valid() and user_profile.centro:
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    recepcion = form.save(commit=False)
                    recepcion.centro = user_profile.centro
                    recepcion.save()
                    # Actualizar stock
                    alimento = recepcion.alimento
                    alimento.stock_actual += recepcion.cantidad
                    alimento.save()
            messages.success(request, 'Recepciones registradas correctamente.')
            return redirect(self.success_url)
        else:
            messages.error(request, 'Error al guardar las recepciones o no estás asociado a un centro.')
            return render(request, self.template_name, {'formset': formset})

    
    
class RecepcionManualUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Recepcion"
    model = Recepcion
    form_class = RecepcionForm
    template_name = 'recepcion/editar_recepcion_manual.html'
    context_object_name = 'recepcion'
    success_url = reverse_lazy('recepcion:RecepcionManualList')

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Recepcion.objects.filter(centro=user_profile.centro)
        else:
            return Recepcion.objects.none()

    def form_valid(self, form):
        old_recepcion = form.instance.__class__.objects.get(pk=form.instance.pk)
        
        # Ajustar stock antes de guardar
        diferencia = form.instance.cantidad - old_recepcion.cantidad
        form.instance.alimento.stock_actual += diferencia
        form.instance.alimento.save()

        return super().form_valid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)



    
class RecepcionManualDetail(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "Recepcion"
    model = Recepcion
    template_name = 'recepcion/detalle_recepcion_manual.html'
    context_object_name = 'recepcion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))  # Añadimos datos del centro (usuario)
        return context    
        
        
class RecepcionManualDeleteFormView(PermisoMixin, LoginRequiredMixin, FormView):
    permiso_modulo = "Recepcion"
    template_name = 'recepcion/recepcionmanual_confirm_delete.html'
    form_class = RecepcionEliminarForm
    success_url = reverse_lazy('recepcion:RecepcionManualList')

    def get_initial(self):
        return {'recepcion_id': self.kwargs['pk']}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recepcion'] = get_object_or_404(Recepcion, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        recepcion_id = form.cleaned_data['recepcion_id']
        recepcion = get_object_or_404(Recepcion, pk=recepcion_id)

        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if recepcion.centro != user_profile.centro:
            messages.error(self.request, "No puedes eliminar recepciones de otro centro.")
            return super().form_invalid(form)

        # Actualizar stock
        recepcion.alimento.stock_actual -= recepcion.cantidad
        recepcion.alimento.save()

        # Eliminar la recepción
        recepcion.delete()

        messages.success(self.request, f"Recepción de {recepcion.alimento} eliminada correctamente.")
        return super().form_valid(form) 
    
    
    
def parse_gs1_128(code):
    """
    Devuelve un diccionario con los datos extraídos de un GS1-128.
    """
    data = {}
    # Expresiones regulares simples para los AIs que nos interesan
    gtin_match = re.search(r'\(01\)(\d{14})', code)
    lote_match = re.search(r'\(10\)([^\(]+)', code)
    caducidad_match = re.search(r'\(17\)(\d{6})', code)

    if gtin_match:
        data['gtin'] = gtin_match.group(1)
    if lote_match:
        data['lote'] = lote_match.group(1)
    if caducidad_match:
        # Convertimos YYMMDD a fecha
        data['fecha_caducidad'] = datetime.strptime(caducidad_match.group(1), "%y%m%d").date()

    return data    

def recepcion_gs1(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo")

        # ⚡ Parsear GS1 (ejemplo sencillo)
        # (01) = GTIN, (10) = Lote, (17) = Fecha caducidad
        gtin = codigo[codigo.find("01")+2:codigo.find("01")+16]
        lote = codigo[codigo.find("10")+2:codigo.find("17")]
        fecha_caducidad_raw = codigo[codigo.find("17")+2:codigo.find("17")+8]
        fecha_caducidad = f"20{fecha_caducidad_raw[:2]}-{fecha_caducidad_raw[2:4]}-{fecha_caducidad_raw[4:]}"

        try:
            alimento = Alimento.objects.get(gtin=gtin)
        except Alimento.DoesNotExist:
            messages.error(request, f"No existe un alimento con GTIN {gtin}. Selección manual requerida.")
            return render(request, "recepcion/recepcion_gs1.html")

        # 🚨 proveedor: aquí puedes pedirlo en el formulario o asignar uno por defecto
        proveedor = Proveedor.objects.first()

        Recepcion.objects.create(
            proveedor=proveedor,
            alimento=alimento,
            lote=lote,
            fecha_caducidad=fecha_caducidad,
            cantidad=1
        )

        messages.success(request, f"Recepción registrada: {alimento.nombre}, lote {lote}.")
        return redirect("recepcion_gs1")

    return render(request, "recepcion/recepcion_gs1.html")



######################################################################################
##############################    TIPO DE MERMAS  ####################################
######################################################################################

class TipoDeMermaList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "TipoMerma"
    model = TipoDeMerma
    template_name = 'recepcion/listar_tipodemerma.html'
    context_object_name = 'tipodemermas'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = TipoDeMerma.objects.filter(centro=centro).order_by('id')

                # Permitir búsqueda dentro de los tipos de merma del centro
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_query) |
                        Q(descripcion__icontains=search_query)
                    )
                return queryset
            else:
                return TipoDeMerma.objects.none()
        except ObjectDoesNotExist:
            return TipoDeMerma.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay tipos de merma asociados
        if not context['tipodemermas'].exists():
            context['mensaje'] = "No tiene tipos de merma asociados."

        return context
    
    
class TipoDeMermaCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "TipoMerma"
    model = TipoDeMerma
    form_class = TipoDeMermaForm
    template_name = 'recepcion/crear_tipodemerma.html'
    success_url = reverse_lazy('recepcion:TipoDeMermaList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            form.instance.centro = user_profile.centro
            messages.success(self.request, 'Tipo de merma creada correctamente.')
            return super().form_valid(form)  # solo guarda 1 vez
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)


    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
class TipoDeMermaUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "TipoMerma"
    model = TipoDeMerma
    template_name = 'recepcion/detalle_tipodemerma.html'
    form_class = TipoDeMermaForm
    success_url = reverse_lazy('recepcion:TipoDeMermaList')
    context_object_name = 'tipodemerma'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return TipoDeMerma.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return TipoDeMerma.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Tipo dee merma actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   
    

class TipoDeMermaDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "TipoMerma"
    model = TipoDeMerma
    template_name = 'recepcion/tipodemerma_confirm_delete.html'
    success_url = reverse_lazy('recepcion:TipoDeMermaList')
    context_object_name = 'tiposdemerma'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return TipoDeMerma.objects.filter(centro=user_profile.centro)
        else:
            return TipoDeMerma.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.save
        messages.success(self.request, 'Tipo de merma eliminado correctamente.')
        return super().delete(request, *args, **kwargs) 
    
    
    
######################################################################################
################################      MERMAS    ######################################
######################################################################################

class MermasList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Merma"
    model = Merma
    template_name = 'recepcion/listar_mermas.html'
    context_object_name = 'mermas'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = Merma.objects.filter(centro=centro).order_by('id')

                # Permitir búsqueda dentro de los tipos de merma del centro
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(alimento__icontains=search_query) |
                        Q(fecha__icontains=search_query) |
                        Q(tipo_merma__icontains=search_query)
                    )
                return queryset
            else:
                return Merma.objects.none()
        except ObjectDoesNotExist:
            return Merma.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay mermas asociados
        if not context['mermas'].exists():
            context['mensaje'] = "No tiene mermas asociados."

        return context
    
        
class MermasCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "Merma"
    model = Merma
    form_class = MermaForm
    template_name = 'recepcion/crear_mermas.html'
    success_url = reverse_lazy('recepcion:MermasList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            mermas = form.save(commit=False)
            mermas.centro = user_profile.centro
            mermas.registrado_por = user_profile
            mermas.save()
            messages.success(self.request, 'Merma creada correctamente.')
            return redirect(self.success_url)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)   
    
    
    
class MermasUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "Merma"
    model = Merma
    template_name = 'recepcion/detalle_merma.html'
    form_class = MermaForm
    success_url = reverse_lazy('recepcion:MermasList')
    context_object_name = 'merma'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Merma.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return Merma.objects.none()

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        form.instance.registrado_por = user_profile
        messages.success(self.request, 'Merma actualizada correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)   
    

class MermasDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "Merma"
    model = Merma
    template_name = 'recepcion/merma_confirm_delete.html'
    success_url = reverse_lazy('recepcion:MermasList')
    context_object_name = 'merma'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return Merma.objects.filter(centro=user_profile.centro)
        else:
            return Merma.objects.none()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.eliminar_y_devolver_stock()
        messages.success(request, f"Merma eliminada. {obj.cantidad} devuelta al stock.")
        return redirect(self.success_url)


    
class MermasDetailView(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "Merma"
    model = Merma
    template_name = 'recepcion/datos_merma.html'
    context_object_name = 'merma'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request)) 
        return context      
    
    
    
    
    
class AuditoriaList(PermisoMixin, PaginationMixin, LoginRequiredMixin, TemplateView):
    permiso_modulo = "Recepcion"
    template_name = 'recepcion/listar_auditoria.html'
    paginate_by = 10  # Número de registros por página

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request)) 
        user_profile = UserProfile.objects.filter(user=self.request.user).first()

        if user_profile and user_profile.centro:
            centro = user_profile.centro
            recepciones = Recepcion.objects.filter(centro=centro)
            mermas = Merma.objects.filter(centro=centro)

            movimientos = []

            # Normalizar Recepciones
            for r in recepciones:
                r.fecha_movimiento = r.fecha_recepcion
                r.tipo_movimiento = "Recepción"
                movimientos.append(r)

            # Normalizar Mermas
            for m in mermas:
                m.fecha_movimiento = m.fecha
                m.tipo_movimiento = "Merma"
                movimientos.append(m)

            # Ordenar por fecha descendente
            movimientos.sort(key=lambda x: x.fecha_movimiento, reverse=True)

            context['movimientos'] = movimientos
        else:
            context['movimientos'] = []

        return context