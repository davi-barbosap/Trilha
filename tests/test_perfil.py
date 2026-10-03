import copy
import unittest
from pathlib import Path

import yaml
from pydantic import ValidationError

from trilha.core.perfil import Perfil, carregar_perfil

EXEMPLO = Path(__file__).resolve().parents[1] / "clientes" / "_exemplo" / "perfil.yaml"


class TestPerfil(unittest.TestCase):
    def setUp(self):
        self.bruto = yaml.safe_load(EXEMPLO.read_text(encoding="utf-8"))

    def test_exemplo_valido(self):
        p = carregar_perfil(EXEMPLO)
        self.assertEqual(p.cliente.segmento, "imobiliario")
        self.assertEqual(p.nivel("orcamento"), "L1")
        self.assertEqual(p.nivel("aumento_acima_teto"), "L3")

    def test_mapa_inclui_etapas_de_sistema_do_kommo(self):
        crm = carregar_perfil(EXEMPLO).crm
        self.assertEqual(crm.evento_para(3333, 1111), "lead_qualificado")
        self.assertIsNone(crm.evento_para(3333, 9999))  # outro funil
        self.assertEqual(crm.evento_para(142, 9999), "venda")
        self.assertEqual(crm.evento_para(143, None), "desqualificado")

    def test_autonomia_l3_nao_pode_ser_automatica(self):
        bruto = copy.deepcopy(self.bruto)
        bruto["autonomia"]["aumento_acima_teto"] = "L2"
        with self.assertRaises(ValidationError):
            Perfil.model_validate(bruto)

    def test_campo_desconhecido_e_rejeitado(self):
        bruto = copy.deepcopy(self.bruto)
        bruto["verba"]["mensal_planejda"] = 1
        with self.assertRaises(ValidationError):
            Perfil.model_validate(bruto)

    def test_evento_invalido_no_mapa(self):
        bruto = copy.deepcopy(self.bruto)
        bruto["crm"]["mapa_eventos"][0]["evento"] = "visita"
        with self.assertRaises(ValidationError):
            Perfil.model_validate(bruto)


if __name__ == "__main__":
    unittest.main()
