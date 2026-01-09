from datetime import date
from django.shortcuts import redirect

from contas.models import Competencia
from contas.services.competencia_service import obter_competencia_atual

