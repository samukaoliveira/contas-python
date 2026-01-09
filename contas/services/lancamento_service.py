from datetime import date
from contas.models import Lancamento

def get_lancamentos(competencia):
    return Lancamento.objects.filter(
            data__month = competencia.mes,
            data__year = competencia.ano) or None


def get_despesas_competencia(competencia):
    return get_lancamentos(competencia).filter(natureza = Lancamento.Natureza.DESPESA)


def get_receitas_competencia(competencia):
    return get_lancamentos(competencia).filter(natureza = Lancamento.Natureza.RECEITA)
