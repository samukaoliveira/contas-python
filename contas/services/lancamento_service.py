from datetime import date
from copy import deepcopy
from contas.models import Lancamento
from contas.views.lancamento_form import LancamentoForm
from contas.services import competencia_service, lancamento_service, fatura_service
from django.db.models import Q

def base_lancamentos_competencia(competencia):
    return Lancamento.objects.filter(
        Q(data__month=competencia.mes, data__year=competencia.ano),
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

    lancamento.pk = None
    lancamento_service.salva_lancamento(lancamento)

    mes_atual = lancamento.data.month 
    ano = lancamento.data.year 

    while True:

        proximo = competencia_service.proximo(mes_atual, ano)

        if proximo['ano'] != ano:
            break

        novo_lancamento = Lancamento.objects.get(pk=lancamento.pk)
        novo_lancamento.pk = None
        novo_lancamento.data = date(
            proximo['ano'], 
            proximo['mes'], 
            lancamento.data.day
        )

        lancamento_service.salva_lancamento(novo_lancamento)

        mes_atual = proximo['mes'] 



def cria_lancamentos_fixos_cartao(lancamento):

    lancamento.pk = None
    lancamento_service.salva_lancamento(lancamento)

    mes_atual = lancamento.data.month 
    ano = lancamento.data.year 
    fatura_atual = lancamento.fatura

    while True:

        proximo = competencia_service.proximo(mes_atual, ano)
        nova_fatura = fatura_service.get_proxima_fatura(fatura_atual)

        if proximo['ano'] != ano:
            break

        novo_lancamento = Lancamento.objects.get(pk=lancamento.pk)
        novo_lancamento.pk = None
        novo_lancamento.data = date(
            proximo['ano'], 
            proximo['mes'], 
            lancamento.data.day
        )
        novo_lancamento.fatura = nova_fatura

        lancamento_service.salva_lancamento(novo_lancamento)

        mes_atual = proximo['mes'] 
        fatura_atual = nova_fatura


def cria_lancamentos_parcelados(lancamento):

    mes_atual = lancamento.data.month 
    ano = lancamento.data.year 
    fatura_atual = lancamento.fatura
    qtde_parcelas = lancamento.parcelas
    descricao_inicial = lancamento.descricao
    indice = 2

    lancamento.pk = None
    lancamento.descricao = f"{descricao_inicial} (1/{qtde_parcelas})"
    lancamento_service.salva_lancamento(lancamento)

    while indice <= qtde_parcelas:

        proximo = competencia_service.proximo(mes_atual, ano)
        nova_fatura = None
        if fatura_atual != None:
            nova_fatura = fatura_service.get_proxima_fatura(fatura_atual)

        novo_lancamento = Lancamento.objects.get(pk=lancamento.pk)
        novo_lancamento.pk = None
        novo_lancamento.descricao = f"{descricao_inicial} ({indice}/{qtde_parcelas})"
        novo_lancamento.data = date(
            proximo['ano'], 
            proximo['mes'], 
            lancamento.data.day
        )
        novo_lancamento.fatura = nova_fatura or None

        lancamento_service.salva_lancamento(novo_lancamento)

        mes_atual = proximo['mes'] 
        fatura_atual = nova_fatura

        indice += 1




    