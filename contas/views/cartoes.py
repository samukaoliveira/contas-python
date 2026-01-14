from django.shortcuts import redirect, render
from contas.services import competencia_service
from contas.views.cartao_form import CartaoFrom
from datetime import date
from contas.models import Cartao, Fatura, Lancamento
from contas.services import competencia_service, fatura_service
from django.urls import reverse

def home(request):

    cartoes = Cartao.objects.all

    return render(request, 'contas/cartoes.html', {
        'cartoes': cartoes,
        'path': "cartoes_path",
        'titulo': "Cartões",
        'titulo_tem_setas': False
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
        'path': reverse('cartao_show_path', args=[cartao.id]),
        'pk': cartao.id,
        'titulo': f"Cartão - { cartao.descricao } - { competencia.mes_nome() }/{ competencia.ano }",
        'titulo_tem_setas': True
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





