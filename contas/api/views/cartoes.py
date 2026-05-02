from django.http import JsonResponse
from contas.services import cartao_service

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def cartao_detalhe_api(request, pk):

    data = cartao_service.get_cartao_detalhe_data(request, pk)

    return JsonResponse({
        "cartao": {
            "id": data["cartao"].id,
            "total_fatura": float(data["total_fatura"]),
            "descricao": data["cartao"].descricao,
            "falta_pagar": float(data["falta_pagar"]),
            "fatura": {
                "id": data["fatura"].id if data["fatura"] else None
            },
        },

        "lancamentos": [
            {
                "id": l.id,
                "descricao": l.descricao,
                "valor": float(l.valor),
                "natureza": l.natureza,
                "pago": l.pago,
                "data": l.data.strftime("%Y-%m-%d"),
                "fatura": l.fatura.id if l.fatura else None
            }
            for l in data["lancamentos"]
        ]
    })