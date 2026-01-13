from django.shortcuts import redirect, render
from contas.services import competencia_service
from contas.views.lancamento_form import LancamentoForm
from datetime import date
from contas.models import Lancamento

def create(request):

    if request.method == 'POST':

        form = LancamentoForm(request.POST)

        if form.is_valid():
            form.save()
        
    return redirect("home_path")


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





