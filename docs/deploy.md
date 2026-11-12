# Deploy no Google App Engine

Ambiente: App Engine Standard, runtime `python312`, banco Postgres no Neon.
Resumo para agentes na skill `.claude/skills/deploy-app-engine`.

## 1. Pré-requisitos

- Google Cloud SDK instalado (`gcloud --version`) e projeto com App Engine criado.
- Banco Postgres (Neon) e a URL de conexão.
- Chave do Gemini criada em https://aistudio.google.com/apikey.

## 2. app.yaml (fora do Git)

```powershell
Copy-Item app.yaml.example app.yaml   # se ainda não existir
```

Preencha em `env_variables`:

| Variável | Valor |
| --- | --- |
| `DEBUG` | `"False"` |
| `SECRET_KEY` | `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DATABASE_URL` | URL do Neon |
| `GEMINI_API_KEY` | chave do AI Studio |
| `CSRF_TRUSTED_ORIGINS` | `https://<projeto>.<região>.r.appspot.com` |

## 3. Publicar

```powershell
gcloud auth login
gcloud config set project <ID_DO_PROJETO>

python manage.py test                        # tudo verde
python manage.py collectstatic --noinput     # gera static_gcloud/
python manage.py migrate                     # com o DATABASE_URL do Neon no .env
gcloud app deploy app.yaml --quiet
gcloud app browse                            # abre o site e mostra a URL
```

Depois do primeiro deploy, coloque a URL em `CSRF_TRUSTED_ORIGINS` e publique de novo.

## 4. Smoke test

1. A página inicial abre com o CSS.
2. Login → Dashboard.
3. Cadastrar, editar e excluir um laboratório (mensagens aparecem).
4. Lista de medicamentos: filtrar e ir para a página 2 (filtro continua).
5. IA → Configuração: "Chave configurada: Sim" e **Testar conexão** OK.
6. Assistente: fazer uma pergunta; ela aparece em IA → Requisições.

## 5. Segurança

- Até esta versão, a URL do Neon (com senha) estava escrita no
  `settings.py` e no `app.yaml` versionados. Ela foi removida do código, mas
  **continua no histórico do Git**: troque a senha do usuário do banco no
  painel do Neon e atualize o `.env` e o `app.yaml`.
- `app.yaml`, `.env` e `db.sqlite3` não são versionados (`.gitignore`).

## Link de acesso

Preencha após o deploy: `https://<projeto>.<região>.r.appspot.com`
