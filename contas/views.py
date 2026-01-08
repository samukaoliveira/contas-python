from django.shortcuts import render
from django.http import HttpResponse
from contas.services.competencia_service import obter_competencia_atual
from contas.models import Lancamento

def home(request):
    competencia = obter_competencia_atual()

    lancamentos = Lancamento.objects.filter(
        data__month=competencia.mes,
        data__year=competencia.ano
    ).order_by('data')

    return render(
        request,
        'contas/home.html',
        {
            'competencia': competencia,
            'lancamentos': lancamentos
        }
    )


def proxima_competencia_view(request):
    atual = obter_competencia_atual()
    proxima_data = date(atual.ano, atual.mes, 1) + relativedelta(months=1)

    competencia, _ = Competencia.objects.get_or_create(
        mes=proxima_data.month,
        ano=proxima_data.year
    )

    return redirect('home_por_competencia', competencia_id=competencia.id)
