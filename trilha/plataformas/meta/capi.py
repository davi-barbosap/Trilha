"""Meta — API de Conversões: eventos de qualidade de lead vindos do CRM (Meta §5, núcleo §7)."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from trilha.conversao.hash import hash_email, hash_telefone_meta
from trilha.integracoes.kommo import DadosLead

VERSAO_PADRAO = os.environ.get("META_GRAPH_VERSION", "v23.0")  # conferir a versão vigente da Graph API


def tem_identificador(dados: DadosLead) -> bool:
    return bool(
        dados.ids.get("ctwa_clid") or dados.ids.get("meta_lead_id") or dados.ids.get("fbclid")
        or dados.emails or dados.telefones
    )


def montar_evento(
    event_name: str,
    event_time: int,
    event_id: str,
    dados: DadosLead,
    valor: float | None = None,
    moeda: str = "BRL",
    page_id: str | None = None,
) -> dict:
    """Monta um evento da API de Conversões.

    Lead vindo de anúncio de clique para WhatsApp (tem ctwa_clid) usa action_source
    business_messaging; os demais usam system_generated com origem CRM.
    """
    user_data: dict = {}
    em = sorted({h for h in map(hash_email, dados.emails) if h})
    ph = sorted({h for h in map(hash_telefone_meta, dados.telefones) if h})
    if em:
        user_data["em"] = em
    if ph:
        user_data["ph"] = ph

    custom_data: dict = {}
    if valor is not None:
        custom_data.update(value=round(valor, 2), currency=moeda)

    evento: dict = {"event_name": event_name, "event_time": int(event_time), "event_id": event_id}

    if dados.ids.get("ctwa_clid"):
        user_data["ctwa_clid"] = dados.ids["ctwa_clid"]
        if page_id:
            user_data["page_id"] = page_id
        evento.update(action_source="business_messaging", messaging_channel="whatsapp")
    else:
        if dados.ids.get("meta_lead_id"):
            user_data["lead_id"] = dados.ids["meta_lead_id"]
        if dados.ids.get("fbclid"):
            criado_ms = int((dados.criado_em or event_time) * 1000)
            user_data["fbc"] = f"fb.1.{criado_ms}.{dados.ids['fbclid']}"
        evento["action_source"] = "system_generated"
        custom_data.update(event_source="crm", lead_event_source="Kommo")

    evento["user_data"] = user_data
    if custom_data:
        evento["custom_data"] = custom_data
    return evento


def montar_requisicao(pixel_id: str, eventos: list[dict], versao: str = VERSAO_PADRAO, test_event_code: str | None = None) -> tuple[str, dict]:
    """URL e corpo do POST — sem o token de acesso, que só entra no envio."""
    corpo: dict = {"data": eventos}
    if test_event_code:
        corpo["test_event_code"] = test_event_code
    return f"https://graph.facebook.com/{versao}/{pixel_id}/events", corpo


def enviar(url: str, corpo: dict, access_token: str, tentativas: int = 4) -> dict:
    dados = json.dumps({**corpo, "access_token": access_token}).encode("utf-8")
    req = urllib.request.Request(url, data=dados, headers={"Content-Type": "application/json"}, method="POST")
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if (e.code < 500 and e.code != 429) or tentativa == tentativas - 1:
                raise
        time.sleep(2 ** (tentativa + 1))
    raise RuntimeError("inalcançável")
