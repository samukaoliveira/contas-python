from django.forms import ModelForm
from contas.models import Lancamento

class LancamentoForm(ModelForm):
    class Meta:
        model = Lancamento
        fields = ['descricao', 'data' , 'valor', 'pago', 'fatura', 'natureza', 'fixo', 'parcelas']