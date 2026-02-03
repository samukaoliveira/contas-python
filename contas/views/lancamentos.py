from django.shortcuts import redirect, render
from contas.services import competencia_service
from contas.views.lancamento_form import LancamentoForm
from datetime import date
from contas.models import Lancamento
from django.contrib.auth.decorators import login_required

@login_required
def create(request):
    salva_lancamento(request)
    return redirect("home_path")
        
@login_required
def create_cartao(request, pk):

    salva_lancamento(request)
    return redirect("cartao_show_path", pk=pk)

@login_required
def salva_lancamento(request):
    if request.method == 'POST':

            form = LancamentoForm(request.POST)

            if form.is_valid():
                form.save()

@login_required
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

@login_required
def delete(request, pk):
    lancamento = Lancamento.objects.get(pk = pk)

    if lancamento != None:
          lancamento.delete()

    return redirect('home_path')




