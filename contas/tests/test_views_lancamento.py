from datetime import date

from django.test import TestCase
from django.urls import reverse

from contas.models import Lancamento, Cartao


class LancamentoCreateViewTest(TestCase):

    def test_create_lancamento_valido_salva_e_redireciona(self):
        response = self.client.post(
            reverse('lancamentos_create_path'),
            data={
                'descricao': 'Aluguel',
                'data': date.today(),
                'valor': 1200,
                'natureza': Lancamento.Natureza.DESPESA,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home_path'))
        self.assertEqual(Lancamento.objects.count(), 1)

    def test_create_lancamento_invalido_nao_salva(self):
        response = self.client.post(
            reverse('lancamentos_create_path'),
            data={
                'descricao': '',
                'valor': '',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Lancamento.objects.count(), 0)


class LancamentoCreateCartaoViewTest(TestCase):

    def setUp(self):
        self.cartao = Cartao.objects.create(
            descricao='Nubank',
            limite=5000,
            fechamento=10,
            vencimento=20
        )

    def test_create_lancamento_cartao_redireciona_para_cartao(self):
        response = self.client.post(
            reverse(
                'cartao_lancamento_create_path',
                args=[self.cartao.pk]
            ),
            data={
                'descricao': 'Mercado',
                'data': date.today(),
                'valor': 300,
                'natureza': Lancamento.Natureza.DESPESA,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('cartao_show_path', args=[self.cartao.pk])
        )

        self.assertEqual(Lancamento.objects.count(), 1)


class LancamentoUpdateViewTest(TestCase):

    def setUp(self):
        self.lancamento = Lancamento.objects.create(
            descricao='Internet',
            data=date.today(),
            valor=100,
            natureza=Lancamento.Natureza.DESPESA,
        )

    def test_update_lancamento_atualiza_e_redireciona(self):
        response = self.client.post(
            reverse(
                'lancamentos_update_path',
                args=[self.lancamento.pk]
            ),
            data={
                'descricao': 'Internet Fibra',
                'data': date.today(),
                'valor': 150,
                'natureza': Lancamento.Natureza.DESPESA,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home_path'))

        self.lancamento.refresh_from_db()
        self.assertEqual(self.lancamento.descricao, 'Internet Fibra')
        self.assertEqual(self.lancamento.valor, 150)
