# ADR-003 — Painel

**Status:** aceita · 2026-10-03

## Decisão
**Looker Studio** sobre o BigQuery como painel MTD padrão — gratuito, compartilhável com o cliente, mesmo layout para todos. **Metabase** quando o cliente exigir login próprio ou filtros que o Looker Studio não suporte bem.

## Consequências
O painel não calcula regra de negócio: metas, CPL máximo e classificações vêm prontos das tabelas geradas pelo núcleo, para que painel, relatório e alertas mostrem o mesmo número.
