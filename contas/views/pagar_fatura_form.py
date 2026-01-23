from django.forms import ModelForm
from contas.models import Fatura

class PagarFaturaFrom(ModelForm):
    class Meta:
        model = Fatura
        fields = ['valor_pago', 
                'data_pagamento']