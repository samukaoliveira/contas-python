from django.forms import ModelForm
from contas.models import Cartao

class CartaoFrom(ModelForm):
    class Meta:
        model = Cartao
        fields = ['descricao', 
                'limite', 
                'fechamento', 
                'vencimento']