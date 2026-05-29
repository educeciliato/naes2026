from django.urls import path
from . import views
from .views import dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),

    path("laboratorio/",                  views.LaboratorioList.as_view(),   name="laboratorio_listar"),
    path("laboratorio/novo/",             views.LaboratorioCreate.as_view(), name="laboratorio_novo"),
    path("laboratorio/<int:pk>/editar/",  views.LaboratorioUpdate.as_view(), name="laboratorio_editar"),
    path("laboratorio/<int:pk>/excluir/", views.LaboratorioDelete.as_view(), name="laboratorio_excluir"),
    path("laboratorio/<int:pk>/",         views.LaboratorioDetail.as_view(), name="laboratorio_detalhe"),

    path("distribuidora/",                  views.DistribuidoraList.as_view(),   name="distribuidora_listar"),
    path("distribuidora/novo/",             views.DistribuidoraCreate.as_view(), name="distribuidora_novo"),
    path("distribuidora/<int:pk>/editar/",  views.DistribuidoraUpdate.as_view(), name="distribuidora_editar"),
    path("distribuidora/<int:pk>/excluir/", views.DistribuidoraDelete.as_view(), name="distribuidora_excluir"),
    path("distribuidora/<int:pk>/",         views.DistribuidoraDetail.as_view(), name="distribuidora_detalhe"),

    path("medicamento/",                  views.MedicamentoList.as_view(),   name="medicamento_listar"),
    path("medicamento/novo/",             views.MedicamentoCreate.as_view(), name="medicamento_novo"),
    path("medicamento/<int:pk>/editar/",  views.MedicamentoUpdate.as_view(), name="medicamento_editar"),
    path("medicamento/<int:pk>/excluir/", views.MedicamentoDelete.as_view(), name="medicamento_excluir"),
    path("medicamento/<int:pk>/",         views.MedicamentoDetail.as_view(), name="medicamento_detalhe"),

    path("produto/",                  views.ProdutoDiversoList.as_view(),   name="produto_listar"),
    path("produto/novo/",             views.ProdutoDiversoCreate.as_view(), name="produto_novo"),
    path("produto/<int:pk>/editar/",  views.ProdutoDiversoUpdate.as_view(), name="produto_editar"),
    path("produto/<int:pk>/excluir/", views.ProdutoDiversoDelete.as_view(), name="produto_excluir"),
    path("produto/<int:pk>/",         views.ProdutoDiversoDetail.as_view(), name="produto_detalhe"),

    path("usuario/",                  views.UsuarioList.as_view(),   name="usuario_listar"),
    path("usuario/novo/",             views.UsuarioCreate.as_view(), name="usuario_novo"),
    path("usuario/<int:pk>/editar/",  views.UsuarioUpdate.as_view(), name="usuario_editar"),
    path("usuario/<int:pk>/excluir/", views.UsuarioDelete.as_view(), name="usuario_excluir"),
    path("usuario/<int:pk>/",         views.UsuarioDetail.as_view(), name="usuario_detalhe"),

    path("farmacia/",                  views.FarmaciaList.as_view(),   name="farmacia_listar"),
    path("farmacia/novo/",             views.FarmaciaCreate.as_view(), name="farmacia_novo"),
    path("farmacia/<int:pk>/editar/",  views.FarmaciaUpdate.as_view(), name="farmacia_editar"),
    path("farmacia/<int:pk>/excluir/", views.FarmaciaDelete.as_view(), name="farmacia_excluir"),
    path("farmacia/<int:pk>/",         views.FarmaciaDetail.as_view(), name="farmacia_detalhe"),

    path("grupo/",                  views.GrupoList.as_view(),   name="grupo_listar"),
    path("grupo/novo/",             views.GrupoCreate.as_view(), name="grupo_novo"),
    path("grupo/<int:pk>/editar/",  views.GrupoUpdate.as_view(), name="grupo_editar"),
    path("grupo/<int:pk>/excluir/", views.GrupoDelete.as_view(), name="grupo_excluir"),
    path("grupo/<int:pk>/",         views.GrupoDetail.as_view(), name="grupo_detalhe"),
]