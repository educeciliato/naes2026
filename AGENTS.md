# AGENTS.md — PharmaSys (projeto `naes2026`)

Guia para agentes de código (Claude Code, Copilot, Codex…) e para pessoas que
chegam ao projeto. Leia inteiro antes de alterar qualquer coisa.

## 1. O sistema

Sistema web de **gestão de estoque de farmácia** em Django 5.2. Cada usuário
cadastra os seus Laboratórios, Distribuidoras, Medicamentos, Produtos
Diversos e Farmácias; gerentes administram usuários, grupos e a IA. Há um
**assistente virtual** (Google Gemini) que tira dúvidas sobre o uso do sistema.

Regras de negócio que não podem ser quebradas:

- **Registro tem dono.** Laboratorio, Distribuidora, Medicamento,
  ProdutoDiverso e Farmacia têm `cadastrado_por`. Só o dono lista, vê, edita
  e exclui — **nem staff vê o dos outros**. Registro alheio dá **404**.
- Um Medicamento só pode apontar para Laboratório/Distribuidora do próprio
  dono (o form limita o queryset; `FormDoUsuario`).
- FKs são `PROTECT`: excluir um laboratório com medicamentos vira
  `messages.error`, nunca erro 500.
- Assistente: **sem orientação de saúde** (dosagem, indicação, interação) e
  sem dados de outros usuários no contexto enviado à IA.

Perfis:

| Perfil | Como é identificado | O que faz |
| --- | --- | --- |
| Visitante | não logado | Início, Sobre, Contato, Login |
| Usuário | logado | CRUD dos próprios registros, assistente, "Meu consumo" de IA |
| Gerente | superuser, staff ou grupo `Gerentes` (`farmacia.permissoes.eh_admin`) | + Usuários, Grupos, Requisições/Configuração/IA por usuário |

## 2. Mapa do projeto

```
naes2026/              settings (variáveis de ambiente), urls raiz, wsgi
farmacia/              domínio: models, views (CBVs), forms, filters
  views.py             DonoQuerysetMixin, MensagemCrudMixin, Dono*View (bases dos CRUDs)
  permissoes.py        eh_admin() e AdminRequiredMixin (áreas de gerente)
  filters.py           FilterSets do django-filter (FKs limitadas ao usuário)
  context_processors.py  eh_admin no contexto dos templates (menu)
  tests.py, test_requisitos.py
website/               páginas públicas, login, templates base
  templatetags/url_params.py   url_com_parametros / paginas_proximas (paginação + filtros)
  templates/website/   modelo.html (base), _paginacao.html, _filtro.html, _acoes.html, detalhe.html, form.html
ia/                    ÚNICA porta de entrada para a IA
  services.py          chamar_ia, consumo_do_mes, cota_do_usuario, testar_conexao
  provedores/gemini.py único arquivo que importa o SDK google-genai
  models.py            ConfiguracaoIA (singleton), PerfilIAUsuario, RequisicaoIA (auditoria)
assistente/            assistente virtual (/assistente/)
  contexto_projeto.md  descrição do sistema enviada à IA (+ dados do usuário em contexto.py)
  instrucoes.py        instruções de sistema (limites do assistente)
  services.py          JANELA_HISTORICO = 5 e perguntar()
  formatacao.py        Markdown -> HTML sanitizado (nh3); filtro {{ texto|markdown_seguro }}
static/                css/farma.css, js/site.js (plugins jQuery), js/assistente.js (AJAX)
docs/                  otimizacoes.md (Debug Toolbar), deploy.md (App Engine)
.claude/skills/        skills dos agentes (seção 10)
```

## 3. Comandos (Windows + PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env        # depois preencha os valores no .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver          # http://127.0.0.1:8000 (Debug Toolbar com DEBUG=True)

python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test               # suíte completa, SQLite em memória, sem internet
python manage.py test farmacia.test_requisitos.DonoTest   # uma classe só

python manage.py collectstatic --noinput   # gera static_gcloud/ (deploy)
```

> Atenção: se o `.env` tiver `DATABASE_URL` do Neon, `migrate`/`runserver`
> mexem no banco de **produção**. Para trabalhar isolado, deixe
> `DATABASE_URL=` vazio (SQLite local). Os testes sempre usam SQLite.

## 4. Convenções

- **Idioma:** nomes, mensagens, docstrings e commits em português do Brasil.
- **Views:** class-based views (exceção histórica: `dashboard`, `login_view`).
  Novos CRUDs de registros com dono herdam de `DonoListView`,
  `DonoDetailView`, `DonoCreateView`, `DonoUpdateView`, `DonoDeleteView`.
- **Templates:** estendem `website/modelo.html`, blocos `titulo`,
  `breadcrumb` e `conteudo`; formulários com `{{ form|crispy }}`; título
  `<Página> — PharmaSys`.
- **Mensagens:** toda criação/alteração/exclusão gera `messages.success`
  (`MensagemCrudMixin`); ações e bloqueios usam `messages.error`.
  `MESSAGE_TAGS` mapeia erro para `danger` (Bootstrap).
- **Listas:** `FilterView` + `filterset_class` + `paginate_by = 10`, com
  `{% include "website/_filtro.html" %}` e `{% include "website/_paginacao.html" %}`.
  Nunca escreva `href="?page=N"` à mão: use `{% url_com_parametros page=N %}`.
- **jQuery:** plugins carregados no `modelo.html` (versões fixas) e
  inicializados em `static/js/site.js`: Mask (`.mascara-cnpj`, `.mascara-uf`),
  Bootbox (`<form data-confirmar="...">`) e DataTables (`table.table-datatable`,
  só em tabelas sem paginação no servidor).
- **Commits:** seguir a skill `mensagens-commit`.

## 5. Arquitetura — onde cada coisa mora

- **Segurança de acesso:** a fronteira é o `get_queryset()` filtrado por
  `cadastrado_por=request.user` (`DonoQuerysetMixin`). Área de gerente usa
  `AdminRequiredMixin` (`farmacia/permissoes.py`).
- **Toda chamada de IA passa por `ia.services.chamar_ia`.** O SDK
  (`google.genai`) só pode ser importado em `ia/provedores/gemini.py` — o
  teste `ia.tests.SdkIsoladoTest` varre o código e falha se aparecer em outro lugar.
- **Consultas:** listas usam `select_related` / `prefetch_related` /
  `annotate` (atributo `relacionados` nas `Dono*View`). Testes com
  `CaptureQueriesContext` garantem que a quantidade de queries não cresce
  com o número de linhas (ver `docs/otimizacoes.md`).

## 6. Variáveis de ambiente (só nomes)

| Variável | Para quê |
| --- | --- |
| `SECRET_KEY` | chave do Django (obrigatória com `DEBUG=False`) |
| `DEBUG` | `True` local, `False` em produção |
| `ALLOWED_HOSTS` | hosts aceitos, separados por vírgula |
| `CSRF_TRUSTED_ORIGINS` | origens HTTPS confiáveis, separadas por vírgula |
| `DATABASE_URL` | Postgres (Neon) em produção; vazio = SQLite local |
| `GEMINI_API_KEY` | chave da API do Gemini |
| `GEMINI_USAR_VERTEX`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` | opcionais; Gemini via Vertex AI sem API Key |

Local: `.env` (python-dotenv). Produção: `env_variables` do `app.yaml`.
Modelos: `.env.example` e `app.yaml.example`.

## 7. Política de segredos

- **Nunca** escreva chaves, senhas ou URLs de banco em código, templates,
  testes, documentação, logs ou commits. Tudo vem de `os.environ`.
- Não leia nem imprima o conteúdo de `.env` ou `app.yaml`.
- `.env`, `app.yaml`, `db.sqlite3`, `static_gcloud/` e `staticfiles/` ficam fora do Git.
- A tela de configuração da IA mostra só se a chave **está configurada**, nunca o valor.
- Antes de commitar, confira `git diff --cached` procurando segredos.

## 8. Testes

- Ficam em `<app>/tests.py` ou `<app>/test_*.py`. Funcionalidade nova ganha teste.
- **Nenhum teste acessa a internet.** IA: mock de `ia.provedores.gemini.gerar`.
- Nos testes a `GEMINI_API_KEY` é zerada pelo settings; use
  `@override_settings(GEMINI_API_KEY='chave-de-teste')` para a IA "ligada".
- Acesso por dono: sempre teste que outro usuário recebe 404.
- Rode `check`, `makemigrations --check` e `test` antes de commitar.

## 9. Deploy (resumo)

Google App Engine Standard (python312) + Postgres no Neon. Passo a passo em
`docs/deploy.md` e na skill `deploy-app-engine`. **Agentes não executam
nada contra produção** (deploy, migrate no Neon) sem pedido explícito — só
deixam os comandos prontos.

## 10. Skills disponíveis (`.claude/skills/`)

| Skill | Quando usar |
| --- | --- |
| `mensagens-commit` | ao escrever qualquer mensagem de commit |
| `django-crud-dono` | ao criar CRUD de registros que pertencem ao usuário logado |
| `django-filter-listagens` | ao criar/editar filtros e paginação de uma listagem |
| `integracao-ia` | ao usar IA em qualquer parte do sistema |
| `deploy-app-engine` | ao preparar ou revisar um deploy |
