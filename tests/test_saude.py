import unittest

from trilha.core.saude import ContaAnuncio, avaliar_conta, saude_do_cliente


class TestSaudeConta(unittest.TestCase):
    def test_dias_de_saldo_e_recarga(self):
        r = avaliar_conta(ContaAnuncio(nome="Conta A", saldo=280, gasto_7d=700), "Bruno")  # queima 100/dia
        self.assertEqual((r["dias_de_saldo"], r["recarga_30_dias"]), (2, 3000))
        self.assertEqual(r["alertas"][0]["nivel"], "P1")
        self.assertEqual(r["alertas"][0]["responsavel"], "Bruno")

    def test_niveis(self):
        def nivel(**kw):
            a = avaliar_conta(ContaAnuncio(nome="x", **kw), "A")["alertas"]
            return a[0]["nivel"] if a else None
        self.assertEqual(nivel(saldo=800, gasto_7d=700), "P2")  # 8 dias
        self.assertIsNone(nivel(saldo=2000, gasto_7d=700))  # 20 dias
        self.assertEqual(nivel(saldo=0, gasto_7d=700), "P1")
        self.assertEqual(nivel(status=202, saldo=5000, gasto_7d=700), "P1")
        self.assertIsNone(nivel(saldo=None, gasto_7d=700))  # pós-paga

    def test_cor_do_cliente(self):
        contas = [ContaAnuncio(nome="a", saldo=5000, gasto_7d=700), ContaAnuncio(nome="b", saldo=800, gasto_7d=700)]
        self.assertEqual(saude_do_cliente(contas, "A")["saude"], "amarelo")
        self.assertEqual(saude_do_cliente(contas[:1], "A")["saude"], "verde")


if __name__ == "__main__":
    unittest.main()
