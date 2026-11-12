"""
Settings do PharmaSys (projeto naes2026).

Tudo que é segredo ou muda entre ambientes vem de variáveis de ambiente:
localmente do arquivo ``.env`` (python-dotenv, fora do Git) e, no App Engine,
do ``env_variables`` do ``app.yaml``. Veja ``.env.example`` e AGENTS.md.
"""
import os
import sys
from pathlib import Path

from django.contrib.messages import constants as message_constants
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# True durante "manage.py test": desliga a Debug Toolbar, usa SQLite em
# memória e zera a chave do Gemini (nenhum teste acessa a internet).
TESTANDO = len(sys.argv) > 1 and sys.argv[1] == 'test'

CHAVE_DESENVOLVIMENTO = 'django-insecure-dev-only-key-change-in-production'
SECRET_KEY = os.environ.get('SECRET_KEY', CHAVE_DESENVOLVIMENTO)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

if not DEBUG and SECRET_KEY == CHAVE_DESENVOLVIMENTO:
    # A chave de desenvolvimento está no código (é pública): em produção ela
    # permitiria forjar sessões e tokens CSRF.
    raise ImproperlyConfigured('Defina a variável de ambiente SECRET_KEY (obrigatória com DEBUG=False).')

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '*').split(',') if h.strip()]

# Origens confiáveis para o CSRF. Ex.: https://meu-projeto.rj.r.appspot.com
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]

if not DEBUG:
    # O App Engine termina o HTTPS no balanceador e repassa em HTTP com o
    # cabeçalho X-Forwarded-Proto.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r'^_ah/']  # requisições internas do App Engine


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'website.apps.WebsiteConfig',
    'farmacia.apps.FarmaciaConfig',
    'ia.apps.IaConfig',
    'assistente.apps.AssistenteConfig',

    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Django Debug Toolbar — só em desenvolvimento (DEBUG=True) e fora dos testes.
# Em produção (App Engine, DEBUG=False) ela nem é instalada.
if DEBUG and not TESTANDO:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'naes2026.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'farmacia.context_processors.permissoes',
            ],
        },
    },
]

WSGI_APPLICATION = 'naes2026.wsgi.application'


# Banco: DATABASE_URL (Postgres no Neon) ou, se vazio, SQLite local.
# Nunca escreva a URL do banco no código: ela tem usuário e senha.
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if TESTANDO:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
elif DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

if TESTANDO:
    # PBKDF2 é lento de propósito; nos testes só deixaria a suíte devagar.
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Para onde o Django redireciona usuários não autenticados
LOGIN_URL = '/login/'
# Para onde vai após login bem-sucedido (se não houver ?next=)
LOGIN_REDIRECT_URL = '/farmacia/'
# Para onde vai após logout
LOGOUT_REDIRECT_URL = '/'


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# Arquivos estáticos. "collectstatic" gera static_gcloud/, que o app.yaml
# serve direto pelo App Engine (handler /static).
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static_gcloud'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# O Bootstrap usa "danger" (e não "error") para a cor vermelha dos alertas.
MESSAGE_TAGS = {message_constants.ERROR: 'danger'}


# ---------------------------------------------------------------------------
# IA generativa — Google Gemini (google-genai). Ver app "ia" e a skill
# integracao-ia. A chave vem SEMPRE do ambiente; modelo, temperatura, limite
# de tokens, timeout e cota ficam na ConfiguracaoIA (banco, editável em tela).
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
# Opcional: Gemini pela identidade de serviço do App Engine (Vertex AI), sem API Key.
GEMINI_USAR_VERTEX = os.environ.get('GEMINI_USAR_VERTEX', 'False') == 'True'
GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
GOOGLE_CLOUD_LOCATION = os.environ.get('GOOGLE_CLOUD_LOCATION', 'global')

# Só para a ESTIMATIVA de custo mostrada em Requisições da IA.
GEMINI_PRECO_ENTRADA_USD = 0.10 / 1_000_000   # por token de entrada
GEMINI_PRECO_SAIDA_USD = 0.40 / 1_000_000     # por token de saída
GEMINI_COTACAO_BRL = 5.50

if TESTANDO:
    # Nenhum teste pode chamar a API de verdade, mesmo que o .env tenha a chave.
    GEMINI_API_KEY = ''
    GEMINI_USAR_VERTEX = False


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {
        'ia': {'handlers': ['console'], 'level': 'INFO'},
    },
}
