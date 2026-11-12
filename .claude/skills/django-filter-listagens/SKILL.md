---
name: django-filter-listagens
description: Use ao criar ou alterar uma listagem com filtros e paginação — FilterSet do django-filter, FilterView com paginate_by, formulário _filtro.html e paginação _paginacao.html com a templatetag url_com_parametros, que preserva os filtros na troca de página.
---

## Peças

| Peça | Onde |
| --- | --- |
| FilterSet | `<app>/filters.py` |
| View | `FilterView` (ou `farmacia.views.DonoListView`) com `filterset_class`, `paginate_by`, `ordering` |
| Form de filtros | `{% include "website/_filtro.html" %}` (GET, colapsável, badge de filtros ativos) |
| Paginação | `{% include "website/_paginacao.html" %}` |
| Templatetag | `website/templatetags/url_params.py`: `url_com_parametros`, `paginas_proximas`, `filtros_ativos` |

## 1. FilterSet

```python
class MedicamentoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains', label='Nome contém')
    laboratorio = django_filters.ModelChoiceFilter(
        queryset=_do_usuario(Laboratorio), label='Laboratório', empty_label='Todos')
    controlado = django_filters.BooleanFilter(label='Controlado', widget=SIM_NAO)

    class Meta:
        model = Medicamento
        fields = []   # declare tudo explicitamente (labels em português)
```

- **FK com dono:** `queryset` é uma função que recebe o `request`
  (`_do_usuario(Modelo)`); nunca `Modelo.objects.all()` — vazaria nomes de
  registros de outros usuários nas opções.
- Booleanos: `BooleanFilter` com `forms.Select` de choices `('', 'Todos'),
  ('true', 'Sim'), ('false', 'Não')`.
- Regras compostas (ex.: "vence em 30 dias"): `ChoiceFilter(method='...')`.
- Datas de `DateTimeField`: `lookup_expr='date__gte'` / `'date__lte'`.

## 2. View

```python
class MedicamentoList(DonoListView):
    model = Medicamento
    filterset_class = MedicamentoFilter
    template_name = 'website/medicamento.html'
    context_object_name = 'meds'
    relacionados = ('laboratorio', 'distribuidora')  # select_related do que a tabela mostra
```

`DonoListView` já tem `paginate_by = 10` e `ordering = ['-cadastrado_em']`.
Fora do domínio com dono, use `django_filters.views.FilterView` direto.

## 3. Paginação que preserva a busca

Nunca escreva `href="?page={{ n }}"`: isso apaga os filtros. Use:

```django
{% load url_params %}
<a href="{% url_com_parametros page=page_obj.next_page_number %}">Próxima</a>
{# -> ?nome=dipirona&controlado=true&page=3 #}
{% url_com_parametros page=None %}   {# remove a página e mantém os filtros #}
```

O `_paginacao.html` já faz isso (primeira, anterior, números com reticências,
próxima, última) e só aparece quando `is_paginated`.

## 4. Template

```django
{% include "website/_filtro.html" %}
<table>...{% empty %}
  {% if filter.is_bound and filter.data %}Nenhum registro com esses filtros.{% else %}Nada cadastrado.{% endif %}
</table>
{% include "website/_paginacao.html" %}
```

## DataTables x django-filter

- Lista paginada no servidor → **django-filter** (DataTables só veria a página atual).
- Tabela que mostra tudo de uma vez (ex.: IA por usuário) → classe
  `table-datatable` (inicializada em `static/js/site.js`).

## Testes

```python
r = self.client.get(url, {'nome': 'dipirona'})
self.assertContains(r, 'href="?nome=dipirona&amp;page=2" rel="next"')
```

Teste também: cada filtro isolado, opções de FK só do usuário e que a
quantidade de queries não cresce com o número de linhas
(`farmacia/test_requisitos.py`: `FiltrosEPaginacaoTest`, `ConsultasTest`).
