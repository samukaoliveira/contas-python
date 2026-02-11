from django.shortcuts import redirect, render
from contas.services import competencia_service, lancamento_service
from contas.views.lancamento_form import LancamentoForm
from datetime import date
from contas.models import Lancamento
from django.contrib.auth.decorators import login_required

@login_required
def create(request):

    fixo = {}
    lancamento = valida_lancamento(request)
    fixo = lancamento.fixo

    match fixo:
        case Lancamento.Fixo.FIXO:
            lancamento_service.cria_lancamentos_fixos(lancamento)
        case Lancamento.Fixo.NAO:
            lancamento_service.salva_lancamento(lancamento)
        case Lancamento.Fixo.PARCELADO:
            return
    
    
    return redirect("home_path")
        
@login_required
def create_cartao(request, pk):

    lancamento_service.salva_lancamento(request)
    return redirect("cartao_show_path", pk=pk)

@login_required
def pagar_cartao(request):

    lancamento_service.salva_lancamento(request)
    return redirect("home_path")




def valida_lancamento(request):
    if request.method == 'POST':

            form = LancamentoForm(request.POST)

            if form.is_valid():
                return form.save(commit=False)

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




