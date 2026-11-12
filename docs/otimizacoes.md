# Otimizações de consultas (Django Debug Toolbar)

A Debug Toolbar fica ativa só em desenvolvimento (`DEBUG=True`, fora dos
testes) — ver `naes2026/settings.py`. Abra qualquer página logado em
`http://127.0.0.1:8000`, clique em **SQL** na barra lateral e procure as
consultas marcadas como **"Similar"/"Duplicated"**: elas indicam o problema
N+1 (uma consulta por linha da tabela).

## O que foi encontrado e corrigido

| Página | Queries repetidas | Causa | Correção |
| --- | --- | --- | --- |
| Medicamentos (`/farmacia/medicamento/`) | 1 `SELECT ... FROM farmacia_laboratorio` por linha | a tabela mostra `{{ m.laboratorio }}` | `select_related('laboratorio', 'distribuidora')` (atributo `relacionados` da view) |
| Dashboard (`/farmacia/`) | 1 laboratório por medicamento do quadro de validade | idem | `select_related('laboratorio')` |
| Grupos (`/farmacia/grupo/`) | 1 `COUNT(*)` de usuários por grupo | template usava `{{ g.user_set.count }}` | `annotate(num_membros=Count('user'))` |
| Usuários (`/farmacia/usuario/`) | 1 consulta de grupos por usuário | nova coluna "Grupos" (`u.groups.all`) | `prefetch_related('groups')` |
| Farmácias (`/farmacia/farmacia/`) | 1 consulta de grupo por linha | coluna "Grupo" | `select_related('grupo')` |
| IA → Requisições | 1 consulta de usuário por linha | coluna "Usuário" | `select_related('usuario')` |
| IA → IA por usuário | consumo e cota calculados por linha | `consumo_do_mes()` por usuário | uma consulta com `annotate` (`Sum` filtrado + `Coalesce`) |
| Detalhe de medicamento/farmácia | consultas das FKs mostradas | lista de campos | `select_related` no `get_queryset` |

Também foi removido o cálculo de listas que o dashboard montava e não exibia
(`ultimos_meds`, `meds_controlados`, `ultimos_prods`).

## Como os testes travam a correção

Em vez de fixar um número de queries (que muda com o middleware), os testes
medem a página com poucos registros e com muitos e exigem **o mesmo número**:

```python
with CaptureQueriesContext(connection) as ctx:
    self.client.get(reverse('medicamento_listar'))
```

Ver `farmacia/test_requisitos.py` (`ConsultasTest`), `ia/tests.py`
(`test_requisicoes_sem_n_mais_1`, `test_ia_por_usuario_numero_de_consultas_nao_cresce`)
e `assistente/tests.py` (`ConsultasAssistenteTest`).
