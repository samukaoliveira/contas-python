def get_dashboard_data(user):
    from contas.services import competencia_service, lancamento_service
    from contas.models import Lancamento, Cartao, Fatura
    from django.db.models import Prefetch, Q, Sum
    from django.db.models.functions import Coalesce
    from datetime import date
    from decimal import Decimal

    competencia, mes, ano = competencia_service.get_competencia_atual(user)

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

    total_cartoes = Decimal('0')
    cartoes_data = []

    for c in cartoes:
        fatura = c.faturas_competencia[0] if c.faturas_competencia else None
        valor_fatura = sum(l.valor for l in fatura.despesas) if fatura else Decimal('0')

        total_cartoes += valor_fatura

        cartoes_data.append({
            "id": c.id,
            "descricao": c.descricao,
            "vencimento": c.vencimento,
            "valor_fatura": valor_fatura,
        })

    totais_mes = Lancamento.objects.filter(
        data__month=competencia.mes,
        data__year=competencia.ano
    ).aggregate(
        receitas=Coalesce(Sum('valor', filter=Q(natureza='RECEITA', is_pagamento_fatura=False)), Decimal('0')),
        despesas=Coalesce(Sum('valor', filter=Q(natureza='DESPESA', fatura__isnull=True)), Decimal('0')),
        receitas_realizadas=Coalesce(Sum('valor', filter=Q(natureza='RECEITA', pago=True, is_pagamento_fatura=False)), Decimal('0')),
        despesas_realizadas=Coalesce(
            Sum('valor', filter=Q(natureza='DESPESA', pago=True) |
                              Q(natureza='RECEITA', pago=True, is_pagamento_fatura=True)),
            Decimal('0')
        ),
    )

    totais_mes['despesas'] += total_cartoes

    primeiro_dia_mes = date(competencia.ano, competencia.mes, 1)

    saldo_anterior = Lancamento.objects.filter(
        data__lt=primeiro_dia_mes
    ).aggregate(
        receitas_realizadas=Coalesce(Sum('valor', filter=Q(natureza='RECEITA', pago=True, is_pagamento_fatura=False)), Decimal('0')),
        despesas_realizadas=Coalesce(
            Sum('valor', filter=Q(natureza='DESPESA', pago=True) |
                              Q(natureza='RECEITA', pago=True, is_pagamento_fatura=True)),
            Decimal('0')
        ),
    )

    saldo_anterior_valor = (
        saldo_anterior['receitas_realizadas']
        - saldo_anterior['despesas_realizadas']
    )

    saldo_previsto = (
        totais_mes['receitas']
        - totais_mes['despesas']
        + saldo_anterior_valor
    )

    saldo_em_caixa = lancamento_service.saldo_em_caixa()

    return {
        "competencia": competencia,
        "lancamentos": lancamentos,
        "cartoes": cartoes_data,
        "totais": totais_mes,
        "saldos": {
            "saldo_previsto": saldo_previsto,
            "saldo_em_caixa": saldo_em_caixa,
            "saldo_anterior": saldo_anterior_valor,
        }
    }