# ADR-001 — Armazenamento

**Status:** aceita · 2026-10-03

## Contexto
O núcleo cita "normalização", "histórico de alterações", "registro de decisões" e "painel", mas a v0.3 não dizia onde os dados vivem. Há dois perfis de dado: (a) eventos transacionais pequenos e críticos (eventos do CRM, alterações, decisões, fila de envios) e (b) histórico de mídia volumoso e analítico (métricas diárias por anúncio).

## Decisão
- **Postgres gerenciado** (Cloud SQL ou Supabase) para `fato_eventos_crm`, `historico_alteracoes`, `decisoes`, `fila_envios` (com estado e tentativas).
- **BigQuery** para `fato_midia`. O Google Ads tem transferência nativa e gratuita para o BigQuery; o Meta entra por script diário de exportação.
- Esquema comum descrito no núcleo §2.1. Um `cliente_id` em todas as tabelas; acesso por cliente controlado por visão.

## Consequências
- Custo baixo no início (BigQuery cobra por consulta; volumes de PME são pequenos).
- Planilhas deixam de ser fonte de dado — podem ser saída, nunca entrada do motor.
- Até a semana 4 do MVP, o pipeline de conversão grava em arquivo JSONL local (`TRILHA_LOG_DIR`) para não bloquear o retorno de eventos pela escolha do provedor.
