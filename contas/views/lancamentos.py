from django.shortcuts import redirect, render
from contas.services import competencia_service
from contas.views.lancamento_form import LancamentoForm
from datetime import date
from contas.models import Lancamento

def create(request):
    salva_lancamento(request)
    return redirect("home_path")
        

def create_cartao(request, pk):

    salva_lancamento(request)
    return redirect("cartao_show_path", pk=pk)


def salva_lancamento(request):
    if request.method == 'POST':

            form = LancamentoForm(request.POST)

            if form.is_valid():
                form.save()


def update(request, pk):
    data = {}
    lancamento = Lancamento.objects.get(
        pk = pk
    )

    form = LancamentoForm(request.POST or None, instance=lancamento)
    data['form'] = form

    if form.is_valid():
        form.save()

    return redirect('home_path')





