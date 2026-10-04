"""Correções confirmadas com o cliente (`clientes/<id>/correcoes.yaml`).

Erros de cadastro no Kommo que o time do cliente confirmou (negócio duplicado, venda fechada
no sistema com data errada) ficam registrados aqui, com o motivo e quem confirmou, em vez de
viverem escondidos no código ou no painel. A coleta aplica antes de qualquer cálculo.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

from trilha.core.funil import LeadFunil


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Exclusao(_Base):
    lead_id: int
    motivo: str
    confirmado_por: str


class DataDaVenda(_Base):
    lead_id: int
    data: date
    motivo: str
    confirmado_por: str


class Correcoes(_Base):
    excluir: list[Exclusao] = []
    data_da_venda: list[DataDaVenda] = []


def carregar_correcoes(caminho: str | Path) -> Correcoes:
    caminho = Path(caminho)
    if not caminho.is_file():
        return Correcoes()
    with open(caminho, encoding="utf-8") as f:
        return Correcoes.model_validate(yaml.safe_load(f) or {})


def aplicar_correcoes(leads: list[LeadFunil], correcoes: Correcoes) -> list[LeadFunil]:
    excluidos = {e.lead_id for e in correcoes.excluir}
    datas = {d.lead_id: d.data for d in correcoes.data_da_venda}
    saida = []
    for l in leads:
        if l.lead_id in excluidos:
            continue
        if l.lead_id in datas and l.vendido():
            l = l.model_copy(deep=True)
            original = l.etapas["venda"]
            l.etapas["venda"] = datetime.combine(datas[l.lead_id], original.timetz() if original.tzinfo else time(12, tzinfo=timezone.utc))
        saida.append(l)
    return saida
