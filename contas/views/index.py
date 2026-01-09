from django.shortcuts import redirect, render
from contas.services import competencia_service
from datetime import date
from contas.models import Lancamento

def home(request):
    hoje = date.today()
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    competencia = competencia_service.obter_ou_criar_competencia(
        mes=int(mes) if mes else hoje.month,
        ano=int(ano) if ano else hoje.year
    )

    lancamentos = Lancamento.objects.filter(
        data__month=competencia.mes,
        data__year=competencia.ano
    )

    return render(request, 'contas/home.html', {
        'competencia': competencia,
        'lancamentos': lancamentos,
        'anterior': competencia_service.anterior(mes, ano),
        'proximo': competencia_service.proximo(mes, ano)
    })


def competencia_anterior(request):
    request.GET.get



