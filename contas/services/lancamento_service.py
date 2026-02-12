from datetime import date
from contas.models import Lancamento
from contas.views.lancamento_form import LancamentoForm
from contas.services import competencia_service, lancamento_service
from django.db.models import Q

def base_lancamentos_competencia(competencia):
    return Lancamento.objects.filter(
        Q(data__month=competencia.mes, data__year=competencia.ano) |
        Q(fixo=Lancamento.Fixo.FIXO),
        fatura__isnull=True
    )


def get_lancamentos(competencia):
    return Lancamento.objects.filter(
            data__month = competencia.mes,
            data__year = competencia.ano)

def get_lancamentos_por_fatura(fatura):
    return Lancamento.objects.filter(
            fatura = fatura)


def get_despesas_competencia(competencia):
    return get_all_lancamentos_por_competencia(competencia).filter(natureza = Lancamento.Natureza.DESPESA)


def get_receitas_competencia(competencia):
    return get_all_lancamentos_por_competencia(competencia).filter(natureza = Lancamento.Natureza.RECEITA)


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


def get_all_lancamentos_por_competencia(competencia):


    return Lancamento.objects.filter(
        (
            Q(data__month=competencia.mes, data__year=competencia.ano)
        ),
        fatura__isnull=True
    )


def get_lancamentos_fixos():

    return Lancamento.objects.filter(
        fixo = Lancamento.Fixo.FIXO
    )


def salva_lancamento(lancamento):
    lancamento.save()


def cria_lancamentos_fixos(lancamento):

    lancamento_service.salva_lancamento(lancamento)

    mes_atual = lancamento.data.month
    ano = lancamento.data.year
    ano_atual = ano

    while ano_atual == ano:

        proximo = competencia_service.proximo(mes_atual, ano)

        lancamento.data = date(
            proximo['ano'],
            proximo['mes'],
            lancamento.data.day
        )

        lancamento_service.salva_lancamento(lancamento)

        mes_atual = proximo['mes']
        ano_atual = proximo['ano']


    