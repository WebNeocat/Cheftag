from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from django.utils.timezone import localtime
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from .forms import UserProfileForm, CentroForm
from .models import UserProfile, Centros
from app.core.mixins import PaginationMixin


@login_required
def home(request):
    return render(request, 'super/home.html')

def datos_super(request):
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


class UsuariosList (PaginationMixin, ListView):
    model = UserProfile
    template_name = 'super/listar_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 8  # Número de registros por página
    
    def get_queryset(self):
        queryset = UserProfile.objects.all().order_by('id')
        search_query = self.request.GET.get('buscar')
        if search_query:
            queryset = queryset.filter(
                Q(nombre__icontains=search_query) |
                Q(apellidos__icontains=search_query) |
                Q(cargo__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        usuarios = self.get_queryset()
        paginator = Paginator(usuarios, self.paginate_by)

        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context
    
    
class CrearUsuarioView(CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'super/crear_usuario.html'
    success_url = reverse_lazy('super:UsuariosList')

    @transaction.atomic
    def form_valid(self, form):
        # Extraer datos
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        nombre = form.cleaned_data['nombre']
        apellidos = form.cleaned_data['apellidos']

        # Crear el User de Django
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nombre,
            last_name=apellidos
        )

        # Asignar user al perfil antes de guardar
        profile = form.save(commit=False)
        profile.user = user
        profile.password = password  # ⚠ Guarda el password plano si quieres mostrarlo, pero no es seguro
        profile.save()

        messages.success(self.request, "Usuario y perfil creados correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al crear el usuario. Revisa los datos.")
        return super().form_invalid(form)


class CentrosList(PaginationMixin, ListView):
    model = Centros
    template_name = 'super/listar_centros.html'
    context_object_name = 'centros'
    paginate_by = 8  # Número de registros por página
    
    def get_queryset(self):
        queryset = Centros.objects.all().order_by('id')
        search_query = self.request.GET.get('buscar')
        if search_query:
            queryset = queryset.filter(
                Q(nombre__icontains=search_query) |
                Q(direccion__icontains=search_query) |
                Q(ciudad__icontains=search_query) |
                Q(codigo_postal__icontains=search_query) |
                Q(pais__icontains=search_query) |
                Q(telefono__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(sitio_web__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        centros = self.get_queryset()
        paginator = Paginator(centros, self.paginate_by)

        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context
    
    
class CentroCreate(CreateView):
    model = Centros
    form_class = CentroForm
    template_name = 'super/crear_centro.html' 
    success_url = reverse_lazy('super:CentrosList')
    
    def form_valid(self, form):
        # Guardar el formulario y obtener el objeto actualizado
        self.object = form.save()
        messages.success(self.request, 'Centro creado correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el centro. Por favor, revisa los datos.')
        return super().form_invalid(form)# Create your views here.
