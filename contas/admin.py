from django.contrib import admin

from contas.models.app_update import AppUpdate
from .models import *

admin.site.register(Lancamento)
admin.site.register(Cartao)
admin.site.register(Fatura)
admin.site.register(Competencia)


@admin.register(AppUpdate)
class AppUpdateAdmin(admin.ModelAdmin):
    list_display = ('version_name', 'version_code', 'ativo')