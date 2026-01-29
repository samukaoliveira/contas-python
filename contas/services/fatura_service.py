from datetime import date
from contas.models import Fatura, Cartao, Lancamento
from contas.services import lancamento_service, competencia_service
from decimal import Decimal


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
    receitas_fatura = get_receitas_fatura(fatura) or Decimal("0.00")
    despesas_fatura = get_despesas_fatura(fatura) or Decimal("0.00")
    soma_fatura = receitas_fatura - despesas_fatura

    return soma_fatura


def total_fatura_por_cartao(cartao, competencia):
    fatura = obter_ou_criar_fatura(cartao, competencia)

    gerar_rotativo(fatura)

    return total_fatura(fatura)


def pagar_fatura(valor, data_pagamento, cartao, competencia):
    fatura = obter_ou_criar_fatura(cartao, competencia)

    if fatura is not None and valor is not None:
        fatura.valor_pago = valor
        fatura.data_pagamento = data_pagamento
        fatura.save()

def saldo_fatura_anterior(fatura):
    fatura_anterior = get_fatura_anterior(fatura)
    return total_fatura(fatura_anterior)


def get_fatura_anterior(fatura):
    mes_anterior = competencia_service.anterior(
        fatura.competencia.mes, 
        fatura.competencia.ano)
    
    comp_anterior = competencia_service.obter_ou_criar_competencia(
        mes_anterior['mes'],
        mes_anterior['ano'])
    
    return obter_ou_criar_fatura(fatura.cartao, comp_anterior)


def saldo_rotativo_cartoes(competencia):
    
    faturas = gera_faturas_por_competencia(competencia)

    for f in faturas:
        soma += f.valor_pago

    return soma


def gera_faturas_por_competencia(competencia):
    return Fatura.objects.filter(
        competencia = competencia
    )


def saldo_nao_pago(fatura):
    receitas = get_receitas_fatura(fatura) or Decimal("0.00")
    despesas = get_despesas_fatura(fatura) or Decimal("0.00")
    total = receitas - despesas

    pago = fatura.valor_pago or Decimal("0.00")

    return total + pago


def gerar_rotativo(fatura_atual):
    fatura_anterior = get_fatura_anterior(fatura_atual)

    saldo = saldo_nao_pago(fatura_anterior)

    Lancamento.objects.update_or_create(
        fatura=fatura_atual,
        eh_rotativo=True,

        defaults={
            "descricao": "Saldo rotativo da fatura anterior",
            "data": date(
                fatura_atual.competencia.ano,
                fatura_atual.competencia.mes,
                1
            ),
            "valor": saldo,
            "natureza": Lancamento.Natureza.DESPESA,
            "pago": False,
        }
    )