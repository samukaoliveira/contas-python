from django.shortcuts import redirect, render
from contas.services import competencia_service, fatura_service, lancamento_service
from datetime import date
from contas.models import Lancamento, Cartao, Fatura
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Prefetch, Q, Sum
from django.db.models.functions import Coalesce
from decimal import Decimal


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
                .prefetch_related(
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
        c.valor_fatura = sum(l.valor for l in fatura.despesas) if fatura else 0
        total_cartoes += c.valor_fatura

    totais_mes = Lancamento.objects.filter(
        data__month=competencia.mes,
        data__year=competencia.ano,
        fatura__isnull=True
    ).aggregate(
        receitas=Coalesce(
            Sum('valor', filter=Q(natureza='RECEITA') | Q(is_pagamento_fatura=True)),
            Decimal('0')
        ),
        despesas=Coalesce(
            Sum('valor', filter=Q(natureza='DESPESA')),
            Decimal('0')
        ),
        receitas_realizadas=Coalesce(
            Sum('valor', filter=Q(natureza='RECEITA', pago=True)),
            Decimal('0')
        ),
        despesas_realizadas=Coalesce(
            Sum('valor', filter=Q(natureza='DESPESA', pago=True)),
            Decimal('0')
        ),
    )

    totais_mes['despesas'] += total_cartoes

    primeiro_dia_mes = date(competencia.ano, competencia.mes, 1)

    saldo_anterior = Lancamento.objects.filter(
        data__lt=primeiro_dia_mes,
        fatura__isnull=True
    ).aggregate(
        saldo=Coalesce(
            Sum('valor', filter=Q(natureza='RECEITA') | Q(is_pagamento_fatura=True)),
            Decimal('0')
        ) - Coalesce(
            Sum('valor', filter=Q(natureza='DESPESA')),
            Decimal('0')
        )
    )['saldo']

    saldo_previsto = (
        totais_mes['receitas']
        - totais_mes['despesas']
        + saldo_anterior
    )

    saldo_em_caixa = lancamento_service.saldo_em_caixa()

    return render(request, 'contas/home.html', {
        'competencia': competencia,
        'lancamentos': lancamentos,
        'anterior': competencia_service.anterior(mes, ano),
        'proximo': competencia_service.proximo(mes, ano),

        'receitas_previstas': totais_mes['receitas'],
        'despesas_previstas': totais_mes['despesas'],
        'receitas_realizadas': totais_mes['receitas_realizadas'],
        'despesas_realizadas': totais_mes['despesas_realizadas'],

        'saldo_previsto': saldo_previsto,
        'saldo_em_caixa': saldo_em_caixa,
        'saldo_anterior': saldo_anterior,

        'form_action': "lancamentos_create_path",
        'path': reverse('home_path', args=None),
        'cartao': None,
        'cartoes': cartoes,
        'titulo': f"<span class='titulo'>Lançamentos </span><span> { competencia.mes_nome() }/{ competencia.ano }</span>",
        'titulo_tem_setas': True
    })


def health_check(request):
    return HttpResponse("OK", status=200)