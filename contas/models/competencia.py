from django.db import models

class Competencia(models.Model):
    mes = models.PositiveSmallIntegerField()
    ano = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('mes', 'ano')
        ordering = ['ano', 'mes']

    def __str__(self):
        return f'{self.mes:02d}/{self.ano}'
    
    def mes_nome(self):
        MESES = [
            '', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
            'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
        ]
        return MESES[self.mes]
    

