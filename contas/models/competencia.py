from django.db import models

class Competencia(models.Model):
    mes = models.DateField()
    ano = models.DateField()

    class Meta:
        unique_together = ('mes', 'ano')
        ordering = ['ano', 'mes']

    def __str__(self):
        return f'{self.mes:02d}/{self.ano}'