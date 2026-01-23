from django.db import models

class Fatura(models.Model):
    cartao = models.ForeignKey(
        'contas.Cartao',
        on_delete=models.CASCADE
    )
    competencia = models.ForeignKey(
        'contas.Competencia',
        on_delete=models.CASCADE
    )
    valor_pago = models.FloatField(null=True)
    data_pagamento = models.DateField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cartao', 'competencia'],
                name='unique_fatura_cartao_competencia'
            )
        ]

    def __str__(self):
        return f'{self.cartao}/{self.competencia}'