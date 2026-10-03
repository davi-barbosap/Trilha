import hashlib
import unittest

from trilha.conversao.hash import hash_email, hash_telefone_google, hash_telefone_meta, normalizar_email, normalizar_telefone


class TestHash(unittest.TestCase):
    def test_email(self):
        self.assertEqual(normalizar_email("  Fulano@Exemplo.COM "), "fulano@exemplo.com")
        self.assertIsNone(normalizar_email("sem-arroba"))
        self.assertEqual(hash_email("test@example.com"), "973dfe463ec85785f5f95af5ba3906eedb2d931c24e69824a89ea65dba4e813b")

    def test_telefone(self):
        self.assertEqual(normalizar_telefone("+55 (11) 98765-4321"), "5511987654321")
        self.assertEqual(normalizar_telefone("(11) 98765-4321"), "5511987654321")
        self.assertEqual(normalizar_telefone("0055 11 98765-4321"), "5511987654321")
        self.assertIsNone(normalizar_telefone("1234"))

    def test_formatos_por_plataforma(self):
        self.assertEqual(hash_telefone_meta("(11) 98765-4321"), hashlib.sha256(b"5511987654321").hexdigest())
        self.assertEqual(hash_telefone_google("(11) 98765-4321"), hashlib.sha256(b"+5511987654321").hexdigest())


if __name__ == "__main__":
    unittest.main()
