# ADR-009 — Escopo do sistema: execução manual dos serviços de mídia; o resto é paralelo

**Status:** aceita · 2026-10-03

## Contexto
Comparada com a descrição do cargo de Assessor de Marketing, a v0.5 misturava três coisas: o trabalho manual dos serviços de mídia paga (que é o objetivo), tarefas humanas do assessor (contatos proativos, tempo de resposta no grupo) e ferramentas de outra natureza (landing pages, disparos em massa, fluxos de CRM, captura de tarefas).

## Decisão
- O Trilha tem um objetivo só: **executar o trabalho manual que sustenta os serviços de mídia paga** — conversão real, coleta e monitoramento, dossiê da otimização semanal e execução do aprovado, números do relatório semanal, pacote de dados do briefing, pacote da reunião mensal e painel da carteira.
- **Do assessor, sem participação do sistema:** contatos proativos (≥ 3 por cliente por semana) e respostas no grupo do cliente (≤ 2 h). O sistema não prepara pauta, não escreve rascunho de mensagem e não mede esses indicadores. (Substitui a "pauta de contato" da v0.5.)
- **Paralelas, só mencionadas na estrutura global** ([ECOSSISTEMA.md](../../ECOSSISTEMA.md)): BotConversa, GA4/GTM, landing pages, disparos em massa, fluxos de CRM, captura de tarefas no ClickUp no mesmo dia, onboarding. O Trilha define apenas o que precisa receber delas (contratos de interface).
- O CRM suportado é o **Kommo**.
- O briefing de criativo sobe de prioridade: o pacote de dados do briefing entra no MVP.

## Consequências
- Saem do Trilha: o módulo de landing pages do Google (M5), a geração de imagens e roteiros, o verificador de copy para landing pages e mensagens de WhatsApp, a geração de fluxos de atendimento, a pauta de contato (W07) e o alerta de SLA em tempo real (W08). A ata→tarefas da reunião mensal passa para a automação paralela de captura de tarefas.
- O perfil do cliente troca `dia_contato`/`canal_contato` por `dia_relatorio`.
