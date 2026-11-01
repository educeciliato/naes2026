"""Settings para rodar servidor local com SQLite (testes de carga)."""
from naes2026.settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_load.sqlite3',
    }
}

INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]
ROOT_URLCONF = 'naes2026.urls_test'
DEBUG = False
ALLOWED_HOSTS = ['*']
