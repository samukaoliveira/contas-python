from django.db import models

class Lancamento(models.Model):
    descricao = models.CharField(max_length=70)
    data = models.DateField()
    valor =  models.DecimalField(
                max_digits=10,
                decimal_places=2
    )
    pago = models.BooleanField(default=False)
    

    class Fixo(models.TextChoices):
            NAO = 'NAO', 'Nao'
            FIXO = 'FIXO', 'Fixo'
            PARCELADO = 'PARCELADO', 'Parcelado'

    fixo = models.CharField(
        max_length=10,
        choices=Fixo.choices,
        default=Fixo.NAO
    )

    parcelas = models.IntegerField(default=False)
    fatura = models.ForeignKey(
        'contas.Fatura', 
        on_delete=models.CASCADE, null=True,
        blank=True
        )
    dt_criacao = models.DateTimeField(auto_now=True)
    dt_update = models.DateTimeField(auto_now=True)

    eh_rotativo = models.BooleanField(default=False)

    class Natureza(models.TextChoices):
        DESPESA = 'DESPESA', 'Despesa'
        RECEITA = 'RECEITA', 'Receita'

    natureza = models.CharField(
        max_length=10,
        choices=Natureza.choices,
        default=Natureza.DESPESA
    )


    def __str__(self):
        return self.descricao
    
    class Meta:
        ordering = ['data']
        

    def fixo_helper(self):
        if self.fixo == True:
             return "FIXA"
        return ""
    
    def parcelas_helper(self):
        if not self.parcelas:
             return ""
        return f"( {{ self.parcelas }} )"