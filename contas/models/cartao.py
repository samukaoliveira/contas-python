from django.db import models

class Cartao(models.Model):
    descricao = models.CharField(max_length=70)
    limite = models.FloatField()
    fechamento = models.IntegerField()
    vencimento = models.IntegerField()
    dt_criacao = models.DateTimeField(auto_now=True)
    dt_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Cartoes'

    def __str__(self):
        return self.descricao