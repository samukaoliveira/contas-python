from django.shortcuts import redirect, render
from contas.services import competencia_service, fatura_service, lancamento_service
from datetime import date
from contas.models import Lancamento, Cartao
from django.urls import reverse

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

    cartoes = Cartao.objects.all()

    for c in cartoes:
        c.fatura = fatura_service.total_fatura_por_cartao(c, competencia)

    return render(request, 'contas/home.html', {
        'competencia': competencia,
        'lancamentos': lancamentos,
        'anterior': competencia_service.anterior(mes, ano),
        'proximo': competencia_service.proximo(mes, ano),
        'receitas_previstas': competencia_service.total_receitas_previstas(competencia),
        'despesas_previstas': competencia_service.total_despesas_previstas(competencia),
        'receitas_realizadas': competencia_service.total_receitas_realizadas(competencia),
        'despesas_realizadas': competencia_service.total_despesas_realizadas(competencia),
        'saldo_previsto': competencia_service.saldo_previsto(competencia),
        'saldo_em_caixa': lancamento_service.saldo_em_caixa(),
        'form_action': "lancamentos_create_path",
        'path': reverse('home_path', args=None),
        'cartao': None,
        'cartoes': cartoes,
        'titulo': f"Lançamentos - { competencia.mes_nome() }/{ competencia.ano }",
        'titulo_tem_setas': True
    })







