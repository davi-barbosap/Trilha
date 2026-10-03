# ADR-006 — Freio de emergência como única ação automática

**Status:** aceita

## Contexto
Toda otimização é do assessor, feita em pelo menos uma sessão semanal por cliente ([modelo operacional](../modelo-operacional.md)). Entre uma sessão e outra — à noite, no fim de semana — uma campanha pode gastar sem retorno possível.

## Decisão
- Toda alteração em conta é decidida pelo assessor a partir do dossiê semanal.
- Única exceção: **freio de emergência**, com dois gatilhos:
  1. gasto desde o último lead ≥ N × CPL máximo (padrão 3);
  2. campanha gastando há ≥ H horas sem nenhum evento de conversão (padrão 6) — rastreamento provavelmente quebrado.
- Modo por cliente no `perfil.yaml` (`freio.modo`): **`pausar`** (padrão) — pausa e avisa na hora, com desfazer; ou `avisar` — só avisa.
- A regra vive na trilha-api (`trilha/core/freio.py`, rota `/freio/avaliar`); o n8n busca as métricas, executa a pausa e avisa.

## Consequências
- Reativar uma campanha pausada pelo freio é sempre decisão do assessor.
- Toda ação do freio entra no histórico de alterações e no dossiê da semana seguinte.
- O token do Meta precisa de permissão de escrita nos clientes em modo `pausar`.
