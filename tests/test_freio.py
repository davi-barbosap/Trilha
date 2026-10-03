import copy
import unittest
from pathlib import Path

import yaml

from trilha.core.freio import MetricaCampanha, avaliar
from trilha.core.perfil import Perfil

EXEMPLO = Path(__file__).resolve().parents[1] / "clientes" / "_exemplo" / "perfil.yaml"


class TestFreio(unittest.TestCase):
    def setUp(self):
        self.bruto = yaml.safe_load(EXEMPLO.read_text(encoding="utf-8"))
        self.perfil = Perfil.model_validate(self.bruto)  # CPL máximo = R$ 28,125 → limite 3× = R$ 84,375

    def test_gasto_sem_lead(self):
        acoes = avaliar(self.perfil, [
            MetricaCampanha("meta", "c1", "Conversão", gasto_desde_ultimo_lead=90),
            MetricaCampanha("meta", "c2", "Teste", gasto_desde_ultimo_lead=80),
            MetricaCampanha("meta", "c3", "Pausada", ativa=False, gasto_desde_ultimo_lead=500),
        ])
        self.assertEqual([(a.campanha_id, a.acao, a.gatilho) for a in acoes], [("c1", "pausar", "gasto_sem_lead")])
        self.assertIn("R$ 84,38", acoes[0].motivo)

    def test_rastreamento_quebrado(self):
        acoes = avaliar(self.perfil, [
            MetricaCampanha("google", "g1", horas_sem_evento_conversao=8, gasto_ultimas_horas=40),
            MetricaCampanha("google", "g2", horas_sem_evento_conversao=8, gasto_ultimas_horas=0),  # parada: nada a proteger
            MetricaCampanha("google", "g3", horas_sem_evento_conversao=3, gasto_ultimas_horas=40),
            MetricaCampanha("google", "g4", horas_sem_evento_conversao=None, gasto_ultimas_horas=40),
        ])
        self.assertEqual([(a.campanha_id, a.gatilho) for a in acoes], [("g1", "rastreamento_quebrado")])

    def test_opcao_b_so_avisa_e_ordem_por_valor(self):
        bruto = copy.deepcopy(self.bruto)
        bruto["freio"]["modo"] = "avisar"
        acoes = avaliar(Perfil.model_validate(bruto), [
            MetricaCampanha("meta", "pequena", gasto_desde_ultimo_lead=100),
            MetricaCampanha("meta", "grande", gasto_desde_ultimo_lead=400),
        ])
        self.assertEqual([a.campanha_id for a in acoes], ["grande", "pequena"])
        self.assertTrue(all(a.acao == "avisar" for a in acoes))


if __name__ == "__main__":
    unittest.main()
