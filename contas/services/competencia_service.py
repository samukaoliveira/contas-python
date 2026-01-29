from datetime import date
from contas.models import Competencia
from contas.services import lancamento_service, cartao_service, fatura_service
from decimal import Decimal

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
    atual = obter_ou_criar_competencia(mes, ano)

    if atual.mes == 1:
        novo_mes = 12
        novo_ano = atual.ano - 1
    else:
        novo_mes = atual.mes - 1
        novo_ano = atual.ano

    return {
        "mes": novo_mes, 
        "ano": novo_ano
    }


def proximo(mes, ano):
    atual = obter_ou_criar_competencia(mes, ano)

    if atual.mes == 12:
        novo_mes = 1
        novo_ano = atual.ano + 1
    else:
        novo_mes =  atual.mes + 1
        novo_ano = atual.ano

    return {
        "mes": novo_mes, 
        "ano": novo_ano
    }


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
        soma += fatura_service.total_fatura(f) or Decimal("0.00")

    return soma


def calcula_rotativo(saldo_cartoes):
    if saldo_cartoes > 0:
        rotativo = 0
    else:
        rotativo = saldo_cartoes

    return rotativo