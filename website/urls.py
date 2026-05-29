from django.urls import path
from .views import IndexView, ContatoView, SobreView, login_view, logout_view

urlpatterns = [
    path("",         IndexView.as_view(), name="index"),
    path("contato/", ContatoView.as_view(), name="contato"),
    path("sobre/",   SobreView.as_view(), name="sobre"),

    path("login/",  login_view,  name="login"),
    path("logout/", logout_view, name="logout"),
]