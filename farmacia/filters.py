"""FilterSets (django-filter) das listagens.

As opções de chave estrangeira (ex.: laboratório) mostram só os registros do
usuário logado: o ``queryset`` é uma função que recebe o ``request``.
"""
from datetime import timedelta

import django_filters
from django import forms
from django.utils import timezone

from .models import Distribuidora, Farmacia, Laboratorio, Medicamento, ProdutoDiverso

SIM_NAO = forms.Select(choices=[('', 'Todos'), ('true', 'Sim'), ('false', 'Não')])
ATIVO = forms.Select(choices=[('', 'Todos'), ('true', 'Ativo'), ('false', 'Inativo')])
DIAS_A_VENCER = 30


def _do_usuario(modelo):
    def queryset(request):
        if request is None:
            return modelo.objects.none()
        return modelo.objects.filter(cadastrado_por=request.user).order_by('nome')
    return queryset


class MedicamentoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains', label='Nome contém')
    lote = django_filters.CharFilter(lookup_expr='icontains', label='Lote')
    laboratorio = django_filters.ModelChoiceFilter(
        queryset=_do_usuario(Laboratorio), label='Laboratório', empty_label='Todos')
    distribuidora = django_filters.ModelChoiceFilter(
        queryset=_do_usuario(Distribuidora), label='Distribuidora', empty_label='Todas')
    controlado = django_filters.BooleanFilter(label='Controlado', widget=SIM_NAO)
    situacao = django_filters.ChoiceFilter(
        label='Validade', method='filtrar_situacao', empty_label='Todas',
        choices=[('vencido', 'Vencido'), ('a_vencer', f'Vence em {DIAS_A_VENCER} dias'), ('valido', 'No prazo')],
    )

    class Meta:
        model = Medicamento
        fields = []

    def filtrar_situacao(self, queryset, name, value):
        hoje = timezone.localdate()
        limite = hoje + timedelta(days=DIAS_A_VENCER)
        if value == 'vencido':
            return queryset.filter(data_validade__lt=hoje)
        if value == 'a_vencer':
            return queryset.filter(data_validade__gte=hoje, data_validade__lte=limite)
        if value == 'valido':
            return queryset.filter(data_validade__gte=hoje)
        return queryset


class ProdutoDiversoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains', label='Nome contém')
    categoria = django_filters.CharFilter(lookup_expr='icontains', label='Categoria')
    preco_min = django_filters.NumberFilter(field_name='preco', lookup_expr='gte', label='Preço mínimo')
    preco_max = django_filters.NumberFilter(field_name='preco', lookup_expr='lte', label='Preço máximo')
    ativo = django_filters.BooleanFilter(label='Status', widget=ATIVO)

    class Meta:
        model = ProdutoDiverso
        fields = []


class LaboratorioFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains', label='Nome contém')
    ativo = django_filters.BooleanFilter(label='Status', widget=ATIVO)

    class Meta:
        model = Laboratorio
        fields = []


class DistribuidoraFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains', label='Nome contém')
    cnpj = django_filters.CharFilter(lookup_expr='icontains', label='CNPJ')
    ativo = django_filters.BooleanFilter(label='Status', widget=ATIVO)

    class Meta:
        model = Distribuidora
        fields = []


class FarmaciaFilter(django_filters.FilterSet):
    nome_proprietario = django_filters.CharFilter(lookup_expr='icontains', label='Proprietário')
    cidade = django_filters.CharFilter(lookup_expr='icontains', label='Cidade')
    estado = django_filters.CharFilter(lookup_expr='iexact', label='UF')

    class Meta:
        model = Farmacia
        fields = []
