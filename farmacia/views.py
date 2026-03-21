from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages

from .models import Laboratorio, Distribuidora, Medicamento, ProdutoDiverso
from .forms  import (LaboratorioForm, DistribuidoraForm, MedicamentoForm,
                     ProdutoDiversoForm, UsuarioForm, GrupoForm)


# ── Auth ────────────────────────────────
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


# ── Dashboard ───────────────────────────
@login_required
def dashboard(request):
    return render(request, "website/dashboard.html", {
        "total_med":  Medicamento.objects.count(),
        "total_prod": ProdutoDiverso.objects.count(),
        "total_lab":  Laboratorio.objects.count(),
        "total_dist": Distribuidora.objects.count(),
    })


# ── Helpers CRUD genéricos ───────────────
def _listar(request, qs, template, ctx_name):
    return render(request, template, {ctx_name: qs})

def _form(request, form_class, template, redirect_to, instance=None):
    form = form_class(request.POST or None, instance=instance)
    if form.is_valid():
        obj = form.save(commit=False)
        if not obj.pk:                        # só preenche na criação
            obj.cadastrado_por = request.user
        obj.save()
        return redirect(redirect_to)
    return render(request, template, {"form": form})

def _excluir(request, obj, redirect_to):
    if request.method == "POST":
        obj.delete()
        return redirect(redirect_to)
    return render(request, "website/confirmar_exclusao.html", {"obj": obj})


# ── Laboratório ─────────────────────────
@login_required
def lab_listar(request):
    return _listar(request, Laboratorio.objects.all(), "website/laboratorio.html", "labs")

@login_required
def lab_form(request, pk=None):
    inst = get_object_or_404(Laboratorio, pk=pk) if pk else None
    return _form(request, LaboratorioForm, "website/form.html", "lab_listar", inst)

@login_required
def lab_excluir(request, pk):
    return _excluir(request, get_object_or_404(Laboratorio, pk=pk), "lab_listar")


# ── Distribuidora ───────────────────────
@login_required
def dist_listar(request):
    return _listar(request, Distribuidora.objects.all(), "website/distribuidora.html", "dists")

@login_required
def dist_form(request, pk=None):
    inst = get_object_or_404(Distribuidora, pk=pk) if pk else None
    return _form(request, DistribuidoraForm, "website/form.html", "dist_listar", inst)

@login_required
def dist_excluir(request, pk):
    return _excluir(request, get_object_or_404(Distribuidora, pk=pk), "dist_listar")


# ── Medicamento ─────────────────────────
@login_required
def med_listar(request):
    return _listar(request, Medicamento.objects.all(), "website/medicamento.html", "meds")

@login_required
def med_form(request, pk=None):
    inst = get_object_or_404(Medicamento, pk=pk) if pk else None
    return _form(request, MedicamentoForm, "website/form.html", "med_listar", inst)

@login_required
def med_excluir(request, pk):
    return _excluir(request, get_object_or_404(Medicamento, pk=pk), "med_listar")


# ── Produto Diverso ─────────────────────
@login_required
def prod_listar(request):
    return _listar(request, ProdutoDiverso.objects.all(), "website/produto.html", "prods")

@login_required
def prod_form(request, pk=None):
    inst = get_object_or_404(ProdutoDiverso, pk=pk) if pk else None
    return _form(request, ProdutoDiversoForm, "website/form.html", "prod_listar", inst)

@login_required
def prod_excluir(request, pk):
    return _excluir(request, get_object_or_404(ProdutoDiverso, pk=pk), "prod_listar")


# ── Usuários ────────────────────────────
@login_required
def usr_listar(request):
    return _listar(request, User.objects.all(), "website/usuario.html", "usuarios")

@login_required
def usr_form(request, pk=None):
    inst = get_object_or_404(User, pk=pk) if pk else None
    return _form(request, UsuarioForm, "website/form.html", "usr_listar", inst)

@login_required
def usr_excluir(request, pk):
    return _excluir(request, get_object_or_404(User, pk=pk), "usr_listar")


# ── Grupos ──────────────────────────────
@login_required
def grp_listar(request):
    return _listar(request, Group.objects.all(), "website/grupo.html", "grupos")

@login_required
def grp_form(request, pk=None):
    inst = get_object_or_404(Group, pk=pk) if pk else None
    return _form(request, GrupoForm, "website/form.html", "grp_listar", inst)

@login_required
def grp_excluir(request, pk):
    return _excluir(request, get_object_or_404(Group, pk=pk), "grp_listar")