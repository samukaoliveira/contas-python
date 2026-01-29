from datetime import date
from contas.models import Lancamento

def get_lancamentos(competencia):
    return Lancamento.objects.filter(
            data__month = competencia.mes,
            data__year = competencia.ano)


def get_despesas_competencia(competencia):
    return get_lancamentos(competencia).filter(natureza = Lancamento.Natureza.DESPESA)


def get_receitas_competencia(competencia):
    return get_lancamentos(competencia).filter(natureza = Lancamento.Natureza.RECEITA)


def todos_lancamentos_pagos():
    return Lancamento.objects.filter(
        pago = True
    )

def todas_receitas_pagas():
    return soma_lancamentos(todos_lancamentos_pagos().filter(
        natureza = Lancamento.Natureza.RECEITA
    ))

def todas_despesas_pagas():
    return soma_lancamentos(todos_lancamentos_pagos().filter(
        natureza = Lancamento.Natureza.DESPESA
    ))

def saldo_em_caixa():
    return todas_receitas_pagas() - todas_despesas_pagas()

def soma_lancamentos(lancamentos):
    soma = 0
    for l in lancamentos:
        soma += l.valor

    return soma