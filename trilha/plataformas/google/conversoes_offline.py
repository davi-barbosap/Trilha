"""Google Ads — conversões offline pela Data Manager API (Google M6, núcleo §7).

Desde 15/06/2026 a Google não aceita novos integradores em
`ConversionUploadService.UploadClickConversions` (Google Ads API): conversões offline
entram pela Data Manager API (`POST https://datamanager.googleapis.com/v1/events:ingest`).
Este módulo monta o corpo dessa chamada. Antes do primeiro envio real, conferir os campos
na referência oficial e testar com `validateOnly: true`.
"""

from __future__ import annotations

import re
from datetime import datetime

from trilha.conversao.hash import hash_email, hash_telefone_google
from trilha.integracoes.kommo import DadosLead

URL_INGESTAO = "https://datamanager.googleapis.com/v1/events:ingest"


def _so_digitos(customer_id: str) -> str:
    return re.sub(r"\D", "", customer_id)


def formatar_data_hora(quando: datetime) -> str:
    """RFC 3339 com fuso (ex.: 2026-10-03T12:00:00-03:00)."""
    if quando.tzinfo is None:
        raise ValueError("data/hora da conversão precisa de fuso horário")
    return quando.isoformat(timespec="seconds")


def montar_evento(
    dados: DadosLead,
    quando: datetime,
    transaction_id: str,
    valor: float | None = None,
    moeda: str = "BRL",
) -> dict | None:
    """Um evento por identificador de clique; sem ele, por e-mail/telefone em hash. Sem nada, None."""
    evento: dict = {
        "eventTimestamp": formatar_data_hora(quando),
        "transactionId": transaction_id,  # deduplicação
    }
    for chave in ("gclid", "gbraid", "wbraid"):  # um só identificador de clique
        if dados.ids.get(chave):
            evento["adIdentifiers"] = {chave: dados.ids[chave]}
            break

    identificadores = [{"emailAddress": h} for h in sorted({h for h in map(hash_email, dados.emails) if h})]
    identificadores += [
        {"phoneNumber": h} for h in sorted({h for h in map(hash_telefone_google, dados.telefones) if h})
    ]
    if identificadores:
        evento["userData"] = {"userIdentifiers": identificadores}

    if "adIdentifiers" not in evento and "userData" not in evento:
        return None
    if valor is not None:
        evento.update(conversionValue=round(valor, 2), currency=moeda)
    return evento


def montar_requisicao(
    customer_id: str,
    conversion_action_id: str,
    eventos: list[dict],
    login_customer_id: str | None = None,
    validar_apenas: bool = False,
) -> tuple[str, dict]:
    destino: dict = {
        "operatingAccount": {"accountType": "GOOGLE_ADS", "accountId": _so_digitos(customer_id)},
        "productDestinationId": str(conversion_action_id),
    }
    if login_customer_id:  # acesso pela MCC da agência
        destino["loginAccount"] = {"accountType": "GOOGLE_ADS", "accountId": _so_digitos(login_customer_id)}
    corpo = {"destinations": [destino], "encoding": "HEX", "events": eventos}
    if validar_apenas:
        corpo["validateOnly"] = True
    return URL_INGESTAO, corpo
