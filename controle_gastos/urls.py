"""
URL configuration for controle_gastos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from contas.views import index, lancamentos, cartoes
from django.views.generic import RedirectView
from controle_gastos import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/home/', permanent=False)),
    path('home/', index.home, name='home_path'),
    path('update/<int:pk>/', lancamentos.update, name='lancamentos_update_path'),
    path('lancamentos/create/', lancamentos.create, name='lancamentos_create_path'),
    path('cartoes/<int:pk>/lancamento/create/', lancamentos.create_cartao, name='cartao_lancamento_create_path'),
    path('cartoes/', cartoes.home, name='cartoes_path'),
    path('cartoes/create/', cartoes.create, name='cartoes_create_path'),
    path('cartoes/<int:pk>/edit/', cartoes.edit, name='cartoes_edit_path'),
    path('cartoes/<int:pk>/', cartoes.show, name='cartao_show_path'),
    path('lancamentos/<int:pk>/delete/', lancamentos.delete, name='lancamentos_delete_path'),
    path('cartoes/pagar_fatura/', cartoes.pagar_fatura, name='pagar_fatura_path'),
    path("accounts/", include("allauth.urls")),
    path("health_check/", index.health_check, name='health_check_path'),
    path('cartoes/lancamento/pagar/', cartoes.pagar_fatura, name='cartao_lancamento_pagar_path'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns


# urls.py
handler404 = "contas.views.errors.erro_404"
handler500 = "contas.views.errors.erro_500"
