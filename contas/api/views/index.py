from django.http import JsonResponse
from django.shortcuts import redirect, render
from contas.services import competencia_service, fatura_service, lancamento_service, dashboard_service
from datetime import date
from contas.models import Lancamento, Cartao, Fatura
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Prefetch, Q, Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def home_api(request):
    data = dashboard_service.get_dashboard_data(request)

    return JsonResponse({
        "competencia": {
            "mes": data['competencia'].mes,
            "ano": data['competencia'].ano,
            "mes_nome": data['competencia'].mes_nome(),
        },
        "totais": {
            k: float(v) for k, v in data['totais'].items()
        },
        "saldos": {
            k: float(v) for k, v in data['saldos'].items()
        },
        "cartoes": [
            {
                **c,
                "valor_fatura": float(c["valor_fatura"])
            } for c in data["cartoes"]
        ],
        "lancamentos": [
            {
                "id": l.id,
                "descricao": l.descricao,
                "valor": float(l.valor),
                "natureza": l.natureza,
                "pago": l.pago,
                "data": l.data.strftime("%Y-%m-%d"),
            }
            for l in data["lancamentos"]
        ]
    })