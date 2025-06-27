from django.http import HttpResponseForbidden
from functools import wraps

def tipo_usuario_requerido(*tipos_permitidos):
    """
    Decorador para permitir acesso apenas a usuários com tipo específico.
    Exemplo: @tipo_usuario_requerido('master', 'editor')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Acesso negado: usuário não autenticado.")
            if request.user.tipo not in tipos_permitidos:
                return HttpResponseForbidden("Acesso negado: permissão insuficiente.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator