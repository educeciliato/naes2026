"""Quem é administrador do PharmaSys e o mixin das áreas restritas.

Uma regra só, usada pelas views de Usuários/Grupos, pelas telas de gestão da
IA e pelo menu (context processor ``permissoes``).
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

GRUPO_ADMIN = 'Gerentes'


def eh_admin(usuario):
    """Superusuário, staff ou membro do grupo "Gerentes"."""
    if not getattr(usuario, 'is_authenticated', False):
        return False
    if usuario.is_superuser or usuario.is_staff:
        return True
    return usuario.groups.filter(name=GRUPO_ADMIN).exists()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Área de administração. Visitante vai para o login; usuário comum
    volta ao dashboard com uma mensagem de erro."""

    login_url = '/login/'

    def test_func(self):
        return eh_admin(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'Somente gerentes têm acesso a esta área.')
        return redirect('dashboard')
