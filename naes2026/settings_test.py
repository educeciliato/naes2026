"""
Settings override para rodar testes locais com SQLite.
Uso: python manage.py test --settings=naes2026.settings_test
"""
from naes2026.settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Desabilita debug toolbar nos testes
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]

# URL conf sem debug toolbar
ROOT_URLCONF = 'naes2026.urls_test'
