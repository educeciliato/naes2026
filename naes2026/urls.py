from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # Website (páginas públicas + auth)
    path('', include('website.urls')),

    # Farmácia (dashboard e CRUDs)
    path('farmacia/', include('farmacia.urls')),

    # IA (única porta de entrada) e assistente virtual
    path('ia/', include('ia.urls')),
    path('assistente/', include('assistente.urls')),

    # Alteração de senha (views built-in do Django)
    path('senha/alterar/',
         auth_views.PasswordChangeView.as_view(
             template_name='website/senha_alterar.html',
             success_url='/senha/alterada/'
         ),
         name='password_change'),
    path('senha/alterada/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='website/senha_alterada.html'
         ),
         name='password_change_done'),
]

# Debug Toolbar só existe quando está instalada (DEBUG=True e fora dos testes).
if 'debug_toolbar' in settings.INSTALLED_APPS:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
