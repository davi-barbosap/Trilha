"""Normalização e hash SHA-256 de dados de contato (LGPD: dado pessoal só sai em hash)."""

from __future__ import annotations

import hashlib
import re


def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def normalizar_email(email: str) -> str | None:
    email = email.strip().lower()
    return email if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) else None


def normalizar_telefone(telefone: str, ddi_padrao: str = "55") -> str | None:
    """Só dígitos, com DDI. Números brasileiros sem DDI (10–11 dígitos) recebem o padrão."""
    digitos = re.sub(r"\D", "", telefone)
    if telefone.strip().startswith("00"):
        digitos = digitos[2:]
    if len(digitos) in (10, 11) and not telefone.strip().startswith("+"):
        digitos = ddi_padrao + digitos
    return digitos if 11 <= len(digitos) <= 15 else None


def hash_email(email: str) -> str | None:
    n = normalizar_email(email)
    return sha256(n) if n else None


def hash_telefone_meta(telefone: str) -> str | None:
    """Meta: dígitos com DDI, sem '+'."""
    n = normalizar_telefone(telefone)
    return sha256(n) if n else None


def hash_telefone_google(telefone: str) -> str | None:
    """Google: formato E.164 (com '+') antes do hash."""
    n = normalizar_telefone(telefone)
    return sha256("+" + n) if n else None
