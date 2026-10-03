import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from trilha.conversao.hash import hash_email
from trilha.conversao.pipeline import eventos_do_webhook, executar, processar
from trilha.core.perfil import carregar_perfil
from trilha.integracoes.kommo import DadosLead, extrair_dados_lead
from trilha.plataformas.google.conversoes_offline import formatar_data_hora

RAIZ = Path(__file__).resolve().parents[1]
FIX = RAIZ / "tests" / "fixtures"


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.perfil = carregar_perfil(RAIZ / "clientes" / "_exemplo" / "perfil.yaml")
        lead = json.loads((FIX / "kommo_lead.json").read_text())
        contato = json.loads((FIX / "kommo_contato.json").read_text())
        self.dados = extrair_dados_lead(lead, [contato], self.perfil.crm.campos)
        self.webhook = (FIX / "kommo_webhook.txt").read_text()

    def test_lead_qualificado_vai_para_meta_e_google(self):
        envios = executar(processar(self.webhook, self.perfil, lambda _: self.dados), simular=True)
        meta, google = envios
        self.assertEqual((meta.plataforma, meta.evento), ("meta", "lead_qualificado"))
        self.assertTrue(meta.destino.endswith("/000000000000000/events"))
        ev = meta.corpo["data"][0]
        self.assertEqual(ev["event_name"], "LeadQualificado")
        self.assertEqual(ev["event_id"], "kommo-987654-lead_qualificado")
        self.assertEqual(ev["action_source"], "system_generated")
        self.assertEqual(ev["user_data"]["em"], [hash_email("cliente.exemplo@email.com")])
        self.assertEqual(ev["user_data"]["fbc"], "fb.1.1789900000000.IwAR-exemplo")
        self.assertAlmostEqual(ev["custom_data"]["value"], 112.5)  # valor ponderado = CPL qualificado máximo
        self.assertNotIn("access_token", json.dumps(meta.corpo))

        self.assertEqual(google.destino, "customers/1234567890:uploadClickConversions")
        conv = google.corpo["conversions"][0]
        self.assertEqual(conv["gclid"], "Cj0KCQjw-exemplo")
        self.assertEqual(conv["conversionAction"], "customers/1234567890/conversionActions/900000002")
        self.assertEqual(conv["orderId"], "kommo-987654-lead_qualificado")
        self.assertTrue(conv["conversionDateTime"].endswith("-03:00"))
        self.assertTrue(google.corpo["partialFailure"])

    def test_venda_usa_receita_da_comissao_e_nao_o_valor_do_imovel(self):
        corpo = "leads[status][0][id]=987654&leads[status][0][status_id]=142&leads[status][0][pipeline_id]=1111"
        meta, google = processar(corpo, self.perfil, lambda _: self.dados)
        self.assertEqual(meta.corpo["data"][0]["event_name"], "Purchase")
        self.assertAlmostEqual(meta.corpo["data"][0]["custom_data"]["value"], 560000 * 0.05 * 0.5)
        self.assertAlmostEqual(google.corpo["conversions"][0]["conversionValue"], 14000)

    def test_whatsapp_usa_business_messaging(self):
        dados = DadosLead(lead_id=1, ids={"ctwa_clid": "ARAkLk-exemplo"})
        corpo = "leads[status][0][id]=1&leads[status][0][status_id]=3333&leads[status][0][pipeline_id]=1111"
        meta, google = processar(corpo, self.perfil, lambda _: dados)
        ev = meta.corpo["data"][0]
        self.assertEqual(ev["action_source"], "business_messaging")
        self.assertEqual(ev["messaging_channel"], "whatsapp")
        self.assertEqual(ev["user_data"], {"ctwa_clid": "ARAkLk-exemplo", "page_id": "000000000000000"})
        self.assertIsNone(google.corpo)
        self.assertIn("sem gclid", google.pulado)

    def test_eventos_internos_e_etapa_repetida(self):
        perdido = "leads[status][0][id]=1&leads[status][0][status_id]=143&leads[status][0][pipeline_id]=1111"
        [e] = processar(perdido, self.perfil, lambda _: self.dados)
        self.assertEqual(e.evento, "desqualificado")
        self.assertIn("uso interno", e.pulado)

        repetido = "leads[status][0][id]=1&leads[status][0][status_id]=3333&leads[status][0][pipeline_id]=1111&leads[status][0][old_status_id]=3333"
        self.assertEqual(eventos_do_webhook(repetido, self.perfil), [])

        desconhecido = "leads[status][0][id]=1&leads[status][0][status_id]=7777&leads[status][0][pipeline_id]=1111"
        self.assertEqual(processar(desconhecido, self.perfil, lambda _: self.dados), [])

    def test_lead_sem_identificador(self):
        corpo = "leads[status][0][id]=1&leads[status][0][status_id]=3333&leads[status][0][pipeline_id]=1111"
        meta, google = processar(corpo, self.perfil, lambda _: DadosLead(lead_id=1))
        self.assertIn("sem identificador", meta.pulado)
        self.assertIn("sem gclid", google.pulado)

    def test_data_hora_google_exige_fuso(self):
        self.assertEqual(formatar_data_hora(datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)), "2026-10-03 12:00:00+00:00")
        with self.assertRaises(ValueError):
            formatar_data_hora(datetime(2026, 10, 3, 12, 0))


if __name__ == "__main__":
    unittest.main()
