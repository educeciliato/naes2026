import os
import sys

# Inserir o diretório do projeto no sys.path para garantir que o pacote 'naes2026' seja encontrado
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Defina aqui a DATABASE_URL (provisório para execução local)
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_FAlIq4RE5LZn@ep-lingering-glade-ac7bddn4-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naes2026.settings')

from django import setup as django_setup
from django.core.management import call_command

if __name__ == '__main__':
    django_setup()
    call_command('migrate')
