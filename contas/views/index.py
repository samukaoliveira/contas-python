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
        data__year=competencia.ano,
        fatura = None
    )

    return render(request, 'contas/home.html', {
        'competencia': competencia,
        'lancamentos': lancamentos,
        'anterior': competencia_service.anterior(mes, ano),
        'proximo': competencia_service.proximo(mes, ano),
        'receitas_previstas': competencia_service.total_receitas_previstas(competencia),
        'despesas_previstas': competencia_service.total_despesas_previstas(competencia),
        'receitas_realizadas': competencia_service.total_receitas_realizadas(competencia),
        'despesas_realizadas': competencia_service.total_despesas_realizadas(competencia),
        'form_action': "lancamentos_create_path",
        'competencia_path': "home_path",
        'pk': None
    })





