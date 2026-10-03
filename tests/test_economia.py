import unittest

from trilha.core.economia import SEMANAS_POR_MES, calcular, receita_bruta_por_venda
from trilha.core.perfil import Economia

IMOB = dict(
    modelo_receita="comissao", valor_medio_bem=450_000, comissao_pct=0.05, participacao_comissao=0.5,
    margem_contribuicao=0.5, pct_investivel=0.5, taxa_fechamento=0.01, taxa_qualificacao=0.25, taxa_agendamento=0.05,
)


class TestEconomia(unittest.TestCase):
    def test_comissao_nao_usa_valor_do_imovel_como_receita(self):
        e = Economia(**IMOB)
        self.assertAlmostEqual(receita_bruta_por_venda(e), 11_250)
        self.assertAlmostEqual(receita_bruta_por_venda(e, 600_000), 15_000)

    def test_exemplo_do_nucleo(self):
        r = calcular(Economia(**IMOB), verba_mensal=8_000)
        self.assertAlmostEqual(r.cac_max, 2_812.5)
        self.assertAlmostEqual(r.cpl_max, 28.125)
        self.assertAlmostEqual(r.cpl_qualificado_max, 112.5)
        self.assertAlmostEqual(r.custo_agendamento_max, 562.5)
        self.assertAlmostEqual(r.verba_por_degrau["lead"], 50 * 28.125 * SEMANAS_POR_MES)
        self.assertEqual(r.verba_minima_viavel, r.verba_por_degrau["lead"])
        self.assertEqual(r.degraus_viaveis, ["lead"])

    def test_venda_direta_e_recorrencia(self):
        base = {k: v for k, v in IMOB.items() if k not in ("modelo_receita", "valor_medio_bem", "comissao_pct", "participacao_comissao")}
        self.assertEqual(receita_bruta_por_venda(Economia(modelo_receita="venda_direta", ticket_medio=3000, **base)), 3000)
        self.assertEqual(receita_bruta_por_venda(Economia(modelo_receita="recorrencia", mensalidade=300, meses_retencao=14, **base)), 4200)

    def test_sem_agendamento_nao_quebra(self):
        r = calcular(Economia(**{**IMOB, "taxa_agendamento": None}))
        self.assertIsNone(r.custo_agendamento_max)
        self.assertNotIn("agendamento", r.verba_por_degrau)

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            Economia(**{**IMOB, "comissao_pct": None})
        with self.assertRaises(ValueError):
            Economia(**{**IMOB, "taxa_qualificacao": 0.005})
        with self.assertRaises(ValueError):
            Economia(**{**IMOB, "taxa_agendamento": 0.5})
        with self.assertRaises(ValueError):
            Economia(**{**IMOB, "estimados": ["campo_que_nao_existe"]})


if __name__ == "__main__":
    unittest.main()
