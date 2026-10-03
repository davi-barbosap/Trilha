"""CLI do Trilha: validar · calcular · simular-webhook · servir."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from pydantic import ValidationError

from trilha.core.economia import calcular
from trilha.core.perfil import carregar_perfil


def _brl(v: float | None) -> str:
    if v is None:
        return "—"
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def cmd_validar(args) -> int:
    perfil = carregar_perfil(args.perfil)
    print(f"OK — perfil de '{perfil.cliente.nome}' (versão {perfil.versao}, vigente desde {perfil.vigente_desde})")
    if perfil.economia.estimados:
        print("Atenção: usando padrões do playbook (estimados) para: " + ", ".join(perfil.economia.estimados))
    if perfil.operacao is None:
        print("Atenção: sem bloco operacao — os dossiês, pautas e pacotes de reunião não serão agendados")
    print(f"Freio de emergência: {perfil.freio.modo} (gasto sem lead ≥ {perfil.freio.gasto_sem_lead_multiplo:g}× CPL máximo"
          f" ou {perfil.freio.horas_rastreamento_quebrado:g}h sem evento de conversão)")
    if perfil.crm and not perfil.crm.mapa_eventos:
        print("Atenção: crm.mapa_eventos vazio — só as etapas de sistema (142 venda, 143 perdida) serão mapeadas")
    return 0


def cmd_calcular(args) -> int:
    perfil = carregar_perfil(args.perfil)
    verba = args.verba or perfil.verba.mensal_planejada
    r = calcular(perfil.economia, verba, perfil.conversao.eventos_semana_aprendizado)
    print(f"Cliente: {perfil.cliente.nome} · modelo de receita: {perfil.economia.modelo_receita}")
    print(f"Receita bruta por venda ....... {_brl(r.receita_bruta)}")
    print(f"CAC máximo .................... {_brl(r.cac_max)}")
    print(f"CPL máximo .................... {_brl(r.cpl_max)}")
    print(f"CPL qualificado máximo ........ {_brl(r.cpl_qualificado_max)}")
    print(f"Custo máximo por agendamento .. {_brl(r.custo_agendamento_max)}")
    print(f"\nVerba mensal para sair do aprendizado ({perfil.conversao.eventos_semana_aprendizado} eventos/semana, 1 conjunto):")
    for degrau, v in r.verba_por_degrau.items():
        marca = "✓" if degrau in r.degraus_viaveis else "✗"
        print(f"  {marca} {degrau:<17} {_brl(v)}")
    print(f"\nVerba planejada: {_brl(verba)} · verba mínima viável: {_brl(r.verba_minima_viavel)}")
    if verba < r.verba_minima_viavel:
        print("→ Abaixo da mínima: concentrar em uma plataforma, uma oferta e uma campanha; leitura de resultado será lenta.")
    elif "lead_qualificado" not in r.degraus_viaveis:
        print("→ Otimizar por lead qualificado é inviável com esta verba: otimizar por lead com atrito qualificador e")
        print("  enviar os eventos de qualidade mesmo assim (núcleo §7.2).")
    if r.estimados:
        print("Estimados (padrão do playbook): " + ", ".join(r.estimados))
    return 0


def cmd_simular_webhook(args) -> int:
    from trilha.conversao.pipeline import executar, processar
    from trilha.integracoes.kommo import extrair_dados_lead

    perfil = carregar_perfil(args.perfil)
    with open(args.webhook, encoding="utf-8") as f:
        corpo = f.read().strip()
    with open(args.lead, encoding="utf-8") as f:
        lead = json.load(f)
    contatos = []
    for caminho in args.contato or []:
        with open(caminho, encoding="utf-8") as f:
            contatos.append(json.load(f))
    dados = extrair_dados_lead(lead, contatos, perfil.crm.campos)
    envios = executar(processar(corpo, perfil, lambda _id: dados), simular=True)
    print(json.dumps([asdict(e) for e in envios], ensure_ascii=False, indent=2))
    return 0


def cmd_servir(args) -> int:
    from trilha.api import servir

    servir(args.host, args.porta)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="trilha", description=__doc__)
    sub = p.add_subparsers(dest="comando", required=True)

    s = sub.add_parser("validar", help="valida um perfil.yaml")
    s.add_argument("perfil")
    s.set_defaults(func=cmd_validar)

    s = sub.add_parser("calcular", help="calculadora de economia unitária e verba por degrau")
    s.add_argument("perfil")
    s.add_argument("--verba", type=float, help="verba mensal (padrão: a do perfil)")
    s.set_defaults(func=cmd_calcular)

    s = sub.add_parser("simular-webhook", help="mostra o que um webhook do Kommo enviaria ao Meta e ao Google")
    s.add_argument("webhook", help="arquivo com o corpo form-urlencoded do webhook")
    s.add_argument("--perfil", required=True)
    s.add_argument("--lead", required=True, help="JSON do lead (API v4)")
    s.add_argument("--contato", action="append", help="JSON de contato (API v4); pode repetir")
    s.set_defaults(func=cmd_simular_webhook)

    s = sub.add_parser("servir", help="sobe a trilha-api (HTTP) usada pelos fluxos do n8n")
    s.add_argument("--host", default="0.0.0.0")
    s.add_argument("--porta", type=int, default=8080)
    s.set_defaults(func=cmd_servir)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except ValidationError as e:
        print(f"Perfil inválido:\n{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
