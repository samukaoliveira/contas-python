from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from contas.views.lancamentos import *


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_create_lancamento(request):

    form = LancamentoForm(request.data)

    if form.is_valid():
        lancamento = form.save(commit=False)

        salva_por_frequencia(lancamento)

        return Response({
            "message": "Lançamento criado com sucesso"
        }, status=status.HTTP_201_CREATED)

    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_update_lancamento(request, pk):

    lancamento = Lancamento.objects.get(pk=pk)

    form = LancamentoForm(request.data, instance=lancamento)

    if form.is_valid():
        escopo = request.data.get("escopo_update", "um")
        lancamento_editado = form.save(commit=False)

        if escopo == "um" or lancamento.fixo == Lancamento.Fixo.NAO:
            lancamento_editado.save()
        else:
            atualizar_lancamentos_futuros(lancamento, lancamento_editado)

        return Response({"message": "Atualizado com sucesso"})

    return Response(form.errors, status=400)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_delete_lancamento(request, pk):

    lancamento = Lancamento.objects.get(pk=pk)
    lancamento.delete()

    return Response({"message": "Deletado com sucesso"})