"""Janelas de comparação e leitura da variação (régua da Trilha).

- Comparação com a janela imediatamente anterior, do mesmo número de dias.
- Mês corrente: do dia 1 ao dia D contra o dia 1 ao dia D do mês anterior (D limitado ao fim daquele mês).
- Taxa varia em pontos percentuais; volume, custo e valor variam em %. |Δ| < 0,5% é estável.
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta

ESTAVEL = 0.005


def janela_anterior(inicio: date, fim: date) -> tuple[date, date]:
    """Mesmo número de dias, imediatamente antes (inclusivo nas duas pontas): 7 dias comparam com 7."""
    dias = (fim - inicio).days + 1
    return inicio - timedelta(days=dias), inicio - timedelta(days=1)


def mes_corrente_anterior(hoje: date) -> tuple[date, date]:
    """Do dia 1 ao mesmo dia do mês anterior, para o acompanhamento do mês ser comparável."""
    ano, mes = (hoje.year - 1, 12) if hoje.month == 1 else (hoje.year, hoje.month - 1)
    return date(ano, mes, 1), date(ano, mes, min(hoje.day, calendar.monthrange(ano, mes)[1]))


def variacao(atual: float | None, anterior: float | None, taxa: bool = False) -> dict:
    """{'valor': Δ, 'unidade': 'pp' | '%', 'leitura': 'subiu' | 'caiu' | 'estável' | 'sem base'}."""
    if atual is None or anterior is None or (not taxa and anterior <= 0):
        return {"valor": None, "unidade": "pp" if taxa else "%", "leitura": "sem base"}
    delta = (atual - anterior) * 100 if taxa else (atual - anterior) / anterior * 100
    estavel = abs(atual - anterior) < ESTAVEL if taxa else abs(delta) < ESTAVEL * 100
    return {"valor": round(delta, 1), "unidade": "pp" if taxa else "%",
            "leitura": "estável" if estavel else "subiu" if delta > 0 else "caiu"}
