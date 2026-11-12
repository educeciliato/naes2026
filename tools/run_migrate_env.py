import os
import sys

# Inserir o diretório do projeto no sys.path para garantir que o pacote 'naes2026' seja encontrado
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# A DATABASE_URL vem do ambiente ou do .env (carregado pelo settings).
# Nunca escreva a URL do banco aqui: ela contém usuário e senha.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naes2026.settings')

from django import setup as django_setup
from django.core.management import call_command

if __name__ == '__main__':
    django_setup()
    call_command('migrate')
