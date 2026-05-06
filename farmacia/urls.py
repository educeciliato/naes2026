from django.urls import path
from . import views
from .views import login_view, logout_view, dashboard

urlpatterns = [
    path("login/",  login_view,  name="login"),
    path("logout/", logout_view, name="logout"),
    path("",        dashboard,   name="dashboard"),

    # Laboratório
    path("laboratorios/",                   views.LaboratorioList.as_view(),   name="lab_listar"),
    path("laboratorios/novo/",              views.LaboratorioCreate.as_view(), name="lab_novo"),
    path("laboratorios/<int:pk>/editar/",   views.LaboratorioUpdate.as_view(), name="lab_editar"),
    path("laboratorios/<int:pk>/excluir/",  views.LaboratorioDelete.as_view(), name="lab_excluir"),

    # Distribuidora
    path("distribuidoras/",                  views.DistribuidoraList.as_view(),   name="dist_listar"),
    path("distribuidoras/novo/",             views.DistribuidoraCreate.as_view(), name="dist_novo"),
    path("distribuidoras/<int:pk>/editar/",  views.DistribuidoraUpdate.as_view(), name="dist_editar"),
    path("distribuidoras/<int:pk>/excluir/", views.DistribuidoraDelete.as_view(), name="dist_excluir"),

    # Medicamento
    path("medicamentos/",                  views.MedicamentoList.as_view(),   name="med_listar"),
    path("medicamentos/novo/",             views.MedicamentoCreate.as_view(), name="med_novo"),
    path("medicamentos/<int:pk>/editar/",  views.MedicamentoUpdate.as_view(), name="med_editar"),
    path("medicamentos/<int:pk>/excluir/", views.MedicamentoDelete.as_view(), name="med_excluir"),

    # Produto Diverso
    path("produtos/",                  views.ProdutoDiversoList.as_view(),   name="prod_listar"),
    path("produtos/novo/",             views.ProdutoDiversoCreate.as_view(), name="prod_novo"),
    path("produtos/<int:pk>/editar/",  views.ProdutoDiversoUpdate.as_view(), name="prod_editar"),
    path("produtos/<int:pk>/excluir/", views.ProdutoDiversoDelete.as_view(), name="prod_excluir"),

    # Usuários
    path("usuarios/",                  views.UsuarioList.as_view(),   name="usr_listar"),
    path("usuarios/novo/",             views.UsuarioCreate.as_view(), name="usr_novo"),
    path("usuarios/<int:pk>/editar/",  views.UsuarioUpdate.as_view(), name="usr_editar"),
    path("usuarios/<int:pk>/excluir/", views.UsuarioDelete.as_view(), name="usr_excluir"),

    # Grupos
    path("grupos/",                  views.GrupoList.as_view(),   name="grp_listar"),
    path("grupos/novo/",             views.GrupoCreate.as_view(), name="grp_novo"),
    path("grupos/<int:pk>/editar/",  views.GrupoUpdate.as_view(), name="grp_editar"),
    path("grupos/<int:pk>/excluir/", views.GrupoDelete.as_view(), name="grp_excluir"),
]