from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.utils.timezone import localtime
from django.db.models import Q
from django.conf import settings
from django.core.files import File
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, TemplateView
from .forms import CentroForm, CentroUpdateForm
from .models import UserProfile, Centros, Permiso
from app.core.mixins import PaginationMixin
from app.dashuser.models import Alergenos, Trazas, UnidadDeMedida, TipoAlimento, Alimento, InformacionNutricional
from app.platos.models import TextoModo, TipoPlato
from app.recepcion.models import TipoDeMerma
import re
import unicodedata
import logging
import pandas as pd
import os




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


def dashboard(request):
    total_centros = Centros.objects.count()
    centros_activos = Centros.objects.filter(estado=True).count()
    total_usuarios = UserProfile.objects.count()
    usuarios_activos = UserProfile.objects.filter(estado=True).count()

    # Últimos registros para mostrarlos debajo
    ultimos_centros = Centros.objects.order_by('-id')[:5]
    ultimos_usuarios = UserProfile.objects.order_by('-id')[:5]

    context = {
        'total_centros': total_centros,
        'centros_activos': centros_activos,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'ultimos_centros': ultimos_centros,
        'ultimos_usuarios': ultimos_usuarios,
    }
    return render(request, 'super/dashboard.html', context)

######################################################################################
#############################   USUARISOS SUPER    ###################################
######################################################################################


class UserList(LoginRequiredMixin, PaginationMixin, ListView):
    model = UserProfile
    template_name = 'super/user_list_super.html' 
    context_object_name = 'users'
    paginate_by = 8 
    
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
        
        users = self.get_queryset()
        paginator = Paginator(users, self.paginate_by)

        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context
    
    

class UserCreate(LoginRequiredMixin, CreateView):
    model = UserProfile
    fields = ['centro', 'username', 'password', 'nombre', 'apellidos', 'cargo', 'imagen', 'estado']
    template_name = 'super/user_crear_super.html'
    success_url = reverse_lazy('super:UserList')

    def form_valid(self, form):
        # Creamos el usuario de Django
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['nombre'],
            last_name=form.cleaned_data['apellidos']
        )
        # Asociamos el user al perfil
        form.instance.user = user
        return super().form_valid(form)



class UserUpdate(UpdateView):
    model = UserProfile
    context_object_name = 'user' 
    fields = ['centro', 'username', 'password', 'nombre', 'apellidos', 'cargo', 'imagen', 'estado']
    template_name = 'super/user_form_super.html'
    success_url = reverse_lazy('super:UserList')

    @transaction.atomic
    def form_valid(self, form):
        """
        Actualiza tanto el UserProfile como el User relacionado.
        """
        profile = form.save(commit=False)
        # Actualizamos también el user de Django asociado
        user = profile.user
        user.username = form.cleaned_data['username']
        user.first_name = form.cleaned_data['nombre']
        user.last_name = form.cleaned_data['apellidos']

        # Si se ha modificado la contraseña
        if form.cleaned_data['password']:
            user.set_password(form.cleaned_data['password'])
            profile.password = form.cleaned_data['password']  

        user.save()
        profile.save()

        messages.success(self.request, "Usuario y perfil actualizados correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar el usuario. Revisa los datos.")
        return super().form_invalid(form)



class UserDelete(LoginRequiredMixin, DeleteView):
    model = UserProfile
    template_name = 'super/user_confirm_delete.html'
    success_url = reverse_lazy('super:UserList')
    context_object_name = 'user'

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        usuario = self.get_object()
        user = usuario.user  

        # Eliminamos primero el perfil
        response = super().delete(request, *args, **kwargs)

        # Luego eliminamos el user de Django
        if user:
            user.delete()

        messages.success(request, "Usuario y perfil eliminados correctamente.")
        return response
    
        
######################################################################################
###############################     CENTROS    #######################################
######################################################################################



class CentrosList(PaginationMixin, ListView):
    model = Centros
    template_name = 'super/listar_centros.html'
    context_object_name = 'centros'
    paginate_by = 10  # Número de registros por página
    
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


logger = logging.getLogger(__name__)

class CentroUpdate(UpdateView):
    model = Centros
    form_class = CentroUpdateForm
    template_name = 'super/editar_centro.html'
    context_object_name = 'centro'
    pk_url_kwarg = 'pk'

    def get_success_url(self):
        return reverse_lazy('super:CentrosList')

    def form_valid(self, form):
        # guarda explícitamente y loggea
        self.object = form.save()
        logger.debug("form_valid called. cleaned_data: %s", form.cleaned_data)
        messages.success(self.request, 'Centro actualizado correctamente.')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        # ver errores en log
        logger.debug("form_invalid called. errors: %s", form.errors.as_json())
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en el campo '{field}': {error}")
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        # Forzamos self.object para que esté disponible en get_context_data
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
        
class CentroDetail(DetailView):
    model = Centros
    template_name = 'super/detalle_centro.html'
    context_object_name = 'centro'
    pk_url_kwarg = 'pk'  # se usa <int:pk> en la URL        
    
    
class CentroDelete(DeleteView):
    model = Centros
    template_name = 'super/confirmar_delete_centro.html'
    context_object_name = 'centro'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('super:CentrosList')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Centro "{self.object.nombre}" eliminado correctamente.')
        return super().delete(request, *args, **kwargs)    
    
    
    
class UsuariosCentroListView(PaginationMixin,ListView):
    model = UserProfile
    template_name = 'super/usuarios_centro.html'
    context_object_name = 'usuarios'
    paginate_by = 10  # Número de registros por página

    def get_queryset(self):
        # obtener pk del centro desde la URL
        centro_id = self.kwargs.get('pk')
        return UserProfile.objects.filter(centro_id=centro_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        centro_id = self.kwargs.get('pk')
        context['centro'] = Centros.objects.get(pk=centro_id)

    
######################################################################################
###############################     PERMISOS    ######################################
######################################################################################

    
    
# Definimos los módulos y acciones
MODULOS = ["Proveedor", "Alimento", "Plato",  "Alergenos", "Trazas", "UnidadDeMedida", "TipoAlimento", "localizacion", 'UserProfile', 'Utensilio', 'AjusteInventario',
           "Conservacion", "TipoPlato", "TextoModo","TipoMerma", "Salsa", "Receta", "Recepcion", "Merma", "EtiquetaPlato", "RegistroAccion", 'Pedido']
ACCIONES = ["create", "read", "update", "delete"]


class UserPermisosView(UserPassesTestMixin, TemplateView):
    permiso_modulo = "UserProfile"
    template_name = "super/user_permisos.html"

    def test_func(self):
        # Solo superuser puede acceder
        return self.request.user.is_superuser

    def get_userprofile(self):
        # Obtenemos el UserProfile del usuario seleccionado
        return get_object_or_404(UserProfile, pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.get_userprofile()

        permisos_dict = {}
        for modulo in MODULOS:
            permisos_dict[modulo] = {}
            for accion in ACCIONES:
                existe = Permiso.objects.filter(
                    usuario=user_profile,
                    modulo=modulo,
                    accion=accion
                ).exists()
                permisos_dict[modulo][accion] = existe

        context["user_profile"] = user_profile
        context["modulos"] = MODULOS
        context["acciones"] = ACCIONES
        context["permisos_dict"] = permisos_dict
        return context

    def post(self, request, *args, **kwargs):
        user_profile = self.get_userprofile()
        for modulo in MODULOS:
            for accion in ACCIONES:
                campo = f"{modulo}_{accion}"
                checked = request.POST.get(campo) == "on"

                permiso, created = Permiso.objects.get_or_create(
                    usuario=user_profile,
                    modulo=modulo,
                    accion=accion
                )
                if checked:
                    permiso.save()
                else:
                    permiso.delete()

        messages.success(request, f"Permisos actualizados para {user_profile}")
        return redirect(
            reverse_lazy("super:UserList")
        )
   
   
   
   
   
######################################################################################
##########################   IMPORTAR BASES DE DATOS    ##############################
######################################################################################

class ImportadorBaseCentro:
    """
    Clase genérica para importar datos en modelos basados en centros.
    Compatible con CSV y Excel.
    """

    def __init__(self, centro, modelo, mapa_campos=None):
        self.centro = centro
        self.modelo = modelo
        self.mapa_campos = mapa_campos or {}

    def importar_archivo(self, archivo):
        extension = archivo.name.split('.')[-1].lower()

        # Leer archivo
        if extension == 'csv':
            df = pd.read_csv(archivo)
        elif extension in ['xls', 'xlsx']:
            df = pd.read_excel(archivo)
        else:
            raise ValueError("Formato no soportado. Usa CSV o Excel.")

        # Normalizar nombres de columnas (quitar espacios)
        df.columns = [str(c).strip() for c in df.columns]

        # Validar columnas requeridas
        columnas_requeridas = ['Nombre'] + list(self.mapa_campos.keys()) + ['Estado', 'Activo']
        faltantes = [c for c in columnas_requeridas if c not in df.columns and c in ['Nombre'] + list(self.mapa_campos.keys())]
        if faltantes:
            raise ValueError(f"El archivo no contiene las columnas necesarias: {faltantes}")

        self._importar_dataframe(df)

    @transaction.atomic
    def _importar_dataframe(self, df):
        total_creados = 0
        total_actualizados = 0
        errores = 0

        for _, fila in df.iterrows():
            nombre = fila.get('Nombre')
            if not nombre:
                continue

            # Detectar campo booleano
            campo_booleano = 'estado' if 'estado' in [f.name for f in self.modelo._meta.fields] else 'activo'

            # Obtener valor booleano desde CSV
            valor_texto = None
            if 'Estado' in df.columns:
                valor_texto = fila.get('Estado')
            elif 'Activo' in df.columns:
                valor_texto = fila.get('Activo')

            valor_bool = True  # Por defecto activo
            if valor_texto is not None:
                valor_str = str(valor_texto).strip().lower()
                if valor_str in ['sí', 'si', 's', 'true', '1']:
                    valor_bool = True
                elif valor_str in ['no', 'n', 'false', '0']:
                    valor_bool = False

            defaults = {campo_booleano: valor_bool}

            # Mapear columnas adicionales
            for col_csv, campo_modelo in self.mapa_campos.items():
                if col_csv in fila:
                    defaults[campo_modelo] = fila.get(col_csv)

            # Filtro para update_or_create
            filtro = {'nombre': nombre}
            if hasattr(self.modelo, 'centro'):
                filtro['centro'] = self.centro

            try:
                _, creado = self.modelo.objects.update_or_create(defaults=defaults, **filtro)
                if creado:
                    total_creados += 1
                else:
                    total_actualizados += 1
            except IntegrityError:
                errores += 1
                print(f"❌ Conflicto con registro existente: {nombre}")

        print(f"✅ {self.modelo.__name__} - Creados: {total_creados}, Actualizados: {total_actualizados}, Errores: {errores}")

            
                   
def importar_datos(request):
    modelos_map = {
        'Alergenos': Alergenos,
        'Trazas': Trazas,
        'UnidadDeMedida': UnidadDeMedida,
        'TipoAlimento': TipoAlimento,
        'TipoPlato': TipoPlato,
        'TipoDeMerma': TipoDeMerma,
        'TextoModo': TextoModo,
    }

    mapas_campos = {
        'Alergenos': {'Código': 'codigo', 'Imagen': 'imagen'},
        'Trazas': {'Código': 'codigo', 'Imagen': 'imagen'},
        'UnidadDeMedida': {'Abreviatura': 'abreviatura'},
        'TipoAlimento': {},
        'TipoPlato': {},
        'TipoDeMerma': {'Descripción': 'descripcion'},
        'TextoModo': {'Texto': 'texto'},
    }

    if request.method == 'POST':
        modelo_str = request.POST.get('modelo')
        centro_id = request.POST.get('centro')
        archivo = request.FILES.get('archivo')

        if not modelo_str or not centro_id or not archivo:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('super:importar_datos')

        modelo = modelos_map.get(modelo_str)
        if not modelo:
            messages.error(request, "Modelo no válido.")
            return redirect('super:importar_datos')

        centro = get_object_or_404(Centros, id=centro_id)
        mapa_campos = mapas_campos.get(modelo_str, {})

        try:
            importador = ImportadorBaseCentro(centro, modelo, mapa_campos)
            importador.importar_archivo(archivo)
            messages.success(request, f"Importación completada para {modelo_str}.")
        except Exception as e:
            messages.error(request, f"Error al importar: {str(e)}")

        return redirect('super:importar_datos')

    centros = Centros.objects.all()
    modelos = list(modelos_map.keys())

    return render(request, 'super/importar_datos.html', {
        'centros': centros,
        'modelos': modelos
    })



class ImportadorAlimentos:
    """
    Importador para Alimento + InformacionNutricional + Alergenos + Trazas
    Usa columna 'Imagen' en el Excel/CSV con ruta relativa desde MEDIA_ROOT
    """

    def __init__(self, centro, usuario=None):
        self.centro = centro
        self.usuario = usuario

    def importar_archivo(self, archivo):
        ext = archivo.name.split('.')[-1].lower()
        if ext == 'csv':
            df = pd.read_csv(archivo)
        elif ext in ('xls', 'xlsx'):
            df = pd.read_excel(archivo)
        else:
            raise ValueError("Formato no soportado. Usa CSV o Excel (.xls/.xlsx).")

        # Normalizar encabezados
        df.columns = [str(c).strip() for c in df.columns]

        return self._procesar_dataframe(df)

    def _procesar_dataframe(self, df):
        columnas_alergenos = [
            c for c in df.columns if Alergenos.objects.filter(nombre__iexact=c, centro=self.centro).exists()
        ]
        columnas_trazas = [
            c for c in df.columns if Trazas.objects.filter(nombre__iexact=c, centro=self.centro).exists()
        ]

        total_creados = total_actualizados = errores = 0
        imagenes_no_encontradas = []

        for _, fila in df.iterrows():
            nombre = fila.get('Nombre')
            tipo_raw = fila.get('Tipo')
            ruta_imagen_rel = fila.get('Imagen')

            if not nombre:
                continue

            try:
                with transaction.atomic():
                    # Buscar tipo de alimento
                    tipo_obj = None
                    if tipo_raw:
                        tipo_obj = TipoAlimento.objects.filter(
                            nombre__iexact=str(tipo_raw).strip(), centro=self.centro
                        ).first()

                    # Crear/actualizar Alimento
                    filtro = {'nombre': nombre, 'centro': self.centro}
                    defaults = {'tipo_alimento': tipo_obj}
                    alimento_obj, creado = Alimento.objects.update_or_create(defaults=defaults, **filtro)

                    if creado:
                        total_creados += 1
                    else:
                        total_actualizados += 1

                    # Asignar imagen si existe la ruta
                    if ruta_imagen_rel:
                        ruta_absoluta = os.path.join(settings.MEDIA_ROOT, ruta_imagen_rel)
                        if os.path.exists(ruta_absoluta):
                            with open(ruta_absoluta, 'rb') as f:
                                alimento_obj.imagen.save(os.path.basename(ruta_absoluta), File(f), save=True)
                            print(f"🖼️ Imagen asignada a {nombre}: {ruta_imagen_rel}")
                        else:
                            imagenes_no_encontradas.append(ruta_imagen_rel)
                            print(f"⚠️ Imagen no encontrada: {ruta_imagen_rel}")

                    # Información Nutricional
                    info_defaults = {
                        'energia': fila.get('Energía (kcal)', 0) or 0,
                        'hidratosdecarbono': fila.get('Hidratos (g)', 0) or 0,
                        'azucares': fila.get('Azúcares (g)', 0) or 0,
                        'proteinas': fila.get('Proteínas (g)', 0) or 0,
                        'grasas_totales': fila.get('Grasas (g)', 0) or 0,
                        'grasas_saturadas': fila.get('Grasas Saturadas (g)', 0) or 0,
                        'sal': fila.get('Sal (g)', 0) or 0,
                    }
                    InformacionNutricional.objects.update_or_create(alimento=alimento_obj, defaults=info_defaults)

                    # Alergenos
                    alimento_obj.alergenos.clear()
                    for col in columnas_alergenos:
                        valor = str(fila.get(col, 'No')).strip().lower()
                        if valor in ('sí', 'si', 's', 'true', '1'):
                            alergeno = Alergenos.objects.get(nombre__iexact=col, centro=self.centro)
                            alimento_obj.alergenos.add(alergeno)

                    # Trazas
                    alimento_obj.trazas.clear()
                    for col in columnas_trazas:
                        valor = str(fila.get(col, 'No')).strip().lower()
                        if valor == 'posible':
                            traza = Trazas.objects.get(nombre__iexact=col, centro=self.centro)
                            alimento_obj.trazas.add(traza)

            except Exception as e:
                errores += 1
                print(f"❌ Error al procesar {nombre}: {e}")

        print(f"✅ Alimentos - Creados: {total_creados}, Actualizados: {total_actualizados}, Errores: {errores}")
        if imagenes_no_encontradas:
            print(f"⚠️ {len(imagenes_no_encontradas)} imágenes no encontradas")

        return {
            'creados': total_creados,
            'actualizados': total_actualizados,
            'errores': errores,
            'imagenes_no_encontradas': imagenes_no_encontradas,
        }

        
        
        
def importar_datos_alimentos(request):
    if request.method == 'POST':
        centro_id = request.POST.get('centro')
        archivo = request.FILES.get('archivo')

        if not centro_id or not archivo:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('super:importar_datos_alimentos')

        centro = get_object_or_404(Centros, id=centro_id)

        try:
            importador = ImportadorAlimentos(centro)
            importador.importar_archivo(archivo)
            messages.success(request, "Importación de alimentos completada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al importar: {e}")

        return redirect('super:importar_datos_alimentos')

    centros = Centros.objects.all()
    return render(request, 'super/importar_alimentos.html', {'centros': centros})        