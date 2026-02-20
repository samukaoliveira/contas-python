from django.shortcuts import redirect, render
from contas.services import competencia_service
from contas.views.cartao_form import CartaoFrom
from contas.views import lancamentos
from contas.views.lancamento_form import LancamentoForm
from datetime import date
from contas.models import Cartao, Fatura, Lancamento
from contas.services import competencia_service, fatura_service, lancamento_service
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

    hoje = date.today()
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    cartao = Cartao.objects.get(pk =pk)

    competencia = competencia_service.obter_ou_criar_competencia(
            mes=int(mes) if mes else hoje.month,
            ano=int(ano) if ano else hoje.year
        )

    fatura = fatura_service.carregar_fatura_com_rotativo(
        cartao=cartao,
        competencia=competencia
    )

    lancamentos = Lancamento.objects.filter(
        fatura = fatura
    )

    total_fatura = fatura_service.calcular_despesas_fatura(fatura)

    falta_pagar = fatura_service.calcular_saldo_fatura(fatura)

    return render(request, 'contas/cartao.html', {
        'cartao': cartao,
        'fatura': fatura,
        'lancamentos': lancamentos,
        'total_fatura': total_fatura,
        'falta_pagar': falta_pagar,
        'form_action': "cartao_lancamento_create_path",
        'anterior': competencia_service.anterior(mes, ano),
        'proximo': competencia_service.proximo(mes, ano),
        'path': reverse('cartao_show_path', args=[cartao.id]),
        'pk': cartao.id,
        'titulo': f"<span>Cartão - { cartao.descricao }</span><span>{ competencia.mes_nome() }/{ competencia.ano }</span>",
        'titulo_tem_setas': True
    })

@login_required
def create(request):

    if request.method == 'POST':

        form = CartaoFrom(request.POST)

        if form.is_valid():
            form.save()
        
    return redirect("cartoes_path")

@login_required
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

@login_required
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

@login_required
def pagar_fatura(request):

    if request.method == "POST":

        fatura = get_object_or_404(
            Fatura,
            pk=request.POST.get("fatura_id")
        )

        valor = Decimal(request.POST.get("valor"))
        data = request.POST.get("data")

        lancamento_service.lancamento_pagar_fatura(
            valor,
            data,
            fatura
        )

    return redirect("home_path")





