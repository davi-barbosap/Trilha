"""Calculadora de economia unitária — matemática reversa (núcleo §3.1)."""

from __future__ import annotations

from dataclasses import dataclass, field

from trilha.core.perfil import Economia

SEMANAS_POR_MES = 365.25 / 12 / 7
DEGRAUS = ("lead", "lead_qualificado", "agendamento", "venda")


def receita_bruta_por_venda(e: Economia, valor_do_bem: float | None = None) -> float:
    """Receita real que uma venda gera para o cliente.

    `valor_do_bem` permite usar o valor de um negócio específico (ex.: preço do lead no CRM)
    em vez da média do perfil.
    """
    if e.modelo_receita == "venda_direta":
        return valor_do_bem if valor_do_bem is not None else e.ticket_medio
    if e.modelo_receita == "comissao":
        base = valor_do_bem if valor_do_bem is not None else e.valor_medio_bem
        return base * e.comissao_pct * e.participacao_comissao
    return e.mensalidade * e.meses_retencao


@dataclass
class ResultadoEconomia:
    receita_bruta: float
    cac_max: float
    cpl_max: float
    cpl_qualificado_max: float
    custo_agendamento_max: float | None
    verba_por_degrau: dict[str, float]
    verba_minima_viavel: float
    degraus_viaveis: list[str]
    estimados: list[str] = field(default_factory=list)

    def custo_max(self, evento: str) -> float | None:
        return {
            "lead": self.cpl_max,
            "lead_qualificado": self.cpl_qualificado_max,
            "agendamento": self.custo_agendamento_max,
            "venda": self.cac_max,
        }.get(evento)


def calcular(e: Economia, verba_mensal: float | None = None, eventos_semana: int = 50) -> ResultadoEconomia:
    receita = receita_bruta_por_venda(e)
    cac = receita * e.margem_contribuicao * e.pct_investivel
    cpl = cac * e.taxa_fechamento
    cpl_q = cac * e.taxa_fechamento / e.taxa_qualificacao
    custo_ag = cac * e.taxa_fechamento / e.taxa_agendamento if e.taxa_agendamento else None

    custos = {"lead": cpl, "lead_qualificado": cpl_q, "agendamento": custo_ag, "venda": cac}
    verba_por_degrau = {
        d: eventos_semana * c * SEMANAS_POR_MES for d, c in custos.items() if c is not None
    }
    viaveis = (
        [d for d in DEGRAUS if d in verba_por_degrau and verba_por_degrau[d] <= verba_mensal]
        if verba_mensal is not None
        else []
    )
    return ResultadoEconomia(
        receita_bruta=receita,
        cac_max=cac,
        cpl_max=cpl,
        cpl_qualificado_max=cpl_q,
        custo_agendamento_max=custo_ag,
        verba_por_degrau=verba_por_degrau,
        verba_minima_viavel=verba_por_degrau["lead"],
        degraus_viaveis=viaveis,
        estimados=list(e.estimados),
    )
