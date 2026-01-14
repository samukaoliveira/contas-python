from django.shortcuts import redirect, render
from contas.services import competencia_service
from contas.views.cartao_form import CartaoFrom
from datetime import date
from contas.models import Cartao, Fatura, Lancamento
from contas.services import competencia_service, fatura_service

def home(request):

    cartoes = Cartao.objects.all

    return render(request, 'contas/cartoes.html', {
        'cartoes': cartoes
    })

def show(request, pk):

    hoje = date.today()
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    cartao = Cartao.objects.get(pk =pk)

    competencia = competencia_service.obter_ou_criar_competencia(
            mes=int(mes) if mes else hoje.month,
            ano=int(ano) if ano else hoje.year
        )

    fatura = fatura_service.obter_ou_criar_fatura(
        cartao=cartao,
        competencia=competencia
    )

    lancamentos = Lancamento.objects.filter(
        fatura = fatura
    )

    total_fatura = fatura_service.total_fatura(fatura)

    return render(request, 'contas/cartao.html', {
        'cartao': cartao,
        'fatura': fatura,
        'lancamentos': lancamentos,
        'total_fatura': total_fatura,
        'form_action': "cartao_lancamento_create_path",
        'anterior': competencia_service.anterior(mes, ano),
        'proximo': competencia_service.proximo(mes, ano),
        'path': "cartao_show_path",
        'pk': cartao.id
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





