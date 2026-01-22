from datetime import date

from django.test import TestCase
from django.urls import reverse

from contas.models import Cartao, Fatura, Lancamento, Competencia
from contas.services import competencia_service, fatura_service


class CartaoHomeViewTest(TestCase):

    def setUp(self):
        self.cartao = Cartao.objects.create(
            descricao='Nubank',
            limite=5000,
            fechamento=10,
            vencimento=20
        )

    def test_home_status_code_200(self):
        response = self.client.get(reverse('cartoes_path'))
        self.assertEqual(response.status_code, 200)

    def test_home_exibe_cartao(self):
        response = self.client.get(reverse('cartoes_path'))
        self.assertContains(response, 'Nubank')



class CartaoShowViewTest(TestCase):

    def setUp(self):
        self.cartao = Cartao.objects.create(
            descricao='Inter',
            limite=3000,
            fechamento=5,
            vencimento=15
        )

    def test_show_sem_mes_ano_cria_competencia_e_fatura(self):
        response = self.client.get(
            reverse('cartao_show_path', args=[self.cartao.id])
        )

        self.assertEqual(response.status_code, 200)

        hoje = date.today()

        competencia = Competencia.objects.get(
            mes=hoje.month,
            ano=hoje.year
        )

        fatura = Fatura.objects.get(
            cartao=self.cartao,
            competencia=competencia
        )

        self.assertEqual(response.context['cartao'], self.cartao)
        self.assertEqual(response.context['fatura'], fatura)
        self.assertEqual(response.context['fatura'].competencia, competencia)

    def test_show_com_mes_e_ano(self):
        response = self.client.get(
            reverse('cartao_show_path', args=[self.cartao.id]),
            {'mes': 1, 'ano': 2025}
        )

        self.assertEqual(response.status_code, 200)

        competencia = Competencia.objects.get(mes=1, ano=2025)
        self.assertEqual(
            response.context['fatura'].competencia,
            competencia
        )



class CartaoCreateViewTest(TestCase):

    def test_create_cartao_valido(self):
        response = self.client.post(
            reverse('cartoes_create_path'),
            {
                'descricao': 'C6 Bank',
                'limite': 2500,
                'fechamento': 8,
                'vencimento': 18
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Cartao.objects.filter(descricao='C6 Bank').exists()
        )

    def test_create_cartao_invalido_nao_cria(self):
        response = self.client.post(
            reverse('cartoes_create_path'),
            {
                'descricao': '',
                'limite': ''
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cartao.objects.count(), 0)



class CartaoEditViewTest(TestCase):

    def setUp(self):
        self.cartao = Cartao.objects.create(
            descricao='Original',
            limite=1000,
            fechamento=1,
            vencimento=10
        )

    def test_edit_cartao_atualiza_dados(self):
        response = self.client.post(
            reverse('cartoes_edit_path', args=[self.cartao.id]),
            {
                'descricao': 'Atualizado',
                'limite': 1500,
                'fechamento': 2,
                'vencimento': 12
            }
        )

        self.cartao.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cartao.descricao, 'Atualizado')
        self.assertEqual(self.cartao.limite, 1500)



class CartaoUpdateViewTest(TestCase):

    def setUp(self):
        self.cartao = Cartao.objects.create(
            descricao='Visa',
            limite=4000,
            fechamento=12,
            vencimento=22
        )

    def test_update_cartao(self):
        response = self.client.post(
            reverse('cartoes_edit_path', args=[self.cartao.id]),
            {
                'descricao': 'Visa Platinum',
                'limite': 6000,
                'fechamento': 12,
                'vencimento': 22
            }
        )

        self.cartao.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cartao.descricao, 'Visa Platinum')
