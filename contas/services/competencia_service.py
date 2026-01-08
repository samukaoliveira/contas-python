from datetime import date
from contas.models import Competencia

def obter_competencia_atual():
    hoje = date.today()

    competencia, _ = Competencia.objects.get_or_create(
        mes=hoje.month,
        ano=hoje.year
    )

    return competencia
