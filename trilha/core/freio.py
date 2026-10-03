"""Freio de emergência (ADR-008): protege a verba entre as sessões semanais de otimização.

Só dois gatilhos, ambos de "dinheiro saindo sem retorno possível". Todo o resto
vira sugestão no dossiê semanal, decidida pelo responsável.
"""

from __future__ import annotations

from dataclasses import dataclass

from trilha.core.economia import calcular
from trilha.core.perfil import Perfil


@dataclass
class MetricaCampanha:
    plataforma: str  # meta | google
    campanha_id: str
    nome: str = ""
    ativa: bool = True
    gasto_desde_ultimo_lead: float = 0.0
    horas_sem_evento_conversao: float | None = None  # None = não medido
    gasto_ultimas_horas: float = 0.0  # gasto na mesma janela de horas_sem_evento_conversao


@dataclass
class AcaoFreio:
    acao: str  # pausar | avisar
    plataforma: str
    campanha_id: str
    nome: str
    gatilho: str  # gasto_sem_lead | rastreamento_quebrado
    motivo: str
    valor_em_risco: float


def _brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def avaliar(perfil: Perfil, campanhas: list[MetricaCampanha]) -> list[AcaoFreio]:
    freio = perfil.freio
    cpl_max = calcular(perfil.economia).cpl_max
    limite_gasto = freio.gasto_sem_lead_multiplo * cpl_max
    acoes: list[AcaoFreio] = []
    for c in campanhas:
        if not c.ativa:
            continue
        if c.gasto_desde_ultimo_lead >= limite_gasto:
            acoes.append(AcaoFreio(
                freio.modo, c.plataforma, c.campanha_id, c.nome, "gasto_sem_lead",
                f"gastou {_brl(c.gasto_desde_ultimo_lead)} desde o último lead "
                f"(limite: {freio.gasto_sem_lead_multiplo:g}× CPL máximo = {_brl(limite_gasto)})",
                c.gasto_desde_ultimo_lead,
            ))
        elif (
            c.horas_sem_evento_conversao is not None
            and c.horas_sem_evento_conversao >= freio.horas_rastreamento_quebrado
            and c.gasto_ultimas_horas > 0
        ):
            acoes.append(AcaoFreio(
                freio.modo, c.plataforma, c.campanha_id, c.nome, "rastreamento_quebrado",
                f"{c.horas_sem_evento_conversao:g}h gastando ({_brl(c.gasto_ultimas_horas)}) sem nenhum evento "
                "de conversão registrado — possível pixel/tag/integração quebrada",
                c.gasto_ultimas_horas,
            ))
    return sorted(acoes, key=lambda a: a.valor_em_risco, reverse=True)
