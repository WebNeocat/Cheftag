from django.shortcuts import render
from django.views.generic import ListView
from app.core.models import RegistroAccion
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django import forms
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView, DeleteView
from .mixins import PaginationMixin, PermisoMixin
from app.dashuser.views import datos_centro
from app.super.models import UserProfile
from app.super.forms import UserProfileForm



######################################################################################
###########################       REGISTROS LOG    ###################################
######################################################################################


class RegistroAccionListView(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "RegistroAccion"
    model = RegistroAccion
    template_name = "core/registro_accion_list.html"
    context_object_name = "registros"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "userprofile") and user.userprofile.centro:
            return RegistroAccion.objects.filter(
                centro=user.userprofile.centro
            ).order_by("-fecha")
        return RegistroAccion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # añadimos el contexto con los datos del centro
        context.update(datos_centro(self.request))
        return context


class RegistroAccionDetailView(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "RegistroAccion"
    model = RegistroAccion
    template_name = "core/registro_accion_detail.html"
    context_object_name = "registro"

    def get_queryset(self):
        """
        Filtra para que solo muestre registros del centro del usuario logueado.
        """
        user = self.request.user
        if hasattr(user, "userprofile") and user.userprofile.centro:
            return RegistroAccion.objects.filter(centro=user.userprofile.centro)
        return RegistroAccion.objects.none()
    
    
######################################################################################
############################        USUARIOS     #####################################
######################################################################################    
    
class UsersListView(PermisoMixin, PaginationMixin, LoginRequiredMixin, ListView):
    permiso_modulo = "UserProfile"
    model = UserProfile
    template_name = 'core/lista_usuarios.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        # Filtramos por el centro del usuario logueado
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return UserProfile.objects.filter(centro=user_profile.centro)
        return UserProfile.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(datos_centro(self.request))  # pasa el centro como contexto
        return context    
 
    
class UserCreateView(PermisoMixin, LoginRequiredMixin, CreateView):
    permiso_modulo = "UserProfile"
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'core/crear_usuario.html'
    success_url = reverse_lazy('core:UsersListView')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        creator_profile = get_object_or_404(UserProfile, user=self.request.user)

        if creator_profile.centro:
            # Ocultar el campo centro y dejarlo solo de lectura
            form.fields['centro'].widget = forms.HiddenInput()
            form.initial['centro'] = creator_profile.centro
        # Si no tiene centro → dejamos el campo visible para que lo seleccione
        return form

    def form_valid(self, form):
        profile = form.save(commit=False)

        # Asignar centro automáticamente si el creador tiene uno
        creator_profile = get_object_or_404(UserProfile, user=self.request.user)
        if creator_profile.centro:
            profile.centro = creator_profile.centro

        # Crear usuario Django asociado
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['nombre'],
            last_name=form.cleaned_data['apellidos'],
            is_active=profile.estado
        )
        profile.user = user
        profile.save()

        messages.success(self.request, "Usuario creado correctamente.")
        return super().form_valid(form)

    
    
        
class UsersUpdateView(PermisoMixin, LoginRequiredMixin, UpdateView):
    permiso_modulo = "UserProfile"
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'core/editar_usuario.html'
    success_url = reverse_lazy('core:UsersListView')
    context_object_name = 'usuario'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # ⚡ Hacemos que el campo centro no se pueda editar
        if 'centro' in form.fields:
            form.fields['centro'].disabled = True  

        return form

    def form_valid(self, form):
        # Evitar que alguien modifique centro via POST
        if 'centro' in form.changed_data:
            form.instance.centro = self.get_object().centro
        return super().form_valid(form)
    


class UserDeleteView(PermisoMixin, LoginRequiredMixin, DeleteView):
    permiso_modulo = "UserProfile"
    model = UserProfile
    template_name = 'core/confirm_delete_usuario.html'
    success_url = reverse_lazy('core:UsersListView')
    context_object_name = 'usuario'

    def dispatch(self, request, *args, **kwargs):
        """Evitar que un usuario se elimine a sí mismo"""
        self.object = self.get_object()
        if self.object.user == request.user:
            messages.error(request, "No puedes eliminar tu propio usuario.")
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Eliminar UserProfile y User asociado"""
        self.object = self.get_object()
        user_to_delete = self.object.user

        messages.success(request, f"Usuario {user_to_delete.username} eliminado correctamente.")
        
        self.object.delete()  # elimina el UserProfile
        user_to_delete.delete()  # elimina el User

        return redirect(self.success_url)    
    
    

class UserDetailView(PermisoMixin, LoginRequiredMixin, DetailView):
    permiso_modulo = "UserProfile"
    model = UserProfile
    template_name = 'core/detalle_usuario.html'
    context_object_name = 'usuario'

    def get_queryset(self):
        # Filtramos solo por el centro del usuario logueado
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        if user_profile.centro:
            return UserProfile.objects.filter(centro=user_profile.centro)
        return UserProfile.objects.none()   
    
    
######################################################################################
#################################    PERMISOS    #####################################
######################################################################################    
  