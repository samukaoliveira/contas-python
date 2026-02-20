from datetime import date
from decimal import Decimal

from django.test import TestCase
from contas.models import Lancamento, Cartao
from contas.services import lancamento_service


class LancamentoServiceTest(TestCase):

    def test_saldo_em_caixa(self):
        Lancamento.objects.create(
            descricao="Salario",
            data=date.today(),
            valor=1000,
            natureza=Lancamento.Natureza.RECEITA,
            pago=True,
        )

        Lancamento.objects.create(
            descricao="Aluguel",
            data=date.today(),
            valor=400,
            natureza=Lancamento.Natureza.DESPESA,
            pago=True,
        )

        saldo = lancamento_service.saldo_em_caixa()

        self.assertEqual(saldo, Decimal("600"))

    def test_todas_receitas_e_despesas_pagas(self):
        Lancamento.objects.create(
            descricao="Salario",
            data=date.today(),
            valor=2000,
            natureza=Lancamento.Natureza.RECEITA,
            pago=True,
        )

        Lancamento.objects.create(
            descricao="Conta",
            data=date.today(),
            valor=500,
            natureza=Lancamento.Natureza.DESPESA,
            pago=True,
        )

        self.assertEqual(
            lancamento_service.todas_receitas_pagas(),
            Decimal("2000")
        )

        self.assertEqual(
            lancamento_service.todas_despesas_pagas(),
            Decimal("500")
        )

    def test_cria_lancamentos_parcelados(self):
        lancamento = Lancamento(
            descricao="Notebook",
            data=date(2026, 1, 10),
            valor=300,
            natureza=Lancamento.Natureza.DESPESA,
            parcelas=3,
            fixo=Lancamento.Fixo.PARCELADO
        )

        lancamento_service.cria_lancamentos_parcelados(lancamento)

        self.assertEqual(Lancamento.objects.count(), 3)

        descricoes = list(
            Lancamento.objects.values_list("descricao", flat=True)
        )

        self.assertIn("Notebook (1/3)", descricoes)
        self.assertIn("Notebook (2/3)", descricoes)
        self.assertIn("Notebook (3/3)", descricoes)

    def test_cria_lancamentos_fixos(self):
        lancamento = Lancamento(
            descricao="Academia",
            data=date(2026, 1, 5),
            valor=100,
            natureza=Lancamento.Natureza.DESPESA,
            fixo=Lancamento.Fixo.FIXO
        )

        lancamento_service.cria_lancamentos_fixos(lancamento)

        # Janeiro até dezembro
        self.assertTrue(Lancamento.objects.count() >= 1)

    def test_lancamento_pagar_fatura(self):
        cartao = Cartao.objects.create(
            descricao="Visa",
            limite=5000,
            fechamento=10,
            vencimento=20
        )

        # criando fatura fake simples
        from contas.models import Fatura
        from contas.models import Competencia

        competencia = Competencia.objects.create(mes=1, ano=2026)
        fatura = Fatura.objects.create(
            cartao=cartao,
            competencia=competencia
        )

        lancamento_service.lancamento_pagar_fatura(
            valor=500,
            data=date.today(),
            fatura_atual=fatura
        )

        self.assertEqual(Lancamento.objects.count(), 1)

        lanc = Lancamento.objects.first()
        self.assertEqual(lanc.valor, 500)
        self.assertEqual(lanc.natureza, Lancamento.Natureza.RECEITA)