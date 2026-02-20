import datetime
import calendar
from decimal import Decimal
from django.db.models import Sum, Q, Case, When
from django.db.models.functions import Coalesce

from contas.models import Fatura, Cartao, Lancamento
from contas.services import lancamento_service, competencia_service


# -------------------------------
# Faturas
# -------------------------------

def obter_ou_criar_fatura(cartao: Cartao, competencia):
    fatura, _ = Fatura.objects.select_related('competencia').get_or_create(
        cartao=cartao, competencia=competencia
    )
    return fatura


def carregar_fatura_com_rotativo(cartao: Cartao, competencia):
    fatura_atual = obter_ou_criar_fatura(cartao, competencia)
    
    mes_anterior = competencia_service.anterior(competencia.mes, competencia.ano)
    fatura_anterior = Fatura.objects.filter(
        cartao_id=cartao.id,
        competencia__mes=mes_anterior['mes'],
        competencia__ano=mes_anterior['ano'],
    ).select_related('competencia').first()  # ✅ carrega competencia junto

    if fatura_anterior:
        gerar_lancamento_rotativo(fatura_anterior, fatura_atual)

    return fatura_atual


def get_fatura_anterior(fatura: Fatura, gerar_rotativo=True):
    mes_anterior = competencia_service.anterior(fatura.competencia.mes, fatura.competencia.ano)
    
    fatura_anterior = Fatura.objects.filter(
        cartao=fatura.cartao,
        competencia__mes=mes_anterior['mes'],
        competencia__ano=mes_anterior['ano'],
    ).select_related('competencia').first()  # ✅ select_related evita query extra na competencia

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


def gerar_lancamento_rotativo(fatura_anterior, fatura_atual, juros_mensal=0):
    if not fatura_anterior.lancamento_set.filter(eh_rotativo=True).exists():
        comp = competencia_service.anterior(
            fatura_anterior.competencia.mes,
            fatura_anterior.competencia.ano
        )
        # ✅ select_related evita rebuscar cartao e competencia
        fatura_2_atras = Fatura.objects.filter(
            cartao_id=fatura_anterior.cartao_id,  # ✅ usa _id direto, sem JOIN
            competencia__mes=comp['mes'],
            competencia__ano=comp['ano'],
        ).select_related('competencia').first()

        if fatura_2_atras:
            _gerar_rotativo_simples(fatura_2_atras, fatura_anterior, juros_mensal)

    _gerar_rotativo_simples(fatura_anterior, fatura_atual, juros_mensal)


def _gerar_rotativo_simples(fatura_anterior, fatura_atual, juros_mensal=0):
    totais = fatura_anterior.lancamento_set.aggregate(
        total_despesas=Coalesce(Sum('valor', filter=Q(natureza=Lancamento.Natureza.DESPESA)), Decimal('0')),
        total_receitas=Coalesce(Sum('valor', filter=Q(natureza=Lancamento.Natureza.RECEITA)), Decimal('0')),
    )

    saldo = totais['total_despesas'] - totais['total_receitas']
    mes, ano = fatura_atual.competencia.mes, fatura_atual.competencia.ano
    data_lancamento = datetime.date(ano, mes, calendar.monthrange(ano, mes)[1])

    rotativo_existente = fatura_atual.lancamento_set.filter(eh_rotativo=True).first()

    if saldo <= 0:
        if rotativo_existente:  # ✅ só deleta se existir
            rotativo_existente.delete()
        return None

    saldo_com_juros = saldo * (1 + Decimal(str(juros_mensal)))
    descricao = f"Saldo rotativo de {fatura_anterior.competencia.mes}/{fatura_anterior.competencia.ano}"

    if rotativo_existente:
        # ✅ só atualiza se o valor mudou
        if rotativo_existente.valor != saldo_com_juros:
            rotativo_existente.valor = saldo_com_juros
            rotativo_existente.descricao = descricao
            rotativo_existente.data = data_lancamento
            rotativo_existente.save()
    else:
        Lancamento.objects.create(
            fatura=fatura_atual,
            eh_rotativo=True,
            descricao=descricao,
            valor=saldo_com_juros,
            natureza=Lancamento.Natureza.DESPESA,
            pago=False,
            data=data_lancamento,
        )


def calcular_saldo_fatura(fatura: Fatura) -> Decimal:
    totais = fatura.lancamento_set.aggregate(
        despesas=Coalesce(Sum('valor', filter=Q(natureza=Lancamento.Natureza.DESPESA)), Decimal("0.00")),
        receitas=Coalesce(Sum('valor', filter=Q(natureza=Lancamento.Natureza.RECEITA)), Decimal("0.00")),
    )
    return totais['despesas'] - totais['receitas']


def calcular_despesas_fatura(fatura: Fatura) -> Decimal:
    """Simples: despesas - receitas. Rotativo já é um lançamento de DESPESA."""
    return fatura.lancamento_set.filter(
        natureza=Lancamento.Natureza.DESPESA
    ).aggregate(total=Coalesce(Sum('valor'), Decimal("0.00")))['total']

