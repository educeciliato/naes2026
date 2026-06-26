from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),  # ← debug toolbar

    # Website (páginas públicas + auth)
    path('', include('website.urls')),

    # Farmácia (dashboard e CRUDs)
    path('farmacia/', include('farmacia.urls')),

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