"""Saúde das contas de anúncio (portado de trilha-painel/build.py).

Contas pré-pagas param de entregar quando o saldo acaba, sem que a campanha tenha
qualquer problema. O sistema projeta quantos dias de saldo restam pela queima dos
últimos 7 dias e sugere a recarga para 30 dias. P1 = resolver hoje; P2 = esta semana.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# account_status da Graph API do Meta
STATUS_CONTA_META = {
    1: "ativa",
    2: "desativada",
    3: "não confirmada",
    7: "pendente de revisão",
    9: "encerrada",
    100: "pendente de encerramento",
    101: "encerrada por inatividade",
    201: "suspensa por fraude",
    202: "suspensa por regras",
}
DIAS_CRITICO = 5
DIAS_ATENCAO = 10


class ContaAnuncio(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str
    plataforma: str = "meta"
    status: int = 1
    saldo: float | None = Field(default=None, ge=0)  # None = conta pós-paga ou saldo ilegível
    gasto_7d: float = Field(default=0, ge=0)


def avaliar_conta(conta: ContaAnuncio, responsavel: str) -> dict:
    queima = conta.gasto_7d / 7 if conta.gasto_7d else None
    dias = int(conta.saldo / queima) if conta.saldo is not None and queima else None
    recarga = round(queima * 30, 2) if queima else None
    alertas = []

    def alerta(nivel, titulo, acao):
        alertas.append({"nivel": nivel, "titulo": f"{conta.nome}: {titulo}", "acao": acao, "responsavel": responsavel})

    if conta.status != 1:
        rotulo = STATUS_CONTA_META.get(conta.status, f"status {conta.status}")
        alerta("P1", f"conta {rotulo}", "Investigar no Business Manager (limite de gasto, revisão ou suspensão) hoje.")
    elif conta.saldo == 0:
        alerta("P1", "saldo zerado — entrega parada",
               f"Recarga urgente{f' (~R$ {recarga:,.0f} para 30 dias)' if recarga else ''}.".replace(",", "."))
    elif dias is not None and dias < DIAS_CRITICO:
        alerta("P1", f"saldo para {dias} dia(s)", f"Recarga esta semana: ~R$ {recarga:,.0f} para 30 dias.".replace(",", "."))
    elif dias is not None and dias < DIAS_ATENCAO:
        alerta("P2", f"saldo para ~{dias} dias", f"Avisar o cliente sobre a recarga: ~R$ {recarga:,.0f} para 30 dias.".replace(",", "."))
    return {
        "conta": conta.nome,
        "status": STATUS_CONTA_META.get(conta.status, str(conta.status)),
        "queima_diaria": round(queima, 2) if queima else None,
        "dias_de_saldo": dias,
        "recarga_30_dias": recarga,
        "alertas": alertas,
    }


def saude_do_cliente(contas: list[ContaAnuncio], responsavel: str) -> dict:
    avaliadas = [avaliar_conta(c, responsavel) for c in contas]
    alertas = [a for c in avaliadas for a in c["alertas"]]
    cor = "vermelho" if any(a["nivel"] == "P1" for a in alertas) else "amarelo" if alertas else "verde"
    return {"saude": cor, "contas": avaliadas, "alertas": alertas}
