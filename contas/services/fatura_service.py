from datetime import date
import calendar
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce

from contas.models import Fatura, Cartao, Lancamento
from contas.services import lancamento_service, competencia_service


# -------------------------------
# Faturas
# -------------------------------

def obter_ou_criar_fatura(cartao: Cartao, competencia):
    """
    Obtém a fatura ou cria uma nova para o cartão e competência.
    Não gera rotativo automaticamente.
    """
    fatura, _ = Fatura.objects.get_or_create(cartao=cartao, competencia=competencia)
    return fatura


def carregar_fatura_com_rotativo(cartao: Cartao, competencia):
    """
    Carrega a fatura atual e garante que o rotativo da fatura anterior seja gerado ou atualizado.
    """
    fatura_atual = obter_ou_criar_fatura(cartao, competencia)
    fatura_anterior = get_fatura_anterior(fatura_atual, gerar_rotativo=False)

    if fatura_anterior:
        gerar_lancamento_rotativo(fatura_anterior, fatura_atual)

    return fatura_atual


def get_fatura_anterior(fatura: Fatura, gerar_rotativo=True):
    """
    Retorna a fatura anterior.
    Se gerar_rotativo=True, não gera recursivamente para evitar loops.
    """
    mes_anterior = competencia_service.anterior(fatura.competencia.mes, fatura.competencia.ano)
    comp_anterior = competencia_service.obter_ou_criar_competencia(mes_anterior['mes'], mes_anterior['ano'])
    fatura_anterior = Fatura.objects.filter(cartao=fatura.cartao, competencia=comp_anterior).first()

    # Evita loop infinito ao gerar rotativo
    if gerar_rotativo and fatura_anterior:
        gerar_lancamento_rotativo(fatura_anterior, fatura)

    return fatura_anterior


def get_proxima_fatura(fatura: Fatura):
    """
    Retorna a próxima fatura do cartão.
    """
    proxima_comp = competencia_service.proximo(fatura.competencia.mes, fatura.competencia.ano)
    comp_proxima = competencia_service.obter_ou_criar_competencia(proxima_comp['mes'], proxima_comp['ano'])
    return obter_ou_criar_fatura(fatura.cartao, comp_proxima)


def gera_faturas_por_competencia(competencia):
    """
    Retorna todas as faturas de uma competência.
    """
    return Fatura.objects.filter(competencia=competencia)


# -------------------------------
# Rotativo
# -------------------------------

import calendar
from decimal import Decimal
from django.db.models import Sum
import datetime

def gerar_lancamento_rotativo(fatura_anterior, fatura_atual, juros_mensal=0):
    # ✅ Garante que o rotativo da fatura anterior já foi calculado antes
    fatura_anterior_da_anterior = Fatura.objects.filter(
        cartao=fatura_anterior.cartao,
        competencia__mes=competencia_service.anterior(
            fatura_anterior.competencia.mes, 
            fatura_anterior.competencia.ano
        )['mes'],
        competencia__ano=competencia_service.anterior(
            fatura_anterior.competencia.mes,
            fatura_anterior.competencia.ano
        )['ano'],
    ).first()

    if fatura_anterior_da_anterior:
        gerar_lancamento_rotativo(fatura_anterior_da_anterior, fatura_anterior, juros_mensal)

    total_despesas = fatura_anterior.lancamento_set.filter(
        natureza=Lancamento.Natureza.DESPESA
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

    total_receitas = fatura_anterior.lancamento_set.filter(
        natureza=Lancamento.Natureza.RECEITA
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

    saldo = total_despesas - total_receitas

    if saldo <= 0:
        Lancamento.objects.filter(fatura=fatura_atual, eh_rotativo=True).delete()
        return None

    saldo_com_juros = saldo * (1 + Decimal(str(juros_mensal)))

    mes = fatura_atual.competencia.mes
    ano = fatura_atual.competencia.ano
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_lancamento = datetime.date(ano, mes, ultimo_dia)

    lancamento_rotativo, _ = Lancamento.objects.update_or_create(
        fatura=fatura_atual,
        eh_rotativo=True,
        defaults={
            "descricao": f"Saldo rotativo de {fatura_anterior.competencia.mes}/{fatura_anterior.competencia.ano}",
            "valor": saldo_com_juros,
            "natureza": Lancamento.Natureza.DESPESA,
            "pago": False,
            "data": data_lancamento,
        }
    )
    return lancamento_rotativo


def calcular_saldo_fatura(fatura: Fatura) -> Decimal:
    """Simples: despesas - receitas. Rotativo já é um lançamento de DESPESA."""
    despesas = fatura.lancamento_set.filter(
        natureza=Lancamento.Natureza.DESPESA
    ).aggregate(total=Coalesce(Sum('valor'), Decimal("0.00")))['total']

    receitas = fatura.lancamento_set.filter(
        natureza=Lancamento.Natureza.RECEITA
    ).aggregate(total=Coalesce(Sum('valor'), Decimal("0.00")))['total']

    return despesas - receitas


def calcular_despesas_fatura(fatura: Fatura) -> Decimal:
    """Simples: despesas - receitas. Rotativo já é um lançamento de DESPESA."""
    return fatura.lancamento_set.filter(
        natureza=Lancamento.Natureza.DESPESA
    ).aggregate(total=Coalesce(Sum('valor'), Decimal("0.00")))['total']

