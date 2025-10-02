import threading

# Creamos un objeto thread-safe para guardar el usuario actual
_usuario_actual = threading.local()

class UsuarioActualMiddleware:
    """
    Middleware que almacena el usuario actual en un objeto thread-local
    para que pueda ser accedido en signals y otras partes del código.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Guardamos el usuario actual, si existe
        _usuario_actual.user = getattr(request, 'user', None)
        response = self.get_response(request)
        return response

def get_usuario_actual():
    """
    Función para obtener el usuario actual desde cualquier parte del código.
    """
    return getattr(_usuario_actual, 'user', None)

def set_usuario_actual(usuario):
    """
    Asigna un usuario al thread-local para usarlo fuera de una request,
    por ejemplo en shell o scripts.
    """
    _usuario_actual.user = usuario


