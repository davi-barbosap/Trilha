"""Esquema validado de `ofertas/<oferta>.yaml`, com o diagnóstico de aderência ao digital.

As respostas da aderência são do assessor. O sistema só confere se foram dadas e leva
os sinais de risco para o dossiê e para o pacote de briefing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

Avaliacao = Literal["boa", "regular", "fraca", "nao_avaliado"]


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Identificacao(_Base):
    nome: str
    tipo: str  # empreendimento, curso, serviço, produto…
    estagio: str = ""
    localizacao: dict[str, str] = Field(default_factory=dict)
    construtora: str = ""  # quem entrega (incorporadora, escola, clínica…)
    tipologia: str = ""  # tipologias e metragens, turmas, planos…
    plantas: str = ""


class Objecao(_Base):
    eixo: str
    objecao: str
    resposta_do_time: str


class VendasForaDoDigital(_Base):
    canais: list[str] = Field(default_factory=list)  # plantão, indicação, presencial…
    ritmo: str = ""  # ex.: "8 unidades/mês", "60% vendido em 10 meses"
    avaliacao: Avaliacao = "nao_avaliado"


class Aderencia(_Base):
    """Diagnóstico antes de anunciar: o produto tem aderência ao digital?"""

    perfil_compradores: str = ""  # perfil financeiro, onde moram, o que fazem, o que motivou a compra
    finalidade: Literal["uso_proprio", "investimento", "ambos", "nao_avaliado"] = "nao_avaliado"
    pagamento_flexivel: bool | None = None
    pagamento_comunicavel: str = ""
    reputacao: Literal["ativo", "neutra", "obstaculo", "nao_avaliado"] = "nao_avaliado"
    reputacao_nota: str = ""
    vendas_fora_do_digital: VendasForaDoDigital = Field(default_factory=VendasForaDoDigital)
    aderencia_digital: Literal["alta", "media", "baixa", "nao_avaliado"] = "nao_avaliado"
    justificativa: str = ""

    def pendencias(self) -> list[str]:
        faltando = []
        if not self.perfil_compradores:
            faltando.append("perfil dos compradores")
        if self.finalidade == "nao_avaliado":
            faltando.append("finalidade (uso próprio ou investimento)")
        if self.pagamento_flexivel is None:
            faltando.append("flexibilidade de pagamento")
        if self.reputacao == "nao_avaliado":
            faltando.append("reputação")
        if self.vendas_fora_do_digital.avaliacao == "nao_avaliado":
            faltando.append("vendas fora do digital")
        if self.aderencia_digital == "nao_avaliado":
            faltando.append("aderência ao digital (avaliação do assessor)")
        return faltando

    def sinais_de_risco(self) -> list[str]:
        sinais = []
        if self.vendas_fora_do_digital.avaliacao == "fraca":
            sinais.append(
                "vendas fracas fora do digital: o digital tende a expor o problema mais rápido e mais caro — "
                "nutrição mais longa, prova social mais robusta, contorno de objeção já no criativo"
            )
        if self.aderencia_digital == "baixa":
            sinais.append("aderência ao digital avaliada como baixa: rever estratégia antes de escalar verba")
        if self.reputacao == "obstaculo":
            sinais.append("reputação é um obstáculo: tratar a objeção no criativo e no atendimento")
        return sinais


class Oferta(_Base):
    oferta: Identificacao
    aderencia: Aderencia = Field(default_factory=Aderencia)
    diferenciais: list[str] = Field(default_factory=list)
    raridade: str = ""
    ancoras: list[str] = Field(default_factory=list)  # nome próprio + distância ou tempo
    vias_acesso: str = ""
    valorizacao: str = ""
    critica_localizacao: str = ""  # o que o lead costuma criticar na localização
    condicoes_comerciais: dict[str, str | float | int | None] = Field(default_factory=dict)
    objecoes: list[Objecao] = Field(default_factory=list)
    objecoes_avulsas: str = ""
    perfil_lead: dict[str, str | int | None] = Field(default_factory=dict)
    assets: dict[str, list[str]] = Field(default_factory=dict)


def carregar_oferta(caminho: str | Path) -> Oferta:
    with open(caminho, encoding="utf-8") as f:
        return Oferta.model_validate(yaml.safe_load(f))
