"""
Settings para rodar os testes com SQLite em memória.

O settings.py já detecta "manage.py test" e faz o mesmo; este arquivo continua
existindo para quem roda: python manage.py test --settings=naes2026.settings_test
"""
from naes2026.settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']  # noqa: F405
MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]  # noqa: F405
GEMINI_API_KEY = ''
GEMINI_USAR_VERTEX = False
