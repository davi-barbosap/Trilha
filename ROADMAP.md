# Roadmap único — Trilha · v0.6

> Escopo: [`ECOSSISTEMA.md`](ECOSSISTEMA.md). Cada entrega existe para deixar pronto o material de um compromisso do assessor ([`MODELO-OPERACIONAL.md`](MODELO-OPERACIONAL.md)) ou para alimentar esse material.
> Regra: **nenhuma fase começa antes da anterior estar rodando em pelo menos um cliente real.**
> Legenda: ✅ feito · 🟡 em andamento · ⬜ a fazer · ⏸ aguardando decisão

## Pronto (base de código)

Esquema validado do `perfil.yaml` (com `freio` e `operacao`) · calculadora de economia unitária · leitura do Kommo com confirmação da etapa real do lead · payloads da API de Conversões do Meta (v26.0) e da Data Manager API do Google · regras do freio · trilha-api (`/saude`, `/clientes`, `/validar`, `/calcular`, `/conversao`, `/freio/avaliar`) com segredo de webhook por cliente · fluxos-modelo W01 e W10 · infraestrutura em `infra/` · 42 testes · verificação automática no GitHub.

## Fase 1 — MVP em 8 semanas (1 cliente piloto → carteira)

**Pré-requisito ⏸:** servidor autohospedado para o n8n (decisão do assessor, "para depois"). Até lá, nada desta fase roda em produção.

| Semana | Entrega | Compromisso que passa a ter material pronto | Critério de pronto | Status |
|---|---|---|---|---|
| 1 | Servidor (n8n 2.x em modo fila, Postgres, Redis, Caddy, trilha-api), backup testado, **W10** vigia de falhas | — (base) | `/saude` respondendo pela rede interna; falha forçada chegando no Slack; um backup restaurado | 🟡 compose, Dockerfile, backup e W10 escritos; falta o servidor |
| 2 | **W01** conversão real no piloto (Meta) | todos | `lead_qualificado` no Gerenciador de Eventos, primeiro com `META_TEST_EVENT_CODE`, depois em produção | 🟡 trilha-api pronta; falta importar e ligar no Kommo do piloto |
| 3 | Envio ao Google pela **Data Manager API** (OAuth) + **W02** coleta diária (Meta, Google, Kommo → BigQuery) | dossiê, relatório | `validateOnly` aceito, depois envio real; dados do dia anterior às 05:30 | 🟡 payload pronto; envio e coleta a fazer |
| 4 | **W03** urgências + freio (opção A no piloto) + **W04** pacing + **W05** leitura diária | monitoramento | uma pausa simulada com aviso e desfazer; leitura diária no Slack às 07:30 | 🟡 regra do freio pronta |
| 5 | **W12** dossiê de otimização + histórico de alterações; medição de horas | **otimização semanal** | o assessor faz a sessão do piloto só com o dossiê | ⬜ |
| 6 | **W06** execução do aprovado no ClickUp + **W07** números do relatório semanal | otimização semanal, **relatório semanal** | mudança aprovada executada e desfeita em teste; relatório do piloto com os três blocos na véspera | ⬜ |
| 7 | **W08** pacote de dados do briefing; **entrada dos outros 7 clientes** (só configuração) | **briefing de criativo** | 8 perfis válidos em `/clientes`; briefing do piloto escrito sobre o pacote | ⬜ |
| 8 | **W11** pacote da reunião + **W14** painel da carteira; calibração dos limites; runbook revisado | **reunião mensal**, **alinhamento com a equipe** | uma reunião preparada em ≤ 15 min; painel na véspera da reunião de equipe | ⬜ |

**Fora do MVP, de propósito:** subida de campanhas pelo sistema, estatística avançada, verificador de copy, sugestão de alocação de verba, outros segmentos.

## Fase 2 — Profundidade (após 3 meses de operação)

| Entrega | Melhora |
|---|---|
| Taxonomia de ângulos + renomeação dos anúncios existentes | dossiê, relatório e briefing passam a dizer "qual argumento converte", não só "qual anúncio" |
| **Subida de campanhas e anúncios aprovados** (montagem pela taxonomia, publicação após aprovação) | execução que hoje é manual |
| Auditoria de onboarding automatizada (Meta, Google, desperdício em termos de pesquisa) | entrada de cliente |
| Varredura de termos de pesquisa (Google) como pontos de atenção no dossiê | otimização semanal |
| Painel MTD no Looker Studio | reunião mensal |
| Calendário sazonal | dossiê e pacote da reunião antecipam datas |

## Fase 3 — Inteligência

Verificador de copy dos anúncios (Meta e RSA) · métricas de criativo e protocolo de testes · estatística modo médio/alto (≥ 1 cliente com 20+ conversões/dia) · vencedores por argumento · base de referência da carteira (≥ 5 clientes do mesmo segmento).

## Fase 4 — Escala

Visão consolidada entre canais · novos playbooks (educação, serviço local, saúde) · TikTok e LinkedIn · testes de AI Max, Demand Gen, YouTube e PMax como hipóteses por cliente.

## Em paralelo (fora deste repositório — [ECOSSISTEMA.md](ECOSSISTEMA.md))

BotConversa · GA4/GTM · landing pages · disparos em massa · fluxos de CRM no Kommo · captura de tarefas no ClickUp no mesmo dia (n8n) · onboarding (briefing-trilha). O Trilha só define o que precisa receber delas.

## Indicadores do sistema

Ver [`MODELO-OPERACIONAL.md`](MODELO-OPERACIONAL.md) §8.
