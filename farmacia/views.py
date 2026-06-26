from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import Http404

from .models import Laboratorio, Distribuidora, Medicamento, ProdutoDiverso, Farmacia
from .forms  import (LaboratorioForm, DistribuidoraForm, MedicamentoForm,
                     ProdutoDiversoForm, UsuarioForm, GrupoForm, FarmaciaForm)


# ── Dashboard ────────────────────────────────────────────────────────────────
@login_required(login_url='/login/')
def dashboard(request):
    hoje = timezone.now().date()

    meus_meds  = Medicamento.objects.filter(cadastrado_por=request.user).select_related('laboratorio', 'distribuidora')
    meus_prods = ProdutoDiverso.objects.filter(cadastrado_por=request.user)
    meus_labs  = Laboratorio.objects.filter(cadastrado_por=request.user)
    meus_dists = Distribuidora.objects.filter(cadastrado_por=request.user)

    return render(request, 'website/dashboard.html', {
        'total_med':  Medicamento.objects.count()    if request.user.is_staff else meus_meds.count(),
        'total_prod': ProdutoDiverso.objects.count() if request.user.is_staff else meus_prods.count(),
        'total_lab':  Laboratorio.objects.count()    if request.user.is_staff else meus_labs.count(),
        'total_dist': Distribuidora.objects.count()  if request.user.is_staff else meus_dists.count(),

        'ultimos_meds':     meus_meds.order_by('-cadastrado_em')[:5],
        'meds_vencidos':    meus_meds.filter(data_validade__lt=hoje).order_by('data_validade')[:5],
        'meds_controlados': meus_meds.filter(controlado=True).order_by('-cadastrado_em')[:5],
        'ultimos_prods':    meus_prods.order_by('-cadastrado_em')[:5],
        'hoje': hoje,
    })


# ── Mixins ───────────────────────────────────────────────────────────────────

class FarmaciaLoginMixin(LoginRequiredMixin):
    login_url = '/login/'

    def form_valid(self, form):
        obj = form.save(commit=False)
        if not obj.pk:
            obj.cadastrado_por = self.request.user
        obj.save()
        return redirect(self.success_url)


class DonoOuStaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/login/'

    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_staff or obj.cadastrado_por == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para acessar este registro.')
        return redirect(self.request.META.get('HTTP_REFERER', 'dashboard'))


class GrupoRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/login/'
    grupo_requerido = None

    def test_func(self):
        if self.request.user.is_staff:
            return True
        if self.grupo_requerido:
            return self.request.user.groups.filter(name=self.grupo_requerido).exists()
        return False

    def handle_no_permission(self):
        messages.error(self.request, 'Seu grupo de usuário não tem acesso a esta área.')
        return redirect('dashboard')


# ── Laboratório ──────────────────────────────────────────────────────────────

class LaboratorioList(LoginRequiredMixin, ListView):
    model = Laboratorio
    template_name = 'website/laboratorio.html'
    context_object_name = 'labs'
    login_url = '/login/'
    paginate_by = 10

    def get_queryset(self):
        qs = Laboratorio.objects.select_related('cadastrado_por')
        if not self.request.user.is_staff:
            qs = qs.filter(cadastrado_por=self.request.user)
        return qs.order_by('-cadastrado_em')


class LaboratorioDetail(LoginRequiredMixin, DetailView):
    model = Laboratorio
    template_name = 'website/detalhe.html'
    login_url = '/login/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_staff and obj.cadastrado_por != self.request.user:
            raise Http404
        return obj


class LaboratorioCreate(FarmaciaLoginMixin, CreateView):
    model = Laboratorio
    form_class = LaboratorioForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('laboratorio_listar')
    extra_context = {'titulo': 'Novo Laboratório', 'botao': 'Criar Laboratório'}


class LaboratorioUpdate(DonoOuStaffMixin, FarmaciaLoginMixin, UpdateView):
    model = Laboratorio
    form_class = LaboratorioForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('laboratorio_listar')
    extra_context = {'titulo': 'Editar Laboratório', 'botao': 'Salvar Alterações'}


class LaboratorioDelete(DonoOuStaffMixin, DeleteView):
    model = Laboratorio
    template_name = 'website/form.html'
    success_url = reverse_lazy('laboratorio_listar')
    login_url = '/login/'
    extra_context = {'titulo': 'Excluir Laboratório', 'botao': 'Sim, excluir!'}


# ── Distribuidora ────────────────────────────────────────────────────────────

class DistribuidoraList(LoginRequiredMixin, ListView):
    model = Distribuidora
    template_name = 'website/distribuidora.html'
    context_object_name = 'dists'
    login_url = '/login/'
    paginate_by = 10

    def get_queryset(self):
        qs = Distribuidora.objects.select_related('cadastrado_por')
        if not self.request.user.is_staff:
            qs = qs.filter(cadastrado_por=self.request.user)
        return qs.order_by('-cadastrado_em')


class DistribuidoraDetail(LoginRequiredMixin, DetailView):
    model = Distribuidora
    template_name = 'website/detalhe.html'
    login_url = '/login/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_staff and obj.cadastrado_por != self.request.user:
            raise Http404
        return obj


class DistribuidoraCreate(FarmaciaLoginMixin, CreateView):
    model = Distribuidora
    form_class = DistribuidoraForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('distribuidora_listar')
    extra_context = {'titulo': 'Nova Distribuidora', 'botao': 'Criar Distribuidora'}


class DistribuidoraUpdate(DonoOuStaffMixin, FarmaciaLoginMixin, UpdateView):
    model = Distribuidora
    form_class = DistribuidoraForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('distribuidora_listar')
    extra_context = {'titulo': 'Editar Distribuidora', 'botao': 'Salvar Alterações'}


class DistribuidoraDelete(DonoOuStaffMixin, DeleteView):
    model = Distribuidora
    template_name = 'website/form.html'
    success_url = reverse_lazy('distribuidora_listar')
    login_url = '/login/'
    extra_context = {'titulo': 'Excluir Distribuidora', 'botao': 'Sim, excluir!'}


# ── Medicamento ──────────────────────────────────────────────────────────────

class MedicamentoList(LoginRequiredMixin, ListView):
    model = Medicamento
    template_name = 'website/medicamento.html'
    context_object_name = 'meds'
    login_url = '/login/'
    paginate_by = 10

    def get_queryset(self):
        qs = Medicamento.objects.select_related('laboratorio', 'distribuidora', 'cadastrado_por')
        if not self.request.user.is_staff:
            qs = qs.filter(cadastrado_por=self.request.user)
        return qs.order_by('-cadastrado_em')


class MedicamentoDetail(LoginRequiredMixin, DetailView):
    model = Medicamento
    template_name = 'website/detalhe.html'
    login_url = '/login/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_staff and obj.cadastrado_por != self.request.user:
            raise Http404
        return obj


class MedicamentoCreate(FarmaciaLoginMixin, CreateView):
    model = Medicamento
    form_class = MedicamentoForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('medicamento_listar')
    extra_context = {'titulo': 'Novo Medicamento', 'botao': 'Criar Medicamento', 'largura': 8}


class MedicamentoUpdate(DonoOuStaffMixin, FarmaciaLoginMixin, UpdateView):
    model = Medicamento
    form_class = MedicamentoForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('medicamento_listar')
    extra_context = {'titulo': 'Editar Medicamento', 'botao': 'Salvar Alterações', 'largura': 8}


class MedicamentoDelete(DonoOuStaffMixin, DeleteView):
    model = Medicamento
    template_name = 'website/form.html'
    success_url = reverse_lazy('medicamento_listar')
    login_url = '/login/'
    extra_context = {'titulo': 'Excluir Medicamento', 'botao': 'Sim, excluir!'}


# ── Produto Diverso ──────────────────────────────────────────────────────────

class ProdutoDiversoList(LoginRequiredMixin, ListView):
    model = ProdutoDiverso
    template_name = 'website/produto.html'
    context_object_name = 'prods'
    login_url = '/login/'
    paginate_by = 10

    def get_queryset(self):
        qs = ProdutoDiverso.objects.select_related('cadastrado_por')
        if not self.request.user.is_staff:
            qs = qs.filter(cadastrado_por=self.request.user)
        return qs.order_by('-cadastrado_em')


class ProdutoDiversoDetail(LoginRequiredMixin, DetailView):
    model = ProdutoDiverso
    template_name = 'website/detalhe.html'
    login_url = '/login/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_staff and obj.cadastrado_por != self.request.user:
            raise Http404
        return obj


class ProdutoDiversoCreate(FarmaciaLoginMixin, CreateView):
    model = ProdutoDiverso
    form_class = ProdutoDiversoForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('produto_listar')
    extra_context = {'titulo': 'Novo Produto', 'botao': 'Criar Produto'}


class ProdutoDiversoUpdate(DonoOuStaffMixin, FarmaciaLoginMixin, UpdateView):
    model = ProdutoDiverso
    form_class = ProdutoDiversoForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('produto_listar')
    extra_context = {'titulo': 'Editar Produto', 'botao': 'Salvar Alterações'}


class ProdutoDiversoDelete(DonoOuStaffMixin, DeleteView):
    model = ProdutoDiverso
    template_name = 'website/form.html'
    success_url = reverse_lazy('produto_listar')
    login_url = '/login/'
    extra_context = {'titulo': 'Excluir Produto', 'botao': 'Sim, excluir!'}


# ── Usuários ──────────────────────────────────────────────────────────────────

class UsuarioList(GrupoRequeridoMixin, ListView):
    model = User
    template_name = 'website/usuario.html'
    context_object_name = 'usuarios'
    grupo_requerido = 'Gerentes'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.order_by('username')


class UsuarioDetail(GrupoRequeridoMixin, DetailView):
    model = User
    template_name = 'website/detalhe.html'
    grupo_requerido = 'Gerentes'


class UsuarioCreate(GrupoRequeridoMixin, CreateView):
    model = User
    form_class = UsuarioForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('usuario_listar')
    grupo_requerido = 'Gerentes'
    extra_context = {'titulo': 'Novo Usuário', 'botao': 'Criar Usuário'}


class UsuarioUpdate(GrupoRequeridoMixin, UpdateView):
    model = User
    form_class = UsuarioForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('usuario_listar')
    grupo_requerido = 'Gerentes'
    extra_context = {'titulo': 'Editar Usuário', 'botao': 'Salvar Alterações'}


class UsuarioDelete(GrupoRequeridoMixin, DeleteView):
    model = User
    template_name = 'website/form.html'
    success_url = reverse_lazy('usuario_listar')
    grupo_requerido = 'Gerentes'
    extra_context = {'titulo': 'Excluir Usuário', 'botao': 'Sim, excluir!'}


# ── Grupos ────────────────────────────────────────────────────────────────────

class GrupoList(GrupoRequeridoMixin, ListView):
    model = Group
    template_name = 'website/grupo.html'
    context_object_name = 'grupos'
    grupo_requerido = 'Gerentes'
    paginate_by = 10

    def get_queryset(self):
        return Group.objects.order_by('name')


class GrupoDetail(GrupoRequeridoMixin, DetailView):
    model = Group
    template_name = 'website/detalhe.html'
    grupo_requerido = 'Gerentes'


class GrupoCreate(GrupoRequeridoMixin, CreateView):
    model = Group
    form_class = GrupoForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('grupo_listar')
    grupo_requerido = 'Gerentes'
    extra_context = {'titulo': 'Novo Grupo', 'botao': 'Criar Grupo'}


class GrupoUpdate(GrupoRequeridoMixin, UpdateView):
    model = Group
    form_class = GrupoForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('grupo_listar')
    grupo_requerido = 'Gerentes'
    extra_context = {'titulo': 'Editar Grupo', 'botao': 'Salvar Alterações'}


class GrupoDelete(GrupoRequeridoMixin, DeleteView):
    model = Group
    template_name = 'website/form.html'
    success_url = reverse_lazy('grupo_listar')
    grupo_requerido = 'Gerentes'
    extra_context = {'titulo': 'Excluir Grupo', 'botao': 'Sim, excluir!'}


# ── Farmácias ────────────────────────────────────────────────────────────────

class FarmaciaList(LoginRequiredMixin, ListView):
    model = Farmacia
    template_name = 'website/farmacia.html'
    context_object_name = 'farmacias'
    login_url = '/login/'
    paginate_by = 10

    def get_queryset(self):
        qs = Farmacia.objects.select_related('cadastrado_por', 'grupo')
        if not self.request.user.is_staff:
            qs = qs.filter(cadastrado_por=self.request.user)
        return qs.order_by('-cadastrado_em')


class FarmaciaDetail(LoginRequiredMixin, DetailView):
    model = Farmacia
    template_name = 'website/detalhe.html'
    login_url = '/login/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_staff and obj.cadastrado_por != self.request.user:
            raise Http404
        return obj


class FarmaciaCreate(FarmaciaLoginMixin, CreateView):
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('farmacia_listar')
    extra_context = {'titulo': 'Nova Farmácia', 'botao': 'Criar Farmácia'}


class FarmaciaUpdate(DonoOuStaffMixin, FarmaciaLoginMixin, UpdateView):
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'website/form.html'
    success_url = reverse_lazy('farmacia_listar')
    extra_context = {'titulo': 'Editar Farmácia', 'botao': 'Salvar Alterações'}


class FarmaciaDelete(DonoOuStaffMixin, DeleteView):
    model = Farmacia
    template_name = 'website/form.html'
    success_url = reverse_lazy('farmacia_listar')
    login_url = '/login/'
    extra_context = {'titulo': 'Excluir Farmácia', 'botao': 'Sim, excluir!'}