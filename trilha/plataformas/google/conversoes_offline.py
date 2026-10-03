"""Google Ads — conversões offline e conversões otimizadas para leads (Google M6, núcleo §7).

Monta o corpo de `customers/{id}:uploadClickConversions` (formato JSON da API REST).
O envio usa a biblioteca oficial `google-ads` (pip install trilha[google]) — próximo passo do MVP.
"""

from __future__ import annotations

import re
from datetime import datetime

from trilha.conversao.hash import hash_email, hash_telefone_google
from trilha.integracoes.kommo import DadosLead


def _so_digitos(customer_id: str) -> str:
    return re.sub(r"\D", "", customer_id)


def formatar_data_hora(quando: datetime) -> str:
    """Formato exigido: 'aaaa-mm-dd hh:mm:ss+hh:mm' (com fuso)."""
    if quando.tzinfo is None:
        raise ValueError("data/hora da conversão precisa de fuso horário")
    texto = quando.strftime("%Y-%m-%d %H:%M:%S%z")
    return texto[:-2] + ":" + texto[-2:]


def montar_conversao(
    customer_id: str,
    conversion_action_id: str,
    dados: DadosLead,
    quando: datetime,
    order_id: str,
    valor: float | None = None,
    moeda: str = "BRL",
) -> dict | None:
    """Uma conversão por identificador de clique; sem ele, por e-mail/telefone em hash. Sem nada, None."""
    cid = _so_digitos(customer_id)
    conversao: dict = {
        "conversionAction": f"customers/{cid}/conversionActions/{conversion_action_id}",
        "conversionDateTime": formatar_data_hora(quando),
        "orderId": order_id,  # deduplicação
    }
    for chave in ("gclid", "gbraid", "wbraid"):  # a API aceita só um
        if dados.ids.get(chave):
            conversao[chave] = dados.ids[chave]
            break

    identificadores = [{"hashedEmail": h} for h in sorted({h for h in map(hash_email, dados.emails) if h})]
    identificadores += [
        {"hashedPhoneNumber": h} for h in sorted({h for h in map(hash_telefone_google, dados.telefones) if h})
    ]
    if identificadores:
        conversao["userIdentifiers"] = identificadores

    if not any(k in conversao for k in ("gclid", "gbraid", "wbraid", "userIdentifiers")):
        return None
    if valor is not None:
        conversao.update(conversionValue=round(valor, 2), currencyCode=moeda)
    return conversao


def montar_requisicao(customer_id: str, conversoes: list[dict]) -> tuple[str, dict]:
    cid = _so_digitos(customer_id)
    return f"customers/{cid}:uploadClickConversions", {"conversions": conversoes, "partialFailure": True}
