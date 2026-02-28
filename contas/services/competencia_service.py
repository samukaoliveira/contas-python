from datetime import date
import calendar
from contas.models import Competencia, Lancamento
from contas.services import lancamento_service, cartao_service, fatura_service
from decimal import Decimal
from django.db.models.functions import Coalesce
from django.db.models import Sum

def obter_ou_criar_competencia(mes=None, ano=None):
    hoje = date.today()

    mes = mes or hoje.month
    ano = ano or hoje.year

    competencia, _ = Competencia.objects.get_or_create(
        mes=mes,
        ano=ano
    )

    return competencia


def anterior(mes, ano):
    mes = int(mes) if mes else 1
    ano = int(ano) if ano else 1
    
    if mes == 1:
        return {"mes": 12, "ano": ano - 1}
    return {"mes": mes - 1, "ano": ano}


def proximo(mes, ano):
    mes = int(mes) if mes else 1
    ano = int(ano) if ano else 1
    
    if mes == 12:
        return {"mes": 1, "ano": ano + 1}
    return {"mes": mes + 1, "ano": ano}


def total_receitas_previstas(competencia):
    lancamentos = lancamento_service.get_receitas_competencia(competencia)

    return soma_lancamentos(lancamentos)


def total_despesas_previstas(competencia):

    saldo_cartoes = saldo_todos_os_cartoes(competencia) or Decimal("0.00")

    return total_despesas_sem_cartao(competencia) - calcula_rotativo(saldo_cartoes)


def total_receitas_realizadas(competencia):

    lancamentos = lancamento_service.get_receitas_competencia(competencia).filter(pago = True)

    return soma_lancamentos(lancamentos)


def total_despesas_realizadas(competencia):
    lancamentos = lancamento_service.get_despesas_competencia(competencia).filter(pago = True)

    return soma_lancamentos(lancamentos)


def soma_lancamentos(lancamentos):
    soma = 0
    for l in lancamentos:
        soma += l.valor

    return soma


def saldo_previsto(competencia):
    total_sem_cartao = total_receitas_sem_cartao(competencia) - total_despesas_sem_cartao(competencia)
    saldo_cartoes = saldo_todos_os_cartoes(competencia) or Decimal("0.00")
    
   
    return (total_sem_cartao or Decimal("0.00")) + calcula_rotativo(saldo_cartoes)



def total_receitas_sem_cartao(competencia):
    lancamentos = lancamento_service.get_receitas_competencia(competencia).filter(
        fatura__isnull=True
    )

    return soma_lancamentos(lancamentos)


def total_despesas_sem_cartao(competencia):
    lancamentos = lancamento_service.get_despesas_competencia(competencia).filter(
        fatura__isnull=True
    )



    return soma_lancamentos(lancamentos)

def saldo_todos_os_cartoes(competencia):
    faturas = fatura_service.gera_faturas_por_competencia(competencia)
    soma = 0
    for f in faturas:
        soma += fatura_service.calcular_despesas_fatura(f) or Decimal("0.00")

    return soma


def calcula_rotativo(saldo_cartoes):
    if saldo_cartoes > 0:
        rotativo = 0
    else:
        rotativo = saldo_cartoes

    return rotativo

def ultimo_dia_competencia(competencia):
    return date(
        competencia.ano,
        competencia.mes,
        calendar.monthrange(competencia.ano, competencia.mes)[1]
    )


def get_competencia_atual(request):

    hoje = date.today()
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    mes = int(mes) if mes else hoje.month
    ano = int(ano) if ano else hoje.year

    return obter_ou_criar_competencia(mes=mes, ano=ano), mes, ano


def get_totais_competencia(competencia, total_cartoes):
    """Uma query só para todos os totais da competência."""
    from django.db.models import Q
    totais = Lancamento.objects.filter(
        data__month=competencia.mes,
        data__year=competencia.ano,
        fatura__isnull=True
    ).aggregate(
        receitas_previstas=Coalesce(Sum('valor', filter=Q(natureza='RECEITA') | Q(is_pagamento_fatura=True)), Decimal('0')),
        despesas_previstas=Coalesce(Sum('valor', filter=Q(natureza='DESPESA')), Decimal('0')),
        receitas_realizadas=Coalesce(Sum('valor', filter=Q(natureza='RECEITA', pago=True)), Decimal('0')),
        despesas_realizadas=Coalesce(Sum('valor', filter=Q(natureza='DESPESA', pago=True)), Decimal('0')),
    )

    totais['despesas_previstas'] += total_cartoes
        
    return totais