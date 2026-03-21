from django.urls import path
from . import views

urlpatterns = [
    path("login/",  views.login_view,  name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("",        views.dashboard,   name="dashboard"),

    # Laboratório
    path("laboratorios/",            views.lab_listar,          name="lab_listar"),
    path("laboratorios/novo/",       views.lab_form,            name="lab_novo"),
    path("laboratorios/<int:pk>/",   views.lab_form,            name="lab_editar"),
    path("laboratorios/<int:pk>/excluir/", views.lab_excluir,   name="lab_excluir"),

    # Distribuidora
    path("distribuidoras/",            views.dist_listar,        name="dist_listar"),
    path("distribuidoras/novo/",       views.dist_form,          name="dist_novo"),
    path("distribuidoras/<int:pk>/",   views.dist_form,          name="dist_editar"),
    path("distribuidoras/<int:pk>/excluir/", views.dist_excluir, name="dist_excluir"),

    # Medicamento
    path("medicamentos/",            views.med_listar,           name="med_listar"),
    path("medicamentos/novo/",       views.med_form,             name="med_novo"),
    path("medicamentos/<int:pk>/",   views.med_form,             name="med_editar"),
    path("medicamentos/<int:pk>/excluir/", views.med_excluir,    name="med_excluir"),

    # Produto Diverso
    path("produtos/",            views.prod_listar,              name="prod_listar"),
    path("produtos/novo/",       views.prod_form,                name="prod_novo"),
    path("produtos/<int:pk>/",   views.prod_form,                name="prod_editar"),
    path("produtos/<int:pk>/excluir/", views.prod_excluir,       name="prod_excluir"),

    # Usuários
    path("usuarios/",            views.usr_listar,               name="usr_listar"),
    path("usuarios/novo/",       views.usr_form,                 name="usr_novo"),
    path("usuarios/<int:pk>/",   views.usr_form,                 name="usr_editar"),
    path("usuarios/<int:pk>/excluir/", views.usr_excluir,        name="usr_excluir"),

    # Grupos
    path("grupos/",            views.grp_listar,                 name="grp_listar"),
    path("grupos/novo/",       views.grp_form,                   name="grp_novo"),
    path("grupos/<int:pk>/",   views.grp_form,                   name="grp_editar"),
    path("grupos/<int:pk>/excluir/", views.grp_excluir,          name="grp_excluir"),
]