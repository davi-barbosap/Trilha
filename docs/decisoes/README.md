# Registro de decisões de arquitetura (ADRs)

Cada decisão estrutural vira um arquivo curto: contexto, decisão, consequências. Uma decisão só muda com um novo ADR que substitui o anterior.

| ADR | Decisão | Status |
|---|---|---|
| [001](001-armazenamento.md) | Postgres para eventos/alterações/decisões; BigQuery para histórico de mídia | aceita |
| [002](002-orquestracao.md) | Cloud Run (webhooks + agendador); no-code fora do caminho crítico | aceita |
| [003](003-painel.md) | Looker Studio sobre BigQuery; Metabase como alternativa | aceita |
| [004](004-dados-de-clientes.md) | Dados de clientes fora do repositório de código | aceita |
| [005](005-dependencia-briefing-trilha.md) | Consumo do briefing-trilha por versão fixada e contrato de dados | proposta — depende da responsável pelo repositório |
| [006](006-niveis-de-autonomia.md) | Níveis de autonomia L0–L3 por cliente e por tipo de ação | aceita |
