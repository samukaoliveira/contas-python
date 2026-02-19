from django.shortcuts import redirect, render
from contas.services import competencia_service, fatura_service, lancamento_service
from datetime import date
from contas.models import Lancamento, Cartao, Fatura
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Prefetch, Sum, Case, When, F, DecimalField, ExpressionWrapper


@login_required
def home(request):
    hoje = date.today()
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    competencia = competencia_service.obter_ou_criar_competencia(
        mes=int(mes) if mes else hoje.month,
        ano=int(ano) if ano else hoje.year
    )

    lancamentos = lancamento_service.get_all_lancamentos_por_competencia(competencia)

    cartoes = (
        Cartao.objects
        .prefetch_related(
            Prefetch(
                "fatura_set",
                queryset=Fatura.objects.filter(competencia=competencia),
                to_attr="faturas_competencia"
            )
        )
    )

    for c in cartoes:
        fatura = c.faturas_competencia[0] if c.faturas_competencia else None
        c.fatura = fatura

        if fatura:
            total = fatura_service.calcular_despesas_fatura(fatura)
            c.valor_fatura = total
        else:
            c.valor_fatura = 0

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
        'titulo': f"<span class='titulo'>Lançamentos </span><span> { competencia.mes_nome() }/{ competencia.ano }</span>",
        'titulo_tem_setas': True
    })


def health_check(request):

    return HttpResponse("OK", status=200)







