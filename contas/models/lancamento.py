from django.db import models

class Lancamento(models.Model):
    descricao = models.CharField(max_length=70)
    data = models.DateField()
    valor = models.FloatField()
    pago = models.BooleanField(default=False)
    fatura = models.ForeignKey(
        'contas.Fatura', 
        on_delete=models.CASCADE, null=True
        )
    dt_criacao = models.DateTimeField(auto_now=True)
    dt_update = models.DateTimeField(auto_now=True)