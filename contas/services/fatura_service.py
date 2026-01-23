from datetime import date
from contas.models import Fatura
from contas.services import lancamento_service, competencia_service


def obter_ou_criar_fatura(cartao, competencia):

    fatura, created = Fatura.objects.get_or_create(
        cartao=cartao,
        competencia=competencia
    )

    return fatura


def get_despesas_fatura(fatura):

    lancamentos = lancamento_service.get_despesas_competencia(fatura.competencia)
    
    lancamentos_fatura = lancamentos.filter(
        fatura = fatura
    )

    return competencia_service.soma_lancamentos(lancamentos_fatura)


def get_receitas_fatura(fatura):

    lancamentos = lancamento_service.get_receitas_competencia(fatura.competencia)
    
    lancamentos_fatura = lancamentos.filter(
        fatura = fatura
    )

    return competencia_service.soma_lancamentos(lancamentos_fatura)

def total_fatura(fatura):
    soma_fatura = get_receitas_fatura(fatura) - get_despesas_fatura(fatura)
    return soma_fatura - (fatura.valor_pago or 0)


def total_fatura_por_cartao(cartao, competencia):
    return total_fatura(obter_ou_criar_fatura(cartao, competencia))

def pagar_fatura(valor, cartao, competencia):
    fatura = obter_ou_criar_fatura(cartao, competencia)

    if fatura != None & valor != None:
        fatura.valor_pago = valor
