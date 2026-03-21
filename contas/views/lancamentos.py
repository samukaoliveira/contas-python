from django.shortcuts import redirect, render
from contas.services import competencia_service, lancamento_service
from contas.views.lancamento_form import LancamentoForm
from datetime import date
from contas.models import Lancamento
from django.contrib.auth.decorators import login_required

@login_required
def create(request):
    
    lancamento = valida_lancamento(request)

    salva_por_frequencia(lancamento)
    
    next_url = request.POST.get('next') 
    
    return redirect(next_url or "home_path")
        
@login_required
def create_cartao(request, pk):
    
    lancamento = valida_lancamento(request)

    salva_por_frequencia_cartao(lancamento)
    
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
            

def salva_por_frequencia(lancamento):

    fixo = {}
    fixo = lancamento.fixo

    match fixo:
        case Lancamento.Fixo.FIXO:
            lancamento_service.cria_lancamentos_fixos(lancamento)
        case Lancamento.Fixo.NAO:
            lancamento_service.salva_lancamento(lancamento)
        case Lancamento.Fixo.PARCELADO:
            lancamento_service.cria_lancamentos_parcelados(lancamento)
        

def salva_por_frequencia_cartao(lancamento):

    fixo = {}
    fixo = lancamento.fixo

    match fixo:
        case Lancamento.Fixo.FIXO:
            lancamento_service.cria_lancamentos_fixos_cartao(lancamento)
        case Lancamento.Fixo.NAO:
            lancamento_service.salva_lancamento(lancamento)
        case Lancamento.Fixo.PARCELADO:
             lancamento_service.cria_lancamentos_parcelados(lancamento)


@login_required
def update(request, pk):
    lancamento = Lancamento.objects.get(pk=pk)

    form = LancamentoForm(request.POST or None, instance=lancamento)

    if request.method == "POST" and form.is_valid():
        escopo = request.POST.get("escopo_update", "um")

        lancamento_editado = form.save(commit=False)

        # 🔹 CASO 1: só este lançamento
        if escopo == "um" or lancamento.fixo == Lancamento.Fixo.NAO:
            lancamento_editado.save()

        # 🔹 CASO 2: este + próximos
        else:
            atualizar_lancamentos_futuros(lancamento, lancamento_editado)

            next_url = request.POST.get('next') 
            
            return redirect(next_url or "home_path")

    return render(request, 'seu_template.html', {'form': form})

@login_required
def delete(request, pk):
    lancamento = Lancamento.objects.get(pk = pk)

    if lancamento != None:
          lancamento.delete()

    return redirect('home_path')


def atualizar_lancamentos_futuros(lancamento_original, lancamento_editado):
    """
    Atualiza este lançamento e todos os próximos da mesma série.
    """

    grupo_id = getattr(lancamento_original, 'grupo_id', None)

    # 🚨 SEM GRUPO → NÃO ARRISCA
    if not grupo_id:
        # atualiza só o atual (fail safe)
        lancamento_original.descricao = lancamento_editado.descricao
        lancamento_original.valor = lancamento_editado.valor
        lancamento_original.natureza = lancamento_editado.natureza

        if hasattr(lancamento_editado, 'categoria'):
            lancamento_original.categoria = lancamento_editado.categoria

        if hasattr(lancamento_editado, 'conta'):
            lancamento_original.conta = lancamento_editado.conta

        lancamento_original.save()
        return

    # ✅ COM GRUPO → atualiza em lote
    lancamentos = Lancamento.objects.filter(
        grupo_id=grupo_id,
        data__gte=lancamento_original.data
    )

    for l in lancamentos:
        l.descricao = lancamento_editado.descricao
        l.valor = lancamento_editado.valor
        l.natureza = lancamento_editado.natureza

        # 🔹 campos opcionais
        if hasattr(lancamento_editado, 'categoria'):
            l.categoria = lancamento_editado.categoria

        if hasattr(lancamento_editado, 'conta'):
            l.conta = lancamento_editado.conta

        # 🔥 IMPORTANTE: NÃO mexer nesses:
        # l.data
        # l.parcelas
        # l.grupo_id

        l.save()