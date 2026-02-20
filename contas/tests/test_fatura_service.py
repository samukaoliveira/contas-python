from datetime import date
from decimal import Decimal

from django.test import TestCase

from contas.models import Cartao, Fatura, Lancamento
from contas.services import fatura_service, competencia_service


class FaturaServiceTest(TestCase):

    def setUp(self):
        self.cartao = Cartao.objects.create(
            descricao="Master",
            limite=5000,
            fechamento=10,
            vencimento=20
        )

        self.comp_atual = competencia_service.obter_ou_criar_competencia(1, 2026)
        self.comp_anterior = competencia_service.obter_ou_criar_competencia(12, 2025)

        self.fatura_atual = Fatura.objects.create(
            cartao=self.cartao,
            competencia=self.comp_atual
        )

        self.fatura_anterior = Fatura.objects.create(
            cartao=self.cartao,
            competencia=self.comp_anterior
        )

    # ---------------------------
    # obter_ou_criar_fatura
    # ---------------------------

    def test_obter_ou_criar_fatura(self):
        fatura = fatura_service.obter_ou_criar_fatura(
            self.cartao,
            self.comp_atual
        )

        self.assertIsNotNone(fatura)
        self.assertEqual(Fatura.objects.count(), 2)

    # ---------------------------
    # calcular saldo
    # ---------------------------

    def test_calcular_saldo_fatura(self):
        Lancamento.objects.create(
            fatura=self.fatura_anterior,
            descricao="Compra",
            data=date.today(),
            valor=500,
            natureza=Lancamento.Natureza.DESPESA,
            pago=False
        )

        Lancamento.objects.create(
            fatura=self.fatura_anterior,
            descricao="Pagamento",
            data=date.today(),
            valor=200,
            natureza=Lancamento.Natureza.RECEITA,
            pago=False
        )

        saldo = fatura_service.calcular_saldo_fatura(self.fatura_anterior)

        self.assertEqual(saldo, Decimal("300"))

    # ---------------------------
    # rotativo cria
    # ---------------------------

    def test_rotativo_criado_quando_saldo_positivo(self):
        Lancamento.objects.create(
            fatura=self.fatura_anterior,
            descricao="Compra",
            data=date.today(),
            valor=1000,
            natureza=Lancamento.Natureza.DESPESA,
            pago=False
        )

        fatura_service.gerar_lancamento_rotativo(
            self.fatura_anterior,
            self.fatura_atual
        )

        rotativo = self.fatura_atual.lancamento_set.filter(
            eh_rotativo=True
        ).first()

        self.assertIsNotNone(rotativo)
        self.assertEqual(rotativo.valor, Decimal("1000"))

    # ---------------------------
    # rotativo não cria
    # ---------------------------

    def test_rotativo_nao_criado_quando_saldo_zero(self):
        fatura_service.gerar_lancamento_rotativo(
            self.fatura_anterior,
            self.fatura_atual
        )

        self.assertFalse(
            self.fatura_atual.lancamento_set.filter(eh_rotativo=True).exists()
        )

    # ---------------------------
    # rotativo atualiza
    # ---------------------------

    def test_rotativo_atualiza_valor(self):
        Lancamento.objects.create(
            fatura=self.fatura_anterior,
            descricao="Compra",
            data=date.today(),
            valor=500,
            natureza=Lancamento.Natureza.DESPESA,
            pago=False
        )

        # primeira geração
        fatura_service.gerar_lancamento_rotativo(
            self.fatura_anterior,
            self.fatura_atual
        )

        # altera valor
        Lancamento.objects.create(
            fatura=self.fatura_anterior,
            descricao="Nova Compra",
            data=date.today(),
            valor=500,
            natureza=Lancamento.Natureza.DESPESA,
            pago=False
        )

        fatura_service.gerar_lancamento_rotativo(
            self.fatura_anterior,
            self.fatura_atual
        )

        rotativo = self.fatura_atual.lancamento_set.filter(
            eh_rotativo=True
        ).first()

        self.assertEqual(rotativo.valor, Decimal("1000"))

    # ---------------------------
    # calcular despesas fatura
    # ---------------------------

    def test_calcular_despesas_fatura(self):
        Lancamento.objects.create(
            fatura=self.fatura_anterior,
            descricao="Compra",
            data=date.today(),
            valor=700,
            natureza=Lancamento.Natureza.DESPESA,
            pago=False
        )

        total = fatura_service.calcular_despesas_fatura(self.fatura_anterior)

        self.assertEqual(total, Decimal("700"))