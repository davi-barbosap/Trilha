# Ferramentas

## Usadas por este sistema

| Ferramenta | Papel no Trilha |
|---|---|
| **n8n 2.x** (autohospedado) | orquestrador dos fluxos — [n8n](n8n.md), ADR-002 |
| **Kommo** | CRM único suportado: etapas, campos de rastreamento, leads — [Kommo](kommo.md) |
| **Meta — API de Conversões (Graph API v26.0)** | retorno de eventos de qualidade de lead |
| **Google — Data Manager API** | retorno de conversões offline (substituiu o envio pela Google Ads API para novos integradores em 15/06/2026) |
| **Google Ads API** | coleta de métricas e execução de mudanças aprovadas |
| **ClickUp** | mesa de trabalho do assessor — [ClickUp](clickup.md) |
| **Slack** | urgências, freio, falhas e leitura diária para a equipe — nunca para o cliente |
| **BigQuery + Looker Studio** | histórico de mídia e painel MTD (ADR-001, ADR-003) |
| **Biblioteca de Anúncios do Meta** e **Central de Transparência do Google** | dados de concorrentes para o pacote de briefing |

## Paralelas (fora deste sistema — [ecossistema](../ecossistema.md))

| Ferramenta | O que o Trilha precisa dela |
|---|---|
| **BotConversa** | repassar `ctwa_clid` e UTMs ao lead no Kommo; mover o lead nas etapas padronizadas |
| **GA4 / GTM** | tag do Google e pixel funcionando; eventos de conversão do site; `event_id` compartilhado com o servidor |
| **Landing pages** | campos ocultos com `gclid`/`gbraid`/`wbraid`/`fbclid`/UTMs gravados no Kommo |
| **Disparos em massa e fluxos de CRM** | não alterar as etapas do funil sem atualizar o `crm.mapa_eventos` |
| **Captura de tarefas no ClickUp (n8n)** | tarefas com o cliente identificado, para o painel da carteira |
| **Canva / Google Drive** | uso da equipe de criação; o Trilha só referencia os links das peças |
