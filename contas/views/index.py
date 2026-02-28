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

    competencia, mes, ano = competencia_service.get_competencia_atual(request)

    lancamentos = lancamento_service.get_all_lancamentos_por_competencia(competencia)

    cartoes = (
        Cartao.objects
        .prefetch_related(
            Prefetch(
                "fatura_set",
                queryset=Fatura.objects.filter(competencia=competencia)
                .prefetch_related(  # ✅ carrega lançamentos junto
                    Prefetch(
                        "lancamento_set",
                        queryset=Lancamento.objects.filter(natureza=Lancamento.Natureza.DESPESA),
                        to_attr="despesas"
                    )
                ),
                to_attr="faturas_competencia"
            )
        )
    )

    total_cartoes = 0

    for c in cartoes:
        fatura = c.faturas_competencia[0] if c.faturas_competencia else None
        c.fatura = fatura
        # ✅ soma em Python, sem query
        c.valor_fatura = sum(l.valor for l in fatura.despesas) if fatura else 0
        total_cartoes += c.valor_fatura

    totais = competencia_service.get_totais_competencia(competencia, total_cartoes)

    return render(request, 'contas/home.html', {
        'competencia': competencia,
        'lancamentos': lancamentos,
        'anterior': competencia_service.anterior(mes, ano),
        'proximo': competencia_service.proximo(mes, ano),
        'receitas_previstas': totais['receitas_previstas'],
        'despesas_previstas': totais['despesas_previstas'],
        'receitas_realizadas': totais['receitas_realizadas'],
        'despesas_realizadas': totais['despesas_realizadas'],
        'saldo_previsto': totais['receitas_previstas'] - totais['despesas_previstas'],
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







