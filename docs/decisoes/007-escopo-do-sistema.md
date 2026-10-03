# ADR-007 — Escopo: execução manual dos serviços de mídia; o resto é paralelo

**Status:** aceita

## Contexto
O cargo de Assessor de Marketing reúne três naturezas de trabalho: o trabalho manual dos serviços de mídia paga, o relacionamento com o cliente e ferramentas de outra natureza (landing pages, disparos em massa, fluxos de CRM, captura de tarefas). Misturar as três num só sistema dilui o objetivo.

## Decisão
- O Trilha tem um objetivo só: **executar o trabalho manual que sustenta os serviços de mídia paga** — conversão real, coleta e monitoramento, dossiê da otimização semanal e execução do aprovado, números do relatório semanal, pacote de dados do briefing, pacote da reunião mensal e painel da carteira.
- **Do assessor, sem participação do sistema:** contatos proativos e respostas no grupo do cliente. O sistema não prepara pauta, não escreve mensagem e não mede esses indicadores.
- **Ferramentas paralelas** ([ecossistema](../ecossistema.md)): BotConversa, GA4/GTM, landing pages, disparos em massa, fluxos de CRM, captura de tarefas no ClickUp, onboarding. O Trilha define apenas o que precisa receber delas.
- O CRM suportado é o **Kommo**.

## Consequências
- Fora do Trilha: construção de landing pages, geração de imagens e roteiros, fluxos de atendimento, mensagens ao cliente, transformação de atas em tarefas.
- O perfil do cliente traz só a agenda do material que o sistema prepara (`operacao.dia_otimizacao`, `dia_relatorio`, `semana_reuniao`, `dia_reuniao`).
