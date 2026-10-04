"""Raio-x do funil: o que acontece entre o lead que entrou e a venda que saiu.

Calcula, etapa por etapa, quantos leads passaram, quanto tempo levaram, onde e por que
foram perdidos, e qual vazamento custa mais vendas. Separa o que o marketing entregou
do que o comercial converteu. Atribui vendas a campanhas pelo próprio Kommo, sem
depender da janela de atribuição das plataformas.

O sistema mostra onde está o maior vazamento e quanto ele custa; a leitura é do assessor.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from statistics import median

from pydantic import BaseModel, ConfigDict, Field

from trilha.core.perfil import ETAPAS_FUNIL, Etapa
from trilha.core.playbook import Playbook

# De quem é cada passagem: chegar à etapa X depende de...
LADO_DA_ETAPA = {
    "em_atendimento": "atendimento",
    "lead_qualificado": "qualificacao",
    "agendamento": "comercial",
    "comparecimento": "comercial",
    "proposta": "comercial",
    "venda": "comercial",
}
ETAPAS_DO_MARKETING = ("lead", "lead_qualificado", "agendamento")
AMOSTRA_MINIMA = 20


class LeadFunil(BaseModel):
    """Histórico de um lead no Kommo, normalizado."""

    model_config = ConfigDict(extra="forbid")

    lead_id: int
    etapas: dict[Etapa, datetime] = Field(default_factory=dict)  # quando entrou em cada etapa
    perdido_em: datetime | None = None
    motivo_perda: str | None = None
    tentativas_contato: int | None = None
    responsavel: str | None = None
    campanha: str | None = None  # utm_campaign gravada no lead
    criativo: str | None = None  # utm_content gravada no lead
    valor: float | None = None  # valor do negócio (VGV no imobiliário)

    def indice(self) -> int:
        """Etapa mais avançada alcançada (etapas puladas contam como passadas)."""
        return max((ETAPAS_FUNIL.index(e) for e in self.etapas), default=0)

    def alcancou(self, etapa: str) -> bool:
        return self.indice() >= ETAPAS_FUNIL.index(etapa)

    def vendido(self) -> bool:
        return "venda" in self.etapas


def classificar_perda(lead: LeadFunil, playbook: Playbook) -> tuple[str, str]:
    """(categoria, momento) de uma perda. Categoria vem do motivo; momento, da etapa."""
    if lead.motivo_perda is None:
        categoria = "sem_motivo"
    else:
        categoria = playbook.motivos_perda.get(lead.motivo_perda, "nao_classificado")
    momento = "depois_da_qualificacao" if lead.alcancou("lead_qualificado") else "antes_da_qualificacao"
    return categoria, momento


def _horas(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 3600


def _mediana(valores: list[float]) -> float | None:
    return round(median(valores), 1) if valores else None


def _taxa(parte: int, todo: int) -> float | None:
    return round(parte / todo, 4) if todo else None


def _resumo(leads: list[LeadFunil]) -> dict:
    vendidos = [l for l in leads if l.vendido()]
    return {
        "leads": len(leads),
        "qualificados": sum(l.alcancou("lead_qualificado") for l in leads),
        "comparecimentos": sum(l.alcancou("comparecimento") for l in leads),
        "vendas": len(vendidos),
        "valor_vendido": sum(l.valor or 0 for l in vendidos),
    }


def raio_x(
    leads: list[LeadFunil],
    playbook: Playbook,
    investimento: float | None = None,
    sla_primeiro_contato_min: float = 30,
    referencia: dict[str, float] | None = None,
    valor_medio_venda: float | None = None,
) -> dict:
    """Raio-x de um período. `referencia` (conversão por etapa) padrão: a do playbook."""
    referencia = referencia if referencia is not None else dict(playbook.taxas_referencia)
    n = len(leads)

    # 1. Etapa por etapa
    alcancaram = {e: [l for l in leads if l.alcancou(e)] for e in ETAPAS_FUNIL}
    etapas = []
    for i, etapa in enumerate(ETAPAS_FUNIL):
        anterior = ETAPAS_FUNIL[i - 1] if i else None
        tempos = [
            _horas(l.etapas[anterior], l.etapas[etapa])
            for l in alcancaram[etapa]
            if anterior and anterior in l.etapas and etapa in l.etapas
        ]
        etapas.append({
            "etapa": etapa,
            "rotulo": playbook.rotulo(etapa),
            "lado": LADO_DA_ETAPA.get(etapa, "marketing"),
            "entraram": len(alcancaram[etapa]),
            "conversao_da_anterior": _taxa(len(alcancaram[etapa]), len(alcancaram[anterior])) if anterior else None,
            "referencia": referencia.get(etapa),
            "mediana_horas_desde_anterior": _mediana(tempos),
        })

    # 2. Primeiro contato e cadência do time comercial do cliente
    minutos = [
        _horas(l.etapas["lead"], l.etapas["em_atendimento"]) * 60
        for l in leads if "lead" in l.etapas and "em_atendimento" in l.etapas
    ]
    perdidos_antes = [l for l in leads if l.perdido_em and not l.alcancou("lead_qualificado")]
    primeiro_contato = {
        "sla_minutos": sla_primeiro_contato_min,
        "mediana_minutos": _mediana(minutos),
        "dentro_do_sla": _taxa(sum(m <= sla_primeiro_contato_min for m in minutos), len(minutos)),
        "sem_primeiro_contato": sum(not l.alcancou("em_atendimento") for l in leads),
    }
    cadencia = {
        "mediana_tentativas_perdidos_antes_de_qualificar": _mediana(
            [l.tentativas_contato for l in perdidos_antes if l.tentativas_contato is not None]
        ),
        "mediana_tentativas_qualificados": _mediana(
            [l.tentativas_contato for l in alcancaram["lead_qualificado"] if l.tentativas_contato is not None]
        ),
    }

    # 3. Perdas: por etapa, por categoria, e critério de qualificação
    perdas_etapa: dict[str, Counter] = defaultdict(Counter)
    perdas_categoria: Counter = Counter()
    criterio_a_revisar = 0
    for l in leads:
        if not l.perdido_em or l.vendido():
            continue
        categoria, momento = classificar_perda(l, playbook)
        perdas_etapa[ETAPAS_FUNIL[l.indice()]][categoria] += 1
        perdas_categoria[categoria] += 1
        if categoria == "lead" and momento == "depois_da_qualificacao":
            criterio_a_revisar += 1
    perdas = {
        "por_etapa": {e: dict(c) for e, c in perdas_etapa.items()},
        "por_categoria": dict(perdas_categoria),
        "qualificados_perdidos_por_motivo_de_lead": criterio_a_revisar,
    }

    # 4. Maior vazamento: vendas que faltaram em cada passagem abaixo da referência
    convs = {x["etapa"]: x["conversao_da_anterior"] for x in etapas}
    vendidos = [l for l in leads if l.vendido()]
    ticket = (sum(l.valor or 0 for l in vendidos) / len(vendidos)) if vendidos and any(l.valor for l in vendidos) else valor_medio_venda
    vazamentos = []
    for i, etapa in enumerate(ETAPAS_FUNIL[1:], start=1):
        entraram_antes = len(alcancaram[ETAPAS_FUNIL[i - 1]])
        obs, ref = convs[etapa], referencia.get(etapa)
        if ref is None or obs is None or entraram_antes < AMOSTRA_MINIMA or obs >= ref:
            continue
        restante = 1.0
        for seguinte in ETAPAS_FUNIL[i + 1:]:
            taxa = convs[seguinte] if convs[seguinte] else referencia.get(seguinte)
            restante *= taxa or 0
        vendas_a_mais = entraram_antes * (ref - obs) * restante
        vazamentos.append({
            "etapa": etapa,
            "rotulo": playbook.rotulo(etapa),
            "lado": LADO_DA_ETAPA[etapa],
            "observado": obs,
            "referencia": ref,
            "base": entraram_antes,
            "vendas_a_mais": round(vendas_a_mais, 2),
            "valor_a_mais": round(vendas_a_mais * ticket, 2) if ticket else None,
        })
    vazamentos.sort(key=lambda v: v["vendas_a_mais"], reverse=True)

    # 5. Marketing entregou × comercial converteu
    mkt = {e: len(alcancaram[e]) for e in ETAPAS_DO_MARKETING}
    marketing = {
        "leads": mkt["lead"],
        "qualificados": mkt["lead_qualificado"],
        "agendamentos": mkt["agendamento"],
        "taxa_qualificacao": _taxa(mkt["lead_qualificado"], mkt["lead"]),
        "custo_por_qualificado": round(investimento / mkt["lead_qualificado"], 2) if investimento and mkt["lead_qualificado"] else None,
        "custo_por_agendamento": round(investimento / mkt["agendamento"], 2) if investimento and mkt["agendamento"] else None,
    }
    comercial = {
        "primeiro_contato_dentro_do_sla": primeiro_contato["dentro_do_sla"],
        "comparecimento": convs["comparecimento"],
        "propostas": len(alcancaram["proposta"]),
        "vendas": len(vendidos),
        "qualificado_para_venda": _taxa(len(vendidos), mkt["lead_qualificado"]),
        "perdas_atendimento": perdas_categoria.get("atendimento", 0),
        "perdas_comercial": perdas_categoria.get("comercial", 0),
    }

    # 6. Resultado: venda e valor vendido; CPL é diagnóstico
    valor_vendido = sum(l.valor or 0 for l in vendidos)
    resultado = {
        "investimento": investimento,
        "vendas": len(vendidos),
        "valor_vendido": valor_vendido,
        "retorno_sobre_investimento": round(valor_vendido / investimento, 1) if investimento else None,
        "custo_por_comparecimento": round(investimento / len(alcancaram["comparecimento"]), 2) if investimento and alcancaram["comparecimento"] else None,
        "custo_por_venda": round(investimento / len(vendidos), 2) if investimento and vendidos else None,
        "diagnostico_cpl": round(investimento / n, 2) if investimento and n else None,
    }

    # 7. Por responsável (time comercial do cliente) e por campanha (atribuição pelo Kommo)
    por_responsavel = {}
    grupos = defaultdict(list)
    for l in leads:
        grupos[l.responsavel or "sem responsável"].append(l)
    for nome, ls in sorted(grupos.items()):
        mins = [
            _horas(l.etapas["lead"], l.etapas["em_atendimento"]) * 60
            for l in ls if "lead" in l.etapas and "em_atendimento" in l.etapas
        ]
        por_responsavel[nome] = {
            **_resumo(ls),
            "mediana_minutos_primeiro_contato": _mediana(mins),
            "dentro_do_sla": _taxa(sum(m <= sla_primeiro_contato_min for m in mins), len(mins)),
        }
    por_campanha = {}
    grupos = defaultdict(list)
    for l in leads:
        grupos[l.campanha or "sem campanha"].append(l)
    for nome, ls in sorted(grupos.items()):
        por_campanha[nome] = _resumo(ls)

    return {
        "leads": n,
        "etapas": etapas,
        "primeiro_contato": primeiro_contato,
        "cadencia": cadencia,
        "perdas": perdas,
        "maior_vazamento": vazamentos[0] if vazamentos else None,
        "vazamentos": vazamentos,
        "marketing_entregou": marketing,
        "comercial_converteu": comercial,
        "resultado": resultado,
        "por_responsavel": por_responsavel,
        "por_campanha": por_campanha,
    }
