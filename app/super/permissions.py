from app.super.models import Permiso



def tiene_permiso(user_profile, modulo, accion):
    """
    Devuelve True si el usuario tiene permiso sobre el módulo y acción indicada.
    - user_profile: instancia de UserProfile
    - modulo: string, nombre del módulo ("Proveedores", "Alérgenos", etc.)
    - accion: string, "create", "read", "update", "delete"
    """
    if not user_profile or not user_profile.estado:
        return False

    # Si eres superusuario, tienes todos los permisos
    try:
        if user_profile.user.is_superuser:
            return True
    except AttributeError:
        return False

    # Consulta en la tabla de permisos
    return Permiso.objects.filter(
        usuario=user_profile,
        modulo=modulo,
        accion=accion
    ).exists()
