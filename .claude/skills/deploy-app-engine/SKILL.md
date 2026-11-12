---
name: deploy-app-engine
description: Use ao preparar, revisar ou depurar o deploy do PharmaSys no Google App Engine Standard (python312) com Postgres no Neon — variáveis de ambiente, collectstatic, migrate e smoke test, sem expor segredos.
---

## Regras

- **Agentes não executam deploy nem `migrate` no Neon sem pedido explícito.**
  Prepare os arquivos e entregue os comandos.
- Nunca imprima nem commite `app.yaml` (tem `SECRET_KEY`, `DATABASE_URL`,
  `GEMINI_API_KEY`). O modelo versionado é `app.yaml.example`.

## Checklist antes do deploy

1. `python manage.py check --deploy` com `DEBUG=False` (avisos de HSTS são aceitáveis).
2. `python manage.py test` — tudo verde.
3. `python manage.py makemigrations --check --dry-run` — nada pendente.
4. `app.yaml` tem em `env_variables`: `DEBUG: "False"`, `SECRET_KEY`,
   `DATABASE_URL`, `GEMINI_API_KEY`, `CSRF_TRUSTED_ORIGINS` (URL https do app).
5. `requirements.txt` com versões fixas e com tudo que o código importa.

## Passo a passo

```powershell
gcloud auth login
gcloud config set project <ID_DO_PROJETO>

# 1. Estáticos: o app.yaml serve /static a partir de static_gcloud/
python manage.py collectstatic --noinput

# 2. Migrations no Neon (DATABASE_URL de produção no .env ou na sessão)
python manage.py migrate

# 3. Deploy
gcloud app deploy app.yaml --quiet
gcloud app browse        # mostra a URL; coloque-a em CSRF_TRUSTED_ORIGINS
```

## Smoke test (depois de cada deploy)

- `/` abre com o CSS (se vier sem estilo: faltou `collectstatic` ou o handler `/static`).
- Login → dashboard; criar, editar e excluir um laboratório (mensagens aparecem).
- Lista de medicamentos com filtro + página 2 mantendo o filtro.
- **IA → Configuração**: "Chave configurada: Sim" e **Testar conexão** OK.
- **Assistente**: uma pergunta responde; aparece em **IA → Requisições**.
- `gcloud app logs tail -s default` sem `Traceback`.

## Problemas comuns

| Sintoma | Causa provável |
| --- | --- |
| `ImproperlyConfigured: Defina a variável de ambiente SECRET_KEY` | falta `SECRET_KEY` no `app.yaml` |
| 403 CSRF no login | `CSRF_TRUSTED_ORIGINS` sem a URL `https://...appspot.com` |
| Página sem CSS | `static_gcloud/` não gerado antes do deploy |
| "A IA não está configurada no servidor" | `GEMINI_API_KEY` vazio no `app.yaml` |
| `relation "ia_configuracaoia" does not exist` | faltou `migrate` no Neon |
| Loop de redirecionamento | `SECURE_PROXY_SSL_HEADER` (já configurado no settings) |
