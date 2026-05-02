from datetime import date
from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from contas.models import Competencia, Cartao, Lancamento
from contas.models.fatura import Fatura
from contas.services import competencia_service, lancamento_service, fatura_service
from contas.views.cartao_form import CartaoFrom

def get_cartoes(competencia):
    return Cartao.objects.filter(
        competencia = competencia
    )

def get_cartao_detalhe_data(request, pk):

    competencia, mes, ano = competencia_service.get_competencia_atual(request)

    cartao = Cartao.objects.get(pk=pk)

    fatura = fatura_service.carregar_fatura_com_rotativo(
        cartao=cartao,
        competencia=competencia
    )

    lancamentos = list(
        Lancamento.objects.filter(fatura=fatura).order_by('data')
    )

    despesas = sum(
        l.valor for l in lancamentos
        if l.natureza == Lancamento.Natureza.DESPESA
    )

    receitas = sum(
        l.valor for l in lancamentos
        if l.natureza == Lancamento.Natureza.RECEITA
    )

    total_fatura = despesas
    falta_pagar = despesas - receitas

    return {
        "cartao": cartao,
        "fatura": fatura,
        "lancamentos": lancamentos,
        "total_fatura": total_fatura,
        "falta_pagar": falta_pagar,
        "competencia": competencia
    }


def show(request, pk):

    competencia, mes, ano = competencia_service.get_competencia_atual(request)

    cartao = Cartao.objects.get(pk =pk)

    fatura = fatura_service.carregar_fatura_com_rotativo(
        cartao=cartao,
        competencia=competencia
    )

    # ✅ Uma única query, avaliada como lista
    lancamentos = list(Lancamento.objects.filter(fatura=fatura).order_by('data'))

    # ✅ Calcula tudo em Python, sem novas queries
    despesas = sum(l.valor for l in lancamentos if l.natureza == Lancamento.Natureza.DESPESA)
    receitas = sum(l.valor for l in lancamentos if l.natureza == Lancamento.Natureza.RECEITA)
    total_fatura = despesas          # total de despesas
    falta_pagar = despesas - receitas  # saldo líquido

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

    next_url = request.POST.get('next') 
    
    return redirect(next_url or "home_path")

