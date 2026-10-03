"""Esquema validado do perfil.yaml do cliente (núcleo §4, §7.2, §10; modelo-operacional.md).

O perfil é o contrato entre o onboarding (wizard do briefing-trilha ou preenchimento
manual) e o núcleo: nenhum módulo liga com um perfil que não passe por aqui.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

Evento = Literal["lead", "lead_qualificado", "agendamento", "venda", "desqualificado", "reativado"]
ModeloReceita = Literal["venda_direta", "comissao", "recorrencia"]
DiaUtil = Literal["segunda", "terca", "quarta", "quinta", "sexta"]
Fracao = Annotated[float, Field(gt=0, le=1)]
Positivo = Annotated[float, Field(gt=0)]

# Etapas de sistema do Kommo, iguais em todas as contas.
KOMMO_STATUS_GANHO = 142
KOMMO_STATUS_PERDIDO = 143

class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


# Mesmo formato do nome da pasta do cliente em trilha-clientes (e do cliente_id da API).
ClienteId = Annotated[str, Field(pattern=r"^[a-z0-9_][a-z0-9_-]{0,63}$")]

# Blocos de versões anteriores: ignorados, com aviso no `validar`.
BLOCOS_LEGADOS = {"autonomia": "substituído pelo bloco freio (ADR-006); pode ser apagado"}


class Cliente(_Base):
    id: ClienteId
    nome: str
    segmento: str  # aponta para playbooks/<segmento>/


class Economia(_Base):
    """Entradas da calculadora de economia unitária (núcleo §3.1)."""

    modelo_receita: ModeloReceita
    # venda_direta
    ticket_medio: Positivo | None = None
    # comissao
    valor_medio_bem: Positivo | None = None
    comissao_pct: Fracao | None = None
    participacao_comissao: Fracao = 1.0
    # recorrencia
    mensalidade: Positivo | None = None
    meses_retencao: Positivo | None = None

    margem_contribuicao: Fracao
    pct_investivel: Fracao
    taxa_fechamento: Fracao
    taxa_qualificacao: Fracao
    taxa_agendamento: Fracao | None = None
    estimados: list[str] = Field(default_factory=list)  # campos que vieram do playbook

    @model_validator(mode="after")
    def _coerencia(self) -> Economia:
        exigidos = {
            "venda_direta": ("ticket_medio",),
            "comissao": ("valor_medio_bem", "comissao_pct"),
            "recorrencia": ("mensalidade", "meses_retencao"),
        }[self.modelo_receita]
        faltando = [c for c in exigidos if getattr(self, c) is None]
        if faltando:
            raise ValueError(f"modelo_receita={self.modelo_receita} exige: {', '.join(faltando)}")
        if self.taxa_qualificacao < self.taxa_fechamento:
            raise ValueError("taxa_qualificacao não pode ser menor que taxa_fechamento")
        if self.taxa_agendamento is not None and not (
            self.taxa_fechamento <= self.taxa_agendamento <= self.taxa_qualificacao
        ):
            raise ValueError("esperado taxa_fechamento ≤ taxa_agendamento ≤ taxa_qualificacao")
        desconhecidos = set(self.estimados) - set(type(self).model_fields)
        if desconhecidos:
            raise ValueError(f"estimados cita campos inexistentes: {sorted(desconhecidos)}")
        return self


class Verba(_Base):
    mensal_planejada: Positivo
    teto_mensal: Positivo | None = None
    moeda: str = "BRL"


class Meta(_Base):
    ad_account_id: str | None = None
    pixel_id: str | None = None  # conjunto de dados da API de Conversões
    page_id: str | None = None  # necessário para eventos de WhatsApp (business_messaging)


class Google(_Base):
    customer_id: str | None = None
    login_customer_id: str | None = None  # MCC


class Plataformas(_Base):
    meta: Meta | None = None
    google: Google | None = None


class MapaEvento(_Base):
    pipeline_id: int | None = None  # None = qualquer funil
    status_id: int
    evento: Evento


class Crm(_Base):
    tipo: Literal["kommo"] = "kommo"
    subdominio: str
    mapa_eventos: list[MapaEvento] = Field(default_factory=list)
    campos: dict[str, str] = Field(default_factory=dict)

    def mapa_completo(self) -> list[MapaEvento]:
        """Mapa do cliente + padrões das etapas de sistema do Kommo (o do cliente tem prioridade)."""
        mapa = list(self.mapa_eventos)
        configurados = {m.status_id for m in mapa}
        for status, evento in ((KOMMO_STATUS_GANHO, "venda"), (KOMMO_STATUS_PERDIDO, "desqualificado")):
            if status not in configurados:
                mapa.append(MapaEvento(status_id=status, evento=evento))
        return mapa

    def evento_para(self, status_id: int, pipeline_id: int | None) -> Evento | None:
        for m in self.mapa_completo():
            if m.status_id == status_id and (m.pipeline_id is None or m.pipeline_id == pipeline_id):
                return m.evento
        return None


class Destino(_Base):
    meta_event_name: str | None = None
    google_conversion_action_id: str | None = None
    # nenhum: sem valor · receita: receita real da venda (comissão, quando for o caso)
    # ponderado: custo máximo do evento pela calculadora (núcleo §7.2, alternativa 3)
    valor: Literal["nenhum", "receita", "ponderado"] = "nenhum"


class Conversao(_Base):
    eventos_semana_aprendizado: Annotated[int, Field(gt=0)] = 50
    destinos: dict[Evento, Destino] = Field(default_factory=dict)


class Freio(_Base):
    """Freio de emergência (ADR-006): a única ação automática do sistema.

    modo "pausar" (opção A, padrão): pausa e avisa na hora; desfazer é um clique.
    modo "avisar" (opção B): só avisa; a pausa fica com o responsável.
    """

    modo: Literal["pausar", "avisar"] = "pausar"
    gasto_sem_lead_multiplo: Positivo = 3.0  # × CPL máximo, desde o último lead
    horas_rastreamento_quebrado: Positivo = 6.0  # gastando sem nenhum evento de conversão registrado


class Operacao(_Base):
    """Agenda do assessor com o cliente — o sistema deixa pronto, na véspera, o material de cada compromisso.

    Contato com o cliente (contatos proativos, respostas no grupo) é do assessor e não entra aqui.
    """

    responsavel: str
    dia_otimizacao: DiaUtil
    dia_relatorio: DiaUtil
    semana_reuniao: Annotated[int, Field(ge=1, le=4)]  # semana do mês da reunião mensal
    dia_reuniao: DiaUtil = "sexta"
    faixa: Literal["essencial", "performance", "escala"] = "essencial"


class Perfil(_Base):
    @model_validator(mode="before")
    @classmethod
    def _ignorar_legado(cls, dados):
        if isinstance(dados, dict) and any(b in dados for b in BLOCOS_LEGADOS):
            dados = {k: v for k, v in dados.items() if k not in BLOCOS_LEGADOS}
        return dados

    versao: Annotated[int, Field(ge=1)]
    vigente_desde: date
    cliente: Cliente
    metrica_principal: Evento
    economia: Economia
    verba: Verba
    plataformas: Plataformas = Field(default_factory=Plataformas)
    crm: Crm | None = None
    conversao: Conversao = Field(default_factory=Conversao)
    freio: Freio = Field(default_factory=Freio)
    operacao: Operacao | None = None


def avisos_legado(caminho: str | Path) -> list[str]:
    with open(caminho, encoding="utf-8") as f:
        bruto = yaml.safe_load(f) or {}
    return [f"bloco '{b}' ignorado: {motivo}" for b, motivo in BLOCOS_LEGADOS.items() if b in bruto]


def carregar_perfil(caminho: str | Path) -> Perfil:
    with open(caminho, encoding="utf-8") as f:
        return Perfil.model_validate(yaml.safe_load(f))
