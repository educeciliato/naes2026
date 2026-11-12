"""Views do PharmaSys (dashboard e CRUDs).

Segurança por dono: Laboratório, Distribuidora, Medicamento, Produto Diverso
e Farmácia pertencem a quem os cadastrou (``cadastrado_por``). A fronteira é
o ``get_queryset()`` filtrado pelo usuário logado (``DonoQuerysetMixin``):
registro de outra pessoa dá 404 em detalhe, edição e exclusão, e não aparece
nas listagens — inclusive para staff.

Mensagens: toda criação, alteração e exclusão usa o framework de mensagens
(``MensagemCrudMixin``); exclusão bloqueada por registros ligados (PROTECT)
vira ``messages.error`` em vez de erro 500.
"""
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.db.models import Count, ProtectedError
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django_filters.views import FilterView

from .filters import (DistribuidoraFilter, FarmaciaFilter, LaboratorioFilter,
                      MedicamentoFilter, ProdutoDiversoFilter)
from .forms import (DistribuidoraForm, FarmaciaForm, FormDoUsuario, GrupoForm, LaboratorioForm,
                    MedicamentoForm, ProdutoDiversoForm, UsuarioForm, UsuarioUpdateForm)
from .models import Distribuidora, Farmacia, Laboratorio, Medicamento, ProdutoDiverso
from .permissoes import AdminRequiredMixin

# Mantido para compatibilidade com código antigo que importava este nome.
GrupoRequeridoMixin = AdminRequiredMixin


# ── Dashboard ────────────────────────────────────────────────────────────────

@login_required(login_url='/login/')
def dashboard(request):
    hoje = timezone.localdate()
    meus_meds = Medicamento.objects.filter(cadastrado_por=request.user)

    return render(request, 'website/dashboard.html', {
        'total_med':  meus_meds.count(),
        'total_prod': ProdutoDiverso.objects.filter(cadastrado_por=request.user).count(),
        'total_lab':  Laboratorio.objects.filter(cadastrado_por=request.user).count(),
        'total_dist': Distribuidora.objects.filter(cadastrado_por=request.user).count(),
        # select_related: a tabela mostra o laboratório de cada medicamento;
        # sem ele seria 1 consulta extra por linha (N+1).
        'meds_alerta': (
            meus_meds.select_related('laboratorio')
            .filter(data_validade__lte=hoje + timedelta(days=30))
            .order_by('data_validade')[:5]
        ),
        'hoje': hoje,
    })


# ── Mixins ───────────────────────────────────────────────────────────────────

class DonoQuerysetMixin(LoginRequiredMixin):
    """Só os registros do usuário logado (404 para os dos outros)."""
    login_url = '/login/'
    relacionados = ()  # nomes para select_related (evita N+1 nas tabelas)

    def get_queryset(self):
        qs = super().get_queryset().filter(cadastrado_por=self.request.user)
        if self.relacionados:
            qs = qs.select_related(*self.relacionados)
        return qs


class FormComUsuarioMixin:
    """Entrega o usuário logado ao form (FKs limitadas aos registros dele)."""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if issubclass(self.get_form_class(), FormDoUsuario):
            kwargs['usuario'] = self.request.user
        return kwargs


class MensagemCrudMixin:
    """Mensagem de sucesso no cadastro, na alteração e na exclusão."""
    acao = ''        # 'cadastrad', 'atualizad', 'excluíd'
    genero = 'o'     # 'o' ou 'a' (ex.: "Distribuidora ... excluída")

    def get_success_message(self):
        nome = self.model._meta.verbose_name.capitalize()
        return f'{nome} "{self.object}" {self.acao}{self.genero} com sucesso.'

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, self.get_success_message())
        return resposta


class DetalheMixin:
    """Monta a lista (rótulo, valor) dos campos para o template detalhe.html."""
    url_base = ''
    campos_ocultos = ('id', 'password')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.object
        campos = []
        for campo in obj._meta.fields:
            if campo.name in self.campos_ocultos:
                continue
            if campo.choices:
                valor = getattr(obj, f'get_{campo.name}_display')()
            else:
                valor = getattr(obj, campo.name)
            campos.append((campo.verbose_name, valor))
        ctx.update(
            campos=campos,
            nome_modelo=obj._meta.verbose_name,
            nome_plural=obj._meta.verbose_name_plural,
            url_listar=reverse(f'{self.url_base}_listar'),
            url_editar=reverse(f'{self.url_base}_editar', args=[obj.pk]),
            url_excluir=reverse(f'{self.url_base}_excluir', args=[obj.pk]),
        )
        return ctx


# ── Bases genéricas dos CRUDs por dono ───────────────────────────────────────

class DonoListView(DonoQuerysetMixin, FilterView):
    """Lista com django-filter + paginação (website/_paginacao.html)."""
    paginate_by = 10
    ordering = ['-cadastrado_em']


class DonoDetailView(DonoQuerysetMixin, DetalheMixin, DetailView):
    template_name = 'website/detalhe.html'


class DonoCreateView(LoginRequiredMixin, FormComUsuarioMixin, MensagemCrudMixin, CreateView):
    login_url = '/login/'
    template_name = 'website/form.html'
    acao = 'cadastrad'

    def form_valid(self, form):
        form.instance.cadastrado_por = self.request.user
        return super().form_valid(form)


class DonoUpdateView(DonoQuerysetMixin, FormComUsuarioMixin, MensagemCrudMixin, UpdateView):
    template_name = 'website/form.html'
    acao = 'atualizad'


class DonoDeleteView(DonoQuerysetMixin, MensagemCrudMixin, DeleteView):
    template_name = 'website/form.html'
    acao = 'excluíd'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f'Não foi possível excluir "{self.object}": existem outros cadastros ligados a ele(a).')
            return redirect(self.get_success_url())


# ── Laboratório ──────────────────────────────────────────────────────────────

class LaboratorioList(DonoListView):
    model = Laboratorio
    filterset_class = LaboratorioFilter
    template_name = 'website/laboratorio.html'
    context_object_name = 'labs'


class LaboratorioDetail(DonoDetailView):
    model = Laboratorio
    url_base = 'laboratorio'


class LaboratorioCreate(DonoCreateView):
    model = Laboratorio
    form_class = LaboratorioForm
    success_url = reverse_lazy('laboratorio_listar')
    extra_context = {'titulo': 'Novo Laboratório', 'botao': 'Criar Laboratório'}


class LaboratorioUpdate(DonoUpdateView):
    model = Laboratorio
    form_class = LaboratorioForm
    success_url = reverse_lazy('laboratorio_listar')
    extra_context = {'titulo': 'Editar Laboratório', 'botao': 'Salvar Alterações'}


class LaboratorioDelete(DonoDeleteView):
    model = Laboratorio
    success_url = reverse_lazy('laboratorio_listar')
    extra_context = {'titulo': 'Excluir Laboratório', 'botao': 'Sim, excluir!'}


# ── Distribuidora ────────────────────────────────────────────────────────────

class DistribuidoraList(DonoListView):
    model = Distribuidora
    filterset_class = DistribuidoraFilter
    template_name = 'website/distribuidora.html'
    context_object_name = 'dists'


class DistribuidoraDetail(DonoDetailView):
    model = Distribuidora
    url_base = 'distribuidora'


class DistribuidoraCreate(DonoCreateView):
    model = Distribuidora
    form_class = DistribuidoraForm
    genero = 'a'
    success_url = reverse_lazy('distribuidora_listar')
    extra_context = {'titulo': 'Nova Distribuidora', 'botao': 'Criar Distribuidora'}


class DistribuidoraUpdate(DonoUpdateView):
    model = Distribuidora
    form_class = DistribuidoraForm
    genero = 'a'
    success_url = reverse_lazy('distribuidora_listar')
    extra_context = {'titulo': 'Editar Distribuidora', 'botao': 'Salvar Alterações'}


class DistribuidoraDelete(DonoDeleteView):
    model = Distribuidora
    genero = 'a'
    success_url = reverse_lazy('distribuidora_listar')
    extra_context = {'titulo': 'Excluir Distribuidora', 'botao': 'Sim, excluir!'}


# ── Medicamento ──────────────────────────────────────────────────────────────

class MedicamentoList(DonoListView):
    model = Medicamento
    filterset_class = MedicamentoFilter
    template_name = 'website/medicamento.html'
    context_object_name = 'meds'
    # A tabela mostra o laboratório: sem select_related seria 1 query por linha.
    relacionados = ('laboratorio', 'distribuidora')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['hoje'] = timezone.localdate()
        return ctx


class MedicamentoDetail(DonoDetailView):
    model = Medicamento
    url_base = 'medicamento'
    relacionados = ('laboratorio', 'distribuidora', 'cadastrado_por')


class MedicamentoCreate(DonoCreateView):
    model = Medicamento
    form_class = MedicamentoForm
    success_url = reverse_lazy('medicamento_listar')
    extra_context = {'titulo': 'Novo Medicamento', 'botao': 'Criar Medicamento', 'largura': 8}


class MedicamentoUpdate(DonoUpdateView):
    model = Medicamento
    form_class = MedicamentoForm
    success_url = reverse_lazy('medicamento_listar')
    extra_context = {'titulo': 'Editar Medicamento', 'botao': 'Salvar Alterações', 'largura': 8}


class MedicamentoDelete(DonoDeleteView):
    model = Medicamento
    success_url = reverse_lazy('medicamento_listar')
    extra_context = {'titulo': 'Excluir Medicamento', 'botao': 'Sim, excluir!'}


# ── Produto Diverso ──────────────────────────────────────────────────────────

class ProdutoDiversoList(DonoListView):
    model = ProdutoDiverso
    filterset_class = ProdutoDiversoFilter
    template_name = 'website/produto.html'
    context_object_name = 'prods'


class ProdutoDiversoDetail(DonoDetailView):
    model = ProdutoDiverso
    url_base = 'produto'


class ProdutoDiversoCreate(DonoCreateView):
    model = ProdutoDiverso
    form_class = ProdutoDiversoForm
    success_url = reverse_lazy('produto_listar')
    extra_context = {'titulo': 'Novo Produto', 'botao': 'Criar Produto'}


class ProdutoDiversoUpdate(DonoUpdateView):
    model = ProdutoDiverso
    form_class = ProdutoDiversoForm
    success_url = reverse_lazy('produto_listar')
    extra_context = {'titulo': 'Editar Produto', 'botao': 'Salvar Alterações'}


class ProdutoDiversoDelete(DonoDeleteView):
    model = ProdutoDiverso
    success_url = reverse_lazy('produto_listar')
    extra_context = {'titulo': 'Excluir Produto', 'botao': 'Sim, excluir!'}


# ── Farmácias ────────────────────────────────────────────────────────────────

class FarmaciaList(DonoListView):
    model = Farmacia
    filterset_class = FarmaciaFilter
    template_name = 'website/farmacia.html'
    context_object_name = 'farmacias'
    relacionados = ('grupo',)


class FarmaciaDetail(DonoDetailView):
    model = Farmacia
    url_base = 'farmacia'
    relacionados = ('grupo', 'cadastrado_por')


class FarmaciaCreate(DonoCreateView):
    model = Farmacia
    form_class = FarmaciaForm
    genero = 'a'
    success_url = reverse_lazy('farmacia_listar')
    extra_context = {'titulo': 'Nova Farmácia', 'botao': 'Criar Farmácia'}


class FarmaciaUpdate(DonoUpdateView):
    model = Farmacia
    form_class = FarmaciaForm
    genero = 'a'
    success_url = reverse_lazy('farmacia_listar')
    extra_context = {'titulo': 'Editar Farmácia', 'botao': 'Salvar Alterações'}


class FarmaciaDelete(DonoDeleteView):
    model = Farmacia
    genero = 'a'
    success_url = reverse_lazy('farmacia_listar')
    extra_context = {'titulo': 'Excluir Farmácia', 'botao': 'Sim, excluir!'}


# ── Usuários (somente gerentes) ──────────────────────────────────────────────

class UsuarioList(AdminRequiredMixin, ListView):
    model = User
    template_name = 'website/usuario.html'
    context_object_name = 'usuarios'
    paginate_by = 10

    def get_queryset(self):
        # prefetch_related: a tabela mostra os grupos de cada usuário.
        return User.objects.prefetch_related('groups').order_by('username')


class UsuarioDetail(AdminRequiredMixin, DetalheMixin, DetailView):
    model = User
    template_name = 'website/detalhe.html'
    url_base = 'usuario'


class UsuarioCreate(AdminRequiredMixin, MensagemCrudMixin, CreateView):
    model = User
    form_class = UsuarioForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('usuario_listar')
    acao = 'cadastrad'
    extra_context = {'titulo': 'Novo Usuário', 'botao': 'Criar Usuário'}


class UsuarioUpdate(AdminRequiredMixin, MensagemCrudMixin, UpdateView):
    model = User
    form_class = UsuarioUpdateForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('usuario_listar')
    acao = 'atualizad'
    extra_context = {'titulo': 'Editar Usuário', 'botao': 'Salvar Alterações'}


class UsuarioDelete(AdminRequiredMixin, MensagemCrudMixin, DeleteView):
    model = User
    template_name = 'website/form.html'
    success_url = reverse_lazy('usuario_listar')
    acao = 'excluíd'
    extra_context = {'titulo': 'Excluir Usuário', 'botao': 'Sim, excluir!'}

    def form_valid(self, form):
        if self.object == self.request.user:
            messages.error(self.request, 'Você não pode excluir o seu próprio usuário.')
            return redirect(self.success_url)
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f'Não foi possível excluir "{self.object}": o usuário tem cadastros no sistema. '
                'Desative-o em "Editar".')
            return redirect(self.success_url)


# ── Grupos (somente gerentes) ────────────────────────────────────────────────

class GrupoList(AdminRequiredMixin, ListView):
    model = Group
    template_name = 'website/grupo.html'
    context_object_name = 'grupos'
    paginate_by = 10

    def get_queryset(self):
        # annotate: o template mostrava g.user_set.count (1 COUNT por linha,
        # visto como "queries repetidas" na Debug Toolbar). Agora é 1 query só.
        return Group.objects.annotate(num_membros=Count('user')).order_by('name')


class GrupoDetail(AdminRequiredMixin, DetalheMixin, DetailView):
    model = Group
    template_name = 'website/detalhe.html'
    url_base = 'grupo'


class GrupoCreate(AdminRequiredMixin, MensagemCrudMixin, CreateView):
    model = Group
    form_class = GrupoForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('grupo_listar')
    acao = 'cadastrad'
    extra_context = {'titulo': 'Novo Grupo', 'botao': 'Criar Grupo'}


class GrupoUpdate(AdminRequiredMixin, MensagemCrudMixin, UpdateView):
    model = Group
    form_class = GrupoForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('grupo_listar')
    acao = 'atualizad'
    extra_context = {'titulo': 'Editar Grupo', 'botao': 'Salvar Alterações'}


class GrupoDelete(AdminRequiredMixin, MensagemCrudMixin, DeleteView):
    model = Group
    template_name = 'website/form.html'
    success_url = reverse_lazy('grupo_listar')
    acao = 'excluíd'
    extra_context = {'titulo': 'Excluir Grupo', 'botao': 'Sim, excluir!'}

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, f'Não foi possível excluir "{self.object}": há farmácias ligadas a ele.')
            return redirect(self.success_url)
