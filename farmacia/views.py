from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import Laboratorio, Distribuidora, Medicamento, ProdutoDiverso
from .forms  import (LaboratorioForm, DistribuidoraForm, MedicamentoForm,
                     ProdutoDiversoForm, UsuarioForm, GrupoForm)


# ── Auth ────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        user = authenticate(request,
                            username=request.POST["username"],
                            password=request.POST["password"])
        if user:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "website/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ── Dashboard ────────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    return render(request, "website/dashboard.html", {
        "total_med":  Medicamento.objects.count(),
        "total_prod": ProdutoDiverso.objects.count(),
        "total_lab":  Laboratorio.objects.count(),
        "total_dist": Distribuidora.objects.count(),
    })


# ── Mixin de autenticação + preenchimento automático de cadastrado_por ───────
class FarmaciaLoginMixin(LoginRequiredMixin):
    login_url = "/farmacia/login/"

    def form_valid(self, form):
        obj = form.save(commit=False)
        if not obj.pk:
            obj.cadastrado_por = self.request.user
        obj.save()
        return redirect(self.success_url)


# ── Laboratório ──────────────────────────────────────────────────────────────
class LaboratorioList(LoginRequiredMixin, ListView):
    model = Laboratorio
    template_name = "website/laboratorio.html"
    context_object_name = "labs"
    login_url = "/farmacia/login/"


class LaboratorioDetail(LoginRequiredMixin, DetailView):
    model = Laboratorio
    template_name = "website/detalhe.html"
    login_url = "/farmacia/login/"


class LaboratorioCreate(FarmaciaLoginMixin, CreateView):
    model = Laboratorio
    form_class = LaboratorioForm
    template_name = "website/form.html"
    success_url = reverse_lazy("laboratorio_listar")
    extra_context = {"titulo": "Novo Laboratório", "botao": "Criar Laboratório"}


class LaboratorioUpdate(FarmaciaLoginMixin, UpdateView):
    model = Laboratorio
    form_class = LaboratorioForm
    template_name = "website/form.html"
    success_url = reverse_lazy("laboratorio_listar")
    extra_context = {"titulo": "Editar Laboratório", "botao": "Salvar Alterações"}


class LaboratorioDelete(LoginRequiredMixin, DeleteView):
    model = Laboratorio
    template_name = "website/form.html"
    success_url = reverse_lazy("laboratorio_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Excluir Laboratório", "botao": "Sim, excluir!"}


# ── Distribuidora ────────────────────────────────────────────────────────────
class DistribuidoraList(LoginRequiredMixin, ListView):
    model = Distribuidora
    template_name = "website/distribuidora.html"
    context_object_name = "dists"
    login_url = "/farmacia/login/"


class DistribuidoraDetail(LoginRequiredMixin, DetailView):
    model = Distribuidora
    template_name = "website/detalhe.html"
    login_url = "/farmacia/login/"


class DistribuidoraCreate(FarmaciaLoginMixin, CreateView):
    model = Distribuidora
    form_class = DistribuidoraForm
    template_name = "website/form.html"
    success_url = reverse_lazy("distribuidora_listar")
    extra_context = {"titulo": "Nova Distribuidora", "botao": "Criar Distribuidora"}


class DistribuidoraUpdate(FarmaciaLoginMixin, UpdateView):
    model = Distribuidora
    form_class = DistribuidoraForm
    template_name = "website/form.html"
    success_url = reverse_lazy("distribuidora_listar")
    extra_context = {"titulo": "Editar Distribuidora", "botao": "Salvar Alterações"}


class DistribuidoraDelete(LoginRequiredMixin, DeleteView):
    model = Distribuidora
    template_name = "website/form.html"
    success_url = reverse_lazy("distribuidora_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Excluir Distribuidora", "botao": "Sim, excluir!"}


# ── Medicamento ──────────────────────────────────────────────────────────────
class MedicamentoList(LoginRequiredMixin, ListView):
    model = Medicamento
    template_name = "website/medicamento.html"
    context_object_name = "meds"
    login_url = "/farmacia/login/"


class MedicamentoDetail(LoginRequiredMixin, DetailView):
    model = Medicamento
    template_name = "website/detalhe.html"
    login_url = "/farmacia/login/"


class MedicamentoCreate(FarmaciaLoginMixin, CreateView):
    model = Medicamento
    form_class = MedicamentoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("medicamento_listar")
    extra_context = {"titulo": "Novo Medicamento", "botao": "Criar Medicamento", "largura": 8}


class MedicamentoUpdate(FarmaciaLoginMixin, UpdateView):
    model = Medicamento
    form_class = MedicamentoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("medicamento_listar")
    extra_context = {"titulo": "Editar Medicamento", "botao": "Salvar Alterações", "largura": 8}


class MedicamentoDelete(LoginRequiredMixin, DeleteView):
    model = Medicamento
    template_name = "website/form.html"
    success_url = reverse_lazy("medicamento_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Excluir Medicamento", "botao": "Sim, excluir!"}


# ── Produto Diverso ──────────────────────────────────────────────────────────
class ProdutoDiversoList(LoginRequiredMixin, ListView):
    model = ProdutoDiverso
    template_name = "website/produto.html"
    context_object_name = "prods"
    login_url = "/farmacia/login/"


class ProdutoDiversoDetail(LoginRequiredMixin, DetailView):
    model = ProdutoDiverso
    template_name = "website/detalhe.html"
    login_url = "/farmacia/login/"


class ProdutoDiversoCreate(FarmaciaLoginMixin, CreateView):
    model = ProdutoDiverso
    form_class = ProdutoDiversoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("produto_listar")
    extra_context = {"titulo": "Novo Produto", "botao": "Criar Produto"}


class ProdutoDiversoUpdate(FarmaciaLoginMixin, UpdateView):
    model = ProdutoDiverso
    form_class = ProdutoDiversoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("produto_listar")
    extra_context = {"titulo": "Editar Produto", "botao": "Salvar Alterações"}


class ProdutoDiversoDelete(LoginRequiredMixin, DeleteView):
    model = ProdutoDiverso
    template_name = "website/form.html"
    success_url = reverse_lazy("produto_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Excluir Produto", "botao": "Sim, excluir!"}


# ── Usuários ─────────────────────────────────────────────────────────────────
class UsuarioList(LoginRequiredMixin, ListView):
    model = User
    template_name = "website/usuario.html"
    context_object_name = "usuarios"
    login_url = "/farmacia/login/"


class UsuarioDetail(LoginRequiredMixin, DetailView):
    model = User
    template_name = "website/detalhe.html"
    login_url = "/farmacia/login/"


class UsuarioCreate(LoginRequiredMixin, CreateView):
    model = User
    form_class = UsuarioForm
    template_name = "website/form.html"
    success_url = reverse_lazy("usuario_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Novo Usuário", "botao": "Criar Usuário"}


class UsuarioUpdate(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioForm
    template_name = "website/form.html"
    success_url = reverse_lazy("usuario_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Editar Usuário", "botao": "Salvar Alterações"}


class UsuarioDelete(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "website/form.html"
    success_url = reverse_lazy("usuario_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Excluir Usuário", "botao": "Sim, excluir!"}


# ── Grupos ────────────────────────────────────────────────────────────────────
class GrupoList(LoginRequiredMixin, ListView):
    model = Group
    template_name = "website/grupo.html"
    context_object_name = "grupos"
    login_url = "/farmacia/login/"


class GrupoDetail(LoginRequiredMixin, DetailView):
    model = Group
    template_name = "website/detalhe.html"
    login_url = "/farmacia/login/"


class GrupoCreate(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GrupoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("grupo_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Novo Grupo", "botao": "Criar Grupo"}


class GrupoUpdate(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GrupoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("grupo_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Editar Grupo", "botao": "Salvar Alterações"}


class GrupoDelete(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = "website/form.html"
    success_url = reverse_lazy("grupo_listar")
    login_url = "/farmacia/login/"
    extra_context = {"titulo": "Excluir Grupo", "botao": "Sim, excluir!"}