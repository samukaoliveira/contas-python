from datetime import date
from contas.models import Competencia, Cartao
from contas.services import lancamento_service

def get_cartoes(competencia):
    return Cartao.objects.filter(
        competencia = competencia
    )

