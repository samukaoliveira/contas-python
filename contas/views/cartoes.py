from django.shortcuts import redirect, render
from contas.services import competencia_service
from contas.views.cartao_form import CartaoFrom
from contas.views import lancamentos
from contas.views.lancamento_form import LancamentoForm
from datetime import date
from contas.models import Cartao, Fatura, Lancamento
from contas.services import competencia_service, fatura_service, lancamento_service, cartao_service
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.shortcuts import get_object_or_404

@login_required
def home(request):

    cartoes = Cartao.objects.all

    return render(request, 'contas/cartoes.html', {
        'cartoes': cartoes,
        'path': "cartoes_path",
        'titulo': "Cartões",
        'titulo_tem_setas': False
    })

@login_required
def show(request, pk):
    return cartao_service.show(request, pk)

@login_required
def create(request):
    return cartao_service.create(request)

@login_required
def edit(request, pk):
    return cartao_service.edit(request, pk)

@login_required
def update(request, pk):
    return cartao_service.update(request, pk)

@login_required
def pagar_fatura(request):
    return cartao_service.pagar_fatura(request)





