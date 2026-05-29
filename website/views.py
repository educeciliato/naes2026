from django.views.generic import TemplateView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect


class IndexView(TemplateView):
    template_name = "website/index.html"

class ContatoView(TemplateView):
    template_name = "website/contato.html"

class SobreView(TemplateView):
    template_name = "website/sobre.html"


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next") or "dashboard"
            return redirect(next_url)
        messages.error(request, "Usuário ou senha inválidos.")

    next_url = request.GET.get("next", "")
    return render(request, "website/login.html", {"next": next_url})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Você saiu do sistema com sucesso.")
    return redirect("index")