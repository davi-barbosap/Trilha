# Outras integrações recomendadas

| Ferramenta | Papel no Trilha | Fase |
|---|---|---|
| **n8n** (no próprio servidor) | orquestrador de todos os fluxos — ver [N8N.md](N8N.md) e ADR-007 | MVP semana 1 |
| **GA4** | comportamento no site, funil da landing, públicos; não é fonte da verdade de conversão (o CRM é) | MVP (auditoria) |
| **GTM server-side** | pixel + API de Conversões do Meta e tag do Google em domínio próprio; menos perda por bloqueadores | Fase 2 |
| **BigQuery + Looker Studio** | histórico de mídia e painel MTD (ADR-001, ADR-003); transferência nativa do Google Ads | MVP semana 4 / Fase 2 |
| **Slack** (ou grupo interno de WhatsApp) | urgências, freio, falhas e leitura diária para a equipe — nunca para o cliente | MVP semana 1 |
| **Canva** | brand kit (cores, fontes, logo do `marca.yaml`) e modelos preenchidos automaticamente com o texto aprovado pelo verificador de copy; substitui a "ferramenta externa de geração" do Meta §6.5 | Fase 3 |
| **Biblioteca de Anúncios do Meta** e **Central de Transparência do Google** | pesquisa de concorrentes: ângulos, ofertas e formatos em uso no mercado local; alimenta a taxonomia de ângulos | Fase 2 |
| **Microsoft Clarity** | mapas de calor e gravações das landing pages; diagnóstico de página que não converte (gratuito) | Fase 2 |
| **Google Drive** | repositório de assets do cliente referenciados em `ofertas/*.yaml` | Fase 2 |
| **Rastreamento de chamadas** | números por campanha para anúncios e extensões de ligação (Google M3) em serviços urgentes | Fase 4 |
