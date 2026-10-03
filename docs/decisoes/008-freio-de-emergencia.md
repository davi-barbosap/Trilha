# ADR-008 — Freio de emergência no lugar dos níveis de autonomia

**Status:** aceita · 2026-10-03 · substitui o [ADR-006](006-niveis-de-autonomia.md)

## Contexto
O ADR-006 previa níveis L0–L3 e a liberação gradual de ações automáticas (L2). O modelo operacional definido depois ([MODELO-OPERACIONAL.md](../../MODELO-OPERACIONAL.md)) deixa explícito que **toda otimização é do assessor**, feita em pelo menos uma sessão semanal por cliente. Ações automáticas de otimização contradizem esse modelo e tiram do assessor a leitura da conta.

## Decisão
- Fim dos níveis L0–L3 e do L2. Toda alteração é **sugestão no dossiê semanal**, aprovada pelo assessor.
- Única exceção: **freio de emergência**, que protege a verba entre as sessões. Dois gatilhos:
  1. gasto desde o último lead ≥ N × CPL máximo (padrão 3);
  2. campanha gastando há ≥ H horas sem nenhum evento de conversão (padrão 6) — rastreamento provavelmente quebrado.
- Modo por cliente no `perfil.yaml` (`freio.modo`): **`pausar` (opção A, padrão)** — pausa e avisa na hora, com desfazer; ou `avisar` (opção B) — só avisa.
- A regra vive na trilha-api (`trilha/core/freio.py`, rota `/freio/avaliar`); o n8n busca as métricas, executa a pausa e avisa.

## Consequências
- O esquema do perfil rejeita o bloco `autonomia` antigo.
- Reativar uma campanha pausada pelo freio é sempre decisão do assessor (no dossiê ou pelo aviso).
- Toda ação do freio entra no histórico de alterações e no dossiê da semana seguinte.
