# app/core/signals.py

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from decimal import Decimal
from django.forms.models import model_to_dict
from datetime import date, datetime
from django.db.models.fields.files import FieldFile
from app.recepcion.models import Recepcion, Merma, Proveedor, TipoDeMerma
from app.core.middleware.usuario_actual import get_usuario_actual
from app.core.models import RegistroAccion
from app.super.models import UserProfile
from app.dashuser.models import *
from app.platos.models import *

def convertir_valor(valor):
    """Convierte valores no serializables en tipos manejables para JSON."""
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, FieldFile):  # Archivos / imágenes
        return valor.url if valor and hasattr(valor, "url") else None
    return valor


def registrar_accion(instance, accion, old_instance=None):
    """
    Crea un registro de acción para cualquier modelo.
    Si es modificación, guarda los cambios antes/después.
    """
    user = get_usuario_actual()
    usuario = UserProfile.objects.filter(user=user).first() if user else None
    centro = usuario.centro if usuario else None

    cambios = None

    if accion == "modificar" and old_instance:
        cambios = {}
        old_dict = model_to_dict(old_instance)
        new_dict = model_to_dict(instance)
        EXCLUIR_CAMPOS = ["observaciones", "fecha_creacion", "id"]
        for field, nuevo in new_dict.items():
            if field in EXCLUIR_CAMPOS:
                continue
            viejo = old_dict.get(field)
            nuevo = convertir_valor(nuevo)
            viejo = convertir_valor(viejo)
            if nuevo != viejo:
                cambios[field] = {"antes": viejo, "despues": nuevo}

    elif accion == "crear":
        cambios = {}
        new_dict = model_to_dict(instance)
        EXCLUIR_CAMPOS = ["observaciones", "fecha_creacion", "id", "centro"]
        for field, valor in new_dict.items():
            if field in EXCLUIR_CAMPOS:
                continue
            cambios[field] = {"antes": None, "despues": convertir_valor(valor)}

    if usuario and centro:
        RegistroAccion.objects.create(
            usuario=usuario,
            centro=centro,
            accion=accion,
            modelo=instance.__class__.__name__,
            objeto_id=instance.pk,
            objeto_repr=str(instance),
            cambios=cambios,
        )
    else:
        print(f"[WARN] RegistroAccion no creado: usuario o centro ausente para {instance}")

# ---PROVEEDOR ---

@receiver(pre_save, sender=Proveedor)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Proveedor)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Proveedor)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')  
    
    
# --- RECEPCION ---

@receiver(pre_save, sender=Recepcion)
def recepcion_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Recepcion)
def recepcion_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Recepcion)
def recepcion_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')


# --- TIPO DE MERMA ---

@receiver(pre_save, sender=TipoDeMerma)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=TipoDeMerma)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=TipoDeMerma)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')
    
    
# --- MERMA ---

@receiver(pre_save, sender=Merma)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Merma)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Merma)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')
    
    
# --- ALERGENOS ---

@receiver(pre_save, sender=Alergenos)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Alergenos)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Alergenos)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')    


# --- TRAZAS ---

@receiver(pre_save, sender=Trazas)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Trazas)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Trazas)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar') 
    
    
    
# --- UNIDAD DE MEDIDA ---

@receiver(pre_save, sender=UnidadDeMedida)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=UnidadDeMedida)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=UnidadDeMedida)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')     
    
    
# --- TIPO DE ALIMENTO ---

@receiver(pre_save, sender=TipoAlimento)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=TipoAlimento)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=TipoAlimento)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')     
    
    
# --- LOCALIZACIÓN ---

@receiver(pre_save, sender=localizacion)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=localizacion)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=localizacion)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')  
    
    
# --- CONSERVACIÓN ---

@receiver(pre_save, sender=Conservacion)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Conservacion)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Conservacion)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')     
    
    
# --- ALIMENTO ---

@receiver(pre_save, sender=Alimento)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Alimento)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Alimento)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')   
    
    
# --- INFORMACIÓN NUTRICIONAL ---

@receiver(pre_save, sender=InformacionNutricional)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=InformacionNutricional)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=InformacionNutricional)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')    
    

# --- TEXTO MODO DE USO ---

@receiver(pre_save, sender=TextoModo)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=TextoModo)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=TextoModo)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')  
    
    
# --- PLATO ---

@receiver(pre_save, sender=Plato)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Plato)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Plato)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')        
    
    
# --- TIPO DE PLATO ---

@receiver(pre_save, sender=TipoPlato)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=TipoPlato)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=TipoPlato)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')   
    
    
# --- INGREDIENTES DEL PLATO ---

@receiver(pre_save, sender=AlimentoPlato)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=AlimentoPlato)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=AlimentoPlato)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar') 
    
    
    
# --- RECETA DEL PLATO ---

@receiver(pre_save, sender=Receta)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Receta)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Receta)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')   
    
    
# --- SALSA ---

@receiver(pre_save, sender=Salsa)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Salsa)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=Salsa)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')    
    
    
# ---ALIMENTOS DE LA SALSA ---

@receiver(pre_save, sender=AlimentoSalsa)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=AlimentoSalsa)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=AlimentoSalsa)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')   
    
    
# ---USUARIOS ---

@receiver(pre_save, sender=UserProfile)
def merma_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=UserProfile)
def merma_post_save(sender, instance, created, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if created:
        registrar_accion(instance, 'crear')
    else:
        registrar_accion(instance, 'modificar', old_instance=old_instance)


@receiver(post_delete, sender=UserProfile)
def merma_post_delete(sender, instance, **kwargs):
    registrar_accion(instance, 'eliminar')                         
    
