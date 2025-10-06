from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate
from django.db.models import Q
from datetime import date
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.core.mixins import PaginationMixin, PermisoMixin
from .models import Pedido, PedidoDetalle
from .forms import PedidoDetalleForm, PedidoForm, ConfirmPasswordForm
from app.dashuser.views import datos_centro
from app.super.models import UserProfile
from app.recepcion.models import Proveedor
import openpyxl


######################################################################################
###############################    PEDIDOS    ########################################
######################################################################################    


class CreatePedidoView(LoginRequiredMixin, CreateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'pedidos/pedido_form.html'
    success_url = reverse_lazy('pedidos:listado_pedidos')

    def get_form_kwargs(self):
        """Pasa el usuario al formulario para filtrar proveedores"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset_prefix = 'detalle'

        PedidoDetalleFormSet = inlineformset_factory(
            Pedido,
            PedidoDetalle,
            form=PedidoDetalleForm,
            fields=['alimento', 'utensilio', 'cantidad', 'unidad', 'precio_unitario'],
            extra=1,
            can_delete=True
        )

        if self.request.POST:
            context['formset'] = PedidoDetalleFormSet(
                self.request.POST,
                form_kwargs={'user': self.request.user},
                prefix=formset_prefix
            )
        else:
            context['formset'] = PedidoDetalleFormSet(
                form_kwargs={'user': self.request.user},
                prefix=formset_prefix
            )

        context['formset_prefix'] = formset_prefix
        context.update(datos_centro(self.request))
        return context

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)

        if not user_profile.centro:
            messages.error(self.request, 'No está asociado a ningún centro.')
            return self.form_invalid(form)

        formset_prefix = 'detalle'
        PedidoDetalleFormSet = inlineformset_factory(
            Pedido,
            PedidoDetalle,
            form=PedidoDetalleForm,
            fields=['alimento', 'utensilio', 'cantidad', 'unidad', 'precio_unitario'],
            extra=1,
            can_delete=True
        )

        formset = PedidoDetalleFormSet(
            self.request.POST,
            form_kwargs={'user': self.request.user},
            prefix=formset_prefix
        )

        if formset.is_valid():
            pedido = form.save(commit=False)
            pedido.centro = user_profile.centro
            pedido.creado_por = self.request.user
            pedido.save()
            formset.instance = pedido
            formset.save()

            messages.success(self.request, 'Pedido creado correctamente.')
            return redirect('pedidos:listado_pedidos')
        else:
            messages.error(self.request, 'Revise los errores en los detalles del pedido.')
            context = self.get_context_data()
            context['formset'] = formset
            return self.render_to_response(context)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
    
class ListPedidoView(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "Pedido"
    model = Pedido
    template_name = 'pedidos/pedido_list.html'
    context_object_name = 'pedidos'
    paginate_by = 10

    def get_queryset(self):
        try:
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                
                # Orden personalizado usando expresión Case
                from django.db.models import Case, When, Value
                from django.db.models.fields import IntegerField
                
                queryset = Pedido.objects.filter(centro=centro).order_by(
                    Case(
                        When(estado='pendiente', then=Value(0)),
                        When(estado='encamino', then=Value(1)),
                        When(estado='parcial', then=Value(2)),
                        When(estado='recibido', then=Value(3)),
                        When(estado='cancelado', then=Value(4)),
                        default=Value(5),
                        output_field=IntegerField()
                    ),
                    '-fecha_entrega'  # Orden descendente por fecha
                )

                # Resto de la lógica (búsqueda y ordenamiento adicional)
                search_query = self.request.GET.get('buscar')
                if search_query:
                    queryset = queryset.filter(
                        Q(proveedor__nombre__icontains=search_query) |
                        Q(observaciones__icontains=search_query)
                    )

                ordering = self.request.GET.get('ordenar')
                if ordering == 'fecha':
                    queryset = queryset.order_by('fecha_entrega')
                elif ordering == 'proveedor':
                    queryset = queryset.order_by('proveedor__nombre')

                return queryset
            else:
                return Pedido.objects.none()
        except ObjectDoesNotExist:
            return Pedido.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))

        if not context['pedidos'].exists():
            context['mensaje'] = "No tiene pedidos registrados."
        
        # Añadir información sobre el orden actual
        context['orden_actual'] = self.request.GET.get('ordenar', 'estado')
        return context
    

class ListPedidoPorProveedorView(PaginationMixin, LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedidos/pedidoproveedor_list.html'
    context_object_name = 'pedidos'
    paginate_by = 10

    def get_queryset(self):
        try:
            proveedor_id = self.kwargs['pk']
            user_profile = UserProfile.objects.filter(user=self.request.user).first()
            if user_profile and user_profile.centro:
                centro = user_profile.centro
                return Pedido.objects.filter(centro=centro, proveedor__id=proveedor_id).order_by('-fecha_entrega')
            else:
                return Pedido.objects.none()
        except ObjectDoesNotExist:
            return Pedido.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))
        context['proveedor'] = Proveedor.objects.get(pk=self.kwargs['pk'])
        if not context['pedidos'].exists():
            context['mensaje'] = "No hay pedidos para este proveedor."
        return context
        
class DetailPedidoView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'pedidos/pedido_detail.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile and user_profile.centro:
            return Pedido.objects.filter(centro=user_profile.centro)
        return Pedido.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))
        context['detalles'] = self.object.detalles.all()
        context['total'] = sum(item.total_linea() for item in context['detalles'])
        return context    
    
    
    
class DeletePedidoView(LoginRequiredMixin, DeleteView):
    model = Pedido
    template_name = 'pedidos/pedido_confirm_delete.html'
    success_url = reverse_lazy('pedidos:listado_pedidos')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form', ConfirmPasswordForm())
        context['form'] = form
        context.update(datos_centro(self.request))
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ConfirmPasswordForm()
        return render(request, self.template_name, {
            'object': self.object,
            'form': form
        })

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ConfirmPasswordForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data['password']
            user = authenticate(username=request.user.username, password=password)

            if user is not None:
                self.object.delete()
                messages.success(request, "Pedido eliminado correctamente.")
                return redirect(self.success_url)
            else:
                messages.error(request, "Contraseña incorrecta.")

        return render(request, self.template_name, {
            'object': self.object,
            'form': form
        })    


class UpdatePedidoView(LoginRequiredMixin, UpdateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'pedidos/pedido_form.html'
    success_url = reverse_lazy('pedidos:listado_pedidos')

    def get_form_kwargs(self):
        """Pasa el usuario al formulario para filtrar proveedores"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        PedidoDetalleFormSet = inlineformset_factory(
            Pedido,
            PedidoDetalle,
            form=PedidoDetalleForm,
            fields=['alimento', 'cantidad', 'unidad', 'precio_unitario'],
            extra=1,
            can_delete=True
        )
        
        if self.request.POST:
            context['formset'] = PedidoDetalleFormSet(
                self.request.POST, 
                instance=self.object, 
                form_kwargs={'user': self.request.user}
            )
        else:
            context['formset'] = PedidoDetalleFormSet(
                instance=self.object, 
                form_kwargs={'user': self.request.user}
            )
        
        context.update(datos_centro(self.request))
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        old_estado = self.get_object().estado

        if formset.is_valid():
            pedido = form.save(commit=False)
            nuevo_estado = form.cleaned_data.get('estado')

            if nuevo_estado == 'recibido' and old_estado != 'recibido':
                pedido.fecha_entrega = date.today()

            pedido.save()
            formset.instance = pedido
            formset.save()

            messages.success(self.request, 'Pedido actualizado correctamente.')
            return redirect(self.success_url)
        else:
            messages.error(self.request, 'Revise los errores en los detalles del pedido.')
            return self.render_to_response(context)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)
    
    
######################################################################################
###########################   EXPORTAR PEDIDOS    ####################################
######################################################################################  
 
    
def exportar_pedido_pdf(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    html_string = render_to_string('pedidos/pedido_pdf.html', {'pedido': pedido})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=pedido_{pedido.id}.pdf'

    HTML(string=html_string).write_pdf(response)
    return response    



def exportar_pedido_excel(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f'Pedido #{pedido.id}'

    ws.append(['Producto', 'Cantidad', 'Unidad', 'Precio Unitario', 'Total Línea'])

    for d in pedido.detalles.all():
        producto = d.alimento.nombre if d.alimento else d.utensilio.nombre
        ws.append([
            producto,
            float(d.cantidad),
            str(d.unidad),
            float(d.precio_unitario),
            float(d.total_linea())
        ])

    ws.append([])
    ws.append(['', '', '', 'Total Pedido:', float(pedido.total_pedido())])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=pedido_{pedido.id}.xlsx'
    wb.save(response)
    return response    