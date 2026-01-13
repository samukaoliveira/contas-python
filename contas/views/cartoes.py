from django.shortcuts import redirect, render
from contas.services import competencia_service
from contas.views.cartao_form import CartaoFrom
from datetime import date
from contas.models import Cartao

def home(request):

    cartoes = Cartao.objects.all

    return render(request, 'contas/cartoes.html', {
        'cartoes': cartoes
    })

def create(request):

    if request.method == 'POST':

        form = CartaoFrom(request.POST)

        if form.is_valid():
            form.save()
        
    return redirect("cartoes_path")


def edit(request, pk):
    data = {}
    lancamento = Cartao.objects.get(
        pk = pk
    )

    form = CartaoFrom(request.POST or None, instance=lancamento)
    data['form'] = form

    if form.is_valid():
        form.save()

    return redirect('cartoes_path')

def update(request, pk):
    data = {}
    lancamento = Cartao.objects.get(
        pk = pk
    )

    form = CartaoFrom(request.POST or None, instance=lancamento)
    data['form'] = form

    if form.is_valid():
        form.save()

    return redirect('cartoes_path')





