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
from .models import Proveedor, Recepcion, TipoDeMerma, Merma, AjusteInventario
from .forms import ProveedorForm, RecepcionForm, TipoDeMermaForm, MermaForm, RecepcionFormSet, RecepcionEliminarForm, AjusteStockForm
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
    

class RecepcionManualCreate(LoginRequiredMixin, View):
    model = Recepcion
    template_name = 'recepcion/crear_recepcion_manual.html'
    success_url = 'recepcion:RecepcionManualList'

    def get(self, request, *args, **kwargs):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        formset = RecepcionFormSet(
            queryset=Recepcion.objects.none(),
            form_kwargs={"centro": user_profile.centro}
        )
        return render(request, self.template_name, {'formset': formset})

    def post(self, request, *args, **kwargs):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        formset = RecepcionFormSet(
            request.POST,
            queryset=Recepcion.objects.none(),
            form_kwargs={"centro": user_profile.centro}
        )

        if not user_profile.centro:
            messages.error(request, 'No estás asociado a ningún centro.')
            return redirect('dashboard')  # o alguna URL de tu elección

        if formset.is_valid():
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    recepcion = form.save(commit=False)
                    recepcion.centro = user_profile.centro
                    recepcion.save()

                    try:
                        # Actualiza stock, stock_util y precio_medio
                        recepcion.actualizar_stock_alimento()
                    except ValueError as e:
                        form.add_error(None, str(e))
                        return render(request, self.template_name, {'formset': formset})

            messages.success(request, 'Recepciones registradas correctamente.')
            return redirect(self.success_url)
        else:
            # Mostrar errores del formset
            print("Formset errors:", formset.errors)
            print("Non form errors:", formset.non_form_errors())
            messages.error(request, 'Error al guardar las recepciones.')
            return render(request, self.template_name, {'formset': formset})


    
    
class RecepcionManualUpdate(LoginRequiredMixin, UpdateView):
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

    def get_form_kwargs(self):
        """Pasar user al formulario para filtrar queryset de alimentos."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if not user_profile.centro:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)
        
        merma = form.save(commit=False)
        merma.centro = user_profile.centro
        merma.registrado_por = user_profile
        merma.save()
        messages.success(self.request, 'Merma creada correctamente.')
        return redirect(self.success_url)

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


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # pasamos el usuario al formulario
        return kwargs
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
            ajustes = AjusteInventario.objects.filter(centro=centro)

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

            # Normalizar Ajustes
            for a in ajustes:
                a.fecha_movimiento = a.fecha
                a.tipo_movimiento = "Ajuste de Inventario"
                # Para que el template funcione
                a.cantidad = a.diferencia  # o a.stock_real si prefieres
                a.proveedor = None  # así entra en el bloque de ajustes, no en Recepción
                movimientos.append(a)

            # Ordenar por fecha descendente
            movimientos.sort(key=lambda x: x.fecha_movimiento, reverse=True)

            context['movimientos'] = movimientos
        else:
            context['movimientos'] = []

        return context

    
    
######################################################################################
#############################  AJUSTE INVENTARIO  ####################################
######################################################################################

 
class AjusteInventarioList(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "AjusteInventario"
    model = AjusteInventario
    template_name = 'recepcion/listar_ajuste.html'
    context_object_name = 'ajustes'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                queryset = AjusteInventario.objects.filter(centro=centro).order_by('id')


                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(alimento__icontains=search_query) 
                    )
                return queryset
            else:
                return AjusteInventario.objects.none()
        except ObjectDoesNotExist:
            return AjusteInventario.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        # Añadir un mensaje si no hay ajustes en inventario asociados
        if not context['ajustes'].exists():
            context['mensaje'] = "No tiene ajustes en el inventario asociados."

        return context
    
    
 
class AjusteInventarioCreate(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "AjusteInventario"
    model = AjusteInventario
    form_class = AjusteStockForm
    template_name = 'recepcion/crear_ajuste.html'
    success_url = reverse_lazy('recepcion:AjusteInventarioList')

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if not user_profile.centro:
            messages.error(self.request, "No estás asociado a ningún centro.")
            return self.form_invalid(form)

        # Guardamos el ajuste normalmente
        ajuste = form.save(commit=False)
        ajuste.centro = user_profile.centro
        ajuste.stock_sistema = ajuste.alimento.stock_actual
        ajuste.diferencia = ajuste.stock_real - ajuste.stock_sistema
        ajuste.save()  # Se dispara el signal aquí una sola vez

        # 🔹 Actualizamos el stock del alimento sin tocar AjusteInventario
        Alimento.objects.filter(pk=ajuste.alimento.pk).update(stock_actual=ajuste.stock_real)

        messages.success(self.request, "Ajuste de inventario creado correctamente.")
        return redirect(self.success_url)




     
class AjusteInventarioUpdate(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "AjusteInventario"
    model = AjusteInventario
    template_name = 'recepcion/detalle_ajuste.html'
    form_class = AjusteStockForm
    success_url = reverse_lazy('recepcion:AjusteInventarioList')
    context_object_name = 'ajuste'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return AjusteInventario.objects.filter(centro_id=user_profile.centro_id)
        else:
            messages.error(self.request, 'No estás asociado a ningún centro.')
            return AjusteInventario.objects.none()

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # No permitir cambiar el alimento en un ajuste existente
        form.fields['alimento'].disabled = True
        return form

    def form_valid(self, form):
        ajuste = form.save(commit=False)

        # Calculamos la diferencia actualizada
        ajuste.diferencia = ajuste.stock_real - ajuste.stock_sistema

        # 🔹 Actualizamos solo el stock del alimento sin volver a tocar AjusteInventario
        Alimento.objects.filter(pk=ajuste.alimento.pk).update(stock_actual=ajuste.stock_real)

        # Guardamos el ajuste actualizado
        ajuste.save()

        messages.success(self.request, 'Ajuste de inventario actualizado correctamente.')
        return redirect(self.success_url)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)



    
    
class AjusteInventarioDelete(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "AjusteInventario"
    model = AjusteInventario
    template_name = 'recepcion/ajuste_confirm_delete.html'
    success_url = reverse_lazy('recepcion:AjusteInventarioList')
    context_object_name = 'ajuste'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return AjusteInventario.objects.filter(centro=user_profile.centro)
        else:
            return AjusteInventario.objects.none()

    def post(self, request, *args, **kwargs):
        ajuste = self.get_object()
        alimento = ajuste.alimento

        # 🔹 Revertir el efecto del ajuste antes de eliminarlo
        alimento.actualizar_stock(-ajuste.diferencia)

        messages.success(self.request, 'Ajuste de inventario eliminado y stock revertido correctamente.')
        return super().post(request, *args, **kwargs)    
