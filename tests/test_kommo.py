import json
import unittest
from pathlib import Path

from trilha.integracoes.kommo import extrair_dados_lead, parse_webhook, subdominio_do_webhook

FIX = Path(__file__).parent / "fixtures"
CAMPOS = {"gclid": "gclid", "fbclid": "fbclid", "ctwa_clid": "ctwa_clid", "utm_content": "utm_content", "utm_source": "504"}


class TestKommo(unittest.TestCase):
    def test_parse_webhook_mudanca_de_etapa(self):
        [m] = parse_webhook((FIX / "kommo_webhook.txt").read_text())
        self.assertEqual((m.lead_id, m.status_id, m.pipeline_id, m.old_status_id), (987654, 3333, 1111, 2222))
        self.assertEqual(m.atualizado_em, 1790000000)
        self.assertEqual(m.tipo, "status")

    def test_parse_webhook_varios_e_lead_novo(self):
        corpo = (
            "leads[add][0][id]=1&leads[add][0][status_id]=2222&leads[add][0][pipeline_id]=1111"
            "&leads[status][0][id]=2&leads[status][0][status_id]=142&leads[status][0][pipeline_id]=1111"
            "&leads[status][1][id]=3&leads[status][1][status_id]="  # incompleto: ignorado
        )
        ms = parse_webhook(corpo.encode())
        self.assertEqual([(m.tipo, m.lead_id, m.status_id) for m in ms], [("add", 1, 2222), ("status", 2, 142)])

    def test_extrair_dados(self):
        lead = json.loads((FIX / "kommo_lead.json").read_text())
        contato = json.loads((FIX / "kommo_contato.json").read_text())
        d = extrair_dados_lead(lead, [contato], CAMPOS)
        self.assertEqual(d.ids, {"gclid": "Cj0KCQjw-exemplo", "fbclid": "IwAR-exemplo"})
        self.assertEqual(d.utm["utm_source"], "google")  # casado pelo field_id
        self.assertTrue(d.utm["utm_content"].startswith("PRECO_"))
        self.assertEqual(d.valor, 560000)
        self.assertEqual((d.status_id, d.pipeline_id), (3333, 1111))
        self.assertEqual(d.telefones, ["+55 (11) 98765-4321"])
        self.assertEqual(len(d.emails), 1)


    def test_subdominio_do_webhook(self):
        self.assertEqual(subdominio_do_webhook((FIX / "kommo_webhook.txt").read_text()), "imobiliaria-exemplo")
        self.assertEqual(subdominio_do_webhook({"account": {"subdomain": "outra"}}), "outra")
        self.assertIsNone(subdominio_do_webhook({"leads": {}}))


if __name__ == "__main__":
    unittest.main()
