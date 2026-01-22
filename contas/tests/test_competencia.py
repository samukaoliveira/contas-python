from django.test import TestCase
from django.db import IntegrityError
from contas.models import Competencia


class CompetenciaModelTest(TestCase):

    def test_criacao_competencia(self):
        comp = Competencia.objects.create(mes=1, ano=2025)

        self.assertEqual(comp.mes, 1)
        self.assertEqual(comp.ano, 2025)

    def test_str(self):
        comp = Competencia.objects.create(mes=3, ano=2024)

        self.assertEqual(str(comp), '03/2024')

    def test_mes_nome(self):
        comp = Competencia.objects.create(mes=5, ano=2024)

        self.assertEqual(comp.mes_nome(), 'Mai')

    def test_unique_together_mes_ano(self):
        Competencia.objects.create(mes=6, ano=2024)

        with self.assertRaises(IntegrityError):
            Competencia.objects.create(mes=6, ano=2024)

    def test_ordering(self):
        Competencia.objects.create(mes=12, ano=2023)
        Competencia.objects.create(mes=1, ano=2023)
        Competencia.objects.create(mes=5, ano=2022)

        competencias = list(Competencia.objects.all())

        self.assertEqual(
            competencias,
            [
                # ordering = ['ano', 'mes']
                competencias[0],
                competencias[1],
                competencias[2],
            ]
        )

        self.assertEqual(competencias[0].ano, 2022)
        self.assertEqual(competencias[0].mes, 5)

        self.assertEqual(competencias[1].ano, 2023)
        self.assertEqual(competencias[1].mes, 1)

        self.assertEqual(competencias[2].ano, 2023)
        self.assertEqual(competencias[2].mes, 12)
