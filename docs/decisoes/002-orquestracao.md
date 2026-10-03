# ADR-002 — Orquestração

**Status:** substituída por [ADR-007](007-n8n-orquestrador.md) · 2026-10-03

## Contexto
Precisamos receber webhooks (Kommo, ClickUp), rodar rotinas agendadas (relatório diário, alertas, pacing) e garantir que falha não seja silenciosa (núcleo §10).

## Decisão
- **Cloud Run** (contêiner com o pacote `trilha`) para os endpoints de webhook e para os jobs, acionados pelo Cloud Scheduler.
- Webhook responde rápido (grava na `fila_envios`) e processa de forma assíncrona, com novas tentativas e backoff exponencial.
- Ferramentas no-code (n8n, Make) são permitidas para automações periféricas, **nunca** no caminho do dinheiro (retorno de conversão, alterações em conta).
- Toda rotina agendada registra execução; ausência de execução no horário dispara alerta.

## Consequências
- Um único artefato implantável, testável localmente (`python -m trilha simular-webhook`).
- Custo próximo de zero em volume de PME.
