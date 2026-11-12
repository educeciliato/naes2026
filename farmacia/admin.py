from django.contrib import admin

from .models import Distribuidora, Farmacia, Laboratorio, Medicamento, ProdutoDiverso


@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'cadastrado_por', 'cadastrado_em']
    list_select_related = ['cadastrado_por']
    search_fields = ['nome']


@admin.register(Distribuidora)
class DistribuidoraAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'ativo', 'cadastrado_por']
    list_select_related = ['cadastrado_por']
    search_fields = ['nome', 'cnpj']


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'lote', 'data_validade', 'controlado', 'laboratorio', 'cadastrado_por']
    list_select_related = ['laboratorio', 'cadastrado_por']
    list_filter = ['controlado']
    search_fields = ['nome', 'lote']


@admin.register(ProdutoDiverso)
class ProdutoDiversoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'preco', 'quantidade', 'ativo', 'cadastrado_por']
    list_select_related = ['cadastrado_por']
    search_fields = ['nome', 'categoria']


@admin.register(Farmacia)
class FarmaciaAdmin(admin.ModelAdmin):
    list_display = ['nome_proprietario', 'cidade', 'estado', 'cnpj', 'cadastrado_por']
    list_select_related = ['cadastrado_por']
