from django.utils.functional import SimpleLazyObject

from .permissoes import eh_admin


def permissoes(request):
    """``eh_admin`` no contexto de todos os templates (menu de gestão).

    Preguiçoso: a consulta aos grupos só acontece se o template usar a variável.
    """
    return {'eh_admin': SimpleLazyObject(lambda: eh_admin(request.user))}
