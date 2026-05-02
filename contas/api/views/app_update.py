from django.http import JsonResponse
from django.db import models

from contas.models.app_update import AppUpdate

def app_update(request):
    versao = AppUpdate.objects.filter(ativo=True).order_by('-version_code').first()

    if not versao:
        return JsonResponse({"erro": "Nenhuma versão cadastrada"}, status=404)

    return JsonResponse({
        "versionCode": versao.version_code,
        "versionName": versao.version_name,
        "apkUrl": request.build_absolute_uri(versao.apk_file.url)
    })