"""Webhook do Kommo → eventos padronizados → envios para Meta e Google (núcleo §7).

Modo simulação é o padrão: nada é enviado sem `simular=False` e credenciais no ambiente.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

from trilha.core.economia import calcular, receita_bruta_por_venda
from trilha.core.perfil import Destino, Perfil
from trilha.integracoes.kommo import DadosLead, MudancaEtapa, parse_webhook
from trilha.plataformas.google import conversoes_offline as google
from trilha.plataformas.meta import capi

FUSO_PADRAO = ZoneInfo("America/Sao_Paulo")


@dataclass
class Envio:
    plataforma: str  # meta | google
    evento: str
    lead_id: int
    destino: str | None = None  # URL (Meta) ou recurso (Google)
    corpo: dict | None = None
    pulado: str | None = None  # motivo, quando não há envio (problema a investigar)
    pendente: str | None = None  # envio previsto mas ainda não implementado (não é problema do lead)
    resposta: dict | None = None


def eventos_do_webhook(corpo: str | bytes, perfil: Perfil) -> list[tuple[MudancaEtapa, str]]:
    if perfil.crm is None:
        raise ValueError("perfil sem bloco crm")
    pares = []
    for m in parse_webhook(corpo):
        if m.old_status_id is not None and m.old_status_id == m.status_id:
            continue
        evento = perfil.crm.evento_para(m.status_id, m.pipeline_id)
        if evento:
            pares.append((m, evento))
    return pares


def _valor(destino: Destino, evento: str, dados: DadosLead, perfil: Perfil) -> float | None:
    if destino.valor == "receita":
        # Receita real: em modelo de comissão, o preço do lead no CRM é o valor do bem, não a receita.
        return receita_bruta_por_venda(perfil.economia, dados.valor)
    if destino.valor == "ponderado":
        r = calcular(perfil.economia, eventos_semana=perfil.conversao.eventos_semana_aprendizado)
        return r.custo_max(evento)
    return None


def preparar_envios(m: MudancaEtapa, evento: str, dados: DadosLead, perfil: Perfil, agora: datetime | None = None) -> list[Envio]:
    destino = perfil.conversao.destinos.get(evento)
    if destino is None:
        return [Envio(plataforma="-", evento=evento, lead_id=m.lead_id, pulado="evento de uso interno (sem destino no perfil)")]

    agora = agora or datetime.now(timezone.utc)
    quando = datetime.fromtimestamp(m.atualizado_em, timezone.utc) if m.atualizado_em else agora
    event_id = f"kommo-{m.lead_id}-{evento}"
    valor = _valor(destino, evento, dados, perfil)
    moeda = perfil.verba.moeda
    envios: list[Envio] = []

    meta = perfil.plataformas.meta
    if destino.meta_event_name:
        if not (meta and meta.pixel_id):
            envios.append(Envio("meta", evento, m.lead_id, pulado="perfil sem plataformas.meta.pixel_id"))
        elif not capi.tem_identificador(dados):
            envios.append(Envio("meta", evento, m.lead_id, pulado="lead sem identificador para o Meta"))
        else:
            ev = capi.montar_evento(destino.meta_event_name, int(quando.timestamp()), event_id, dados, valor, moeda, meta.page_id)
            url, corpo = capi.montar_requisicao(meta.pixel_id, [ev], test_event_code=os.environ.get("META_TEST_EVENT_CODE"))
            envios.append(Envio("meta", evento, m.lead_id, destino=url, corpo=corpo))

    g = perfil.plataformas.google
    if destino.google_conversion_action_id:
        if not (g and g.customer_id):
            envios.append(Envio("google", evento, m.lead_id, pulado="perfil sem plataformas.google.customer_id"))
        else:
            ev = google.montar_evento(dados, quando.astimezone(FUSO_PADRAO), event_id, valor, moeda)
            if ev is None:
                envios.append(Envio("google", evento, m.lead_id, pulado="lead sem gclid/gbraid/wbraid nem contato"))
            else:
                url, corpo = google.montar_requisicao(
                    g.customer_id, destino.google_conversion_action_id, [ev], g.login_customer_id,
                    validar_apenas=os.environ.get("GOOGLE_DATA_MANAGER_VALIDAR") == "1",
                )
                envios.append(Envio("google", evento, m.lead_id, destino=url, corpo=corpo))
    return envios


def processar(
    corpo: str | bytes | dict,
    perfil: Perfil,
    obter_dados: Callable[[int], DadosLead],
    agora: datetime | None = None,
) -> list[Envio]:
    """O webhook só diz qual lead olhar: a etapa é confirmada na leitura do próprio Kommo.

    Assim um webhook forjado não gera conversão para uma etapa em que o lead não está.
    """
    envios: list[Envio] = []
    for m, evento in eventos_do_webhook(corpo, perfil):
        dados = obter_dados(m.lead_id)
        if dados.status_id != m.status_id or (
            m.pipeline_id is not None and dados.pipeline_id is not None and dados.pipeline_id != m.pipeline_id
        ):
            envios.append(Envio("-", evento, m.lead_id, pulado=(
                f"etapa não confirmada no Kommo (webhook: {m.status_id}, lead agora: {dados.status_id})"
            )))
            continue
        envios += preparar_envios(m, evento, dados, perfil, agora)
    return envios


def executar(envios: list[Envio], simular: bool = True, log_dir: str | Path | None = None) -> list[Envio]:
    """Envia (ou só registra, em simulação). O envio ao Google (Data Manager API, OAuth) ainda não está ligado."""
    for e in envios:
        if e.pulado or e.pendente or simular:
            continue
        if e.plataforma == "meta":
            e.resposta = capi.enviar(e.destino, e.corpo, os.environ["META_ACCESS_TOKEN"])
        elif e.plataforma == "google":
            e.pendente = "envio ao Google ainda não implementado (ROADMAP) — payload registrado"
    log_dir = log_dir or os.environ.get("TRILHA_LOG_DIR")
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        with open(Path(log_dir) / "envios.jsonl", "a", encoding="utf-8") as f:
            for e in envios:
                f.write(json.dumps({"simulado": simular, **asdict(e)}, ensure_ascii=False) + "\n")
    return envios
