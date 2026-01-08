from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import redirect

from contas.models import Competencia
from contas.services.competencia_service import obter_competencia_atual


def proxima_competencia_view(request):
    atual = obter_competencia_atual()

    proxima_data = date(atual.ano, atual.mes, 1) + relativedelta(months=1)

    competencia, _ = Competencia.objects.get_or_create(
        mes=proxima_data.month,
        ano=proxima_data.year
    )

    return redirect(
        'home_por_competencia',
        competencia_id=competencia.id
    )
