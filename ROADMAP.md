# Roadmap único — Trilha · v0.5

> Organizado em torno do [`MODELO-OPERACIONAL.md`](MODELO-OPERACIONAL.md): cada entrega existe para preparar um ritual do assessor (otimização semanal, contato proativo, reunião mensal, alinhamento com a equipe) ou para alimentar essa preparação.
> Regra: **nenhuma fase começa antes da anterior estar rodando em pelo menos um cliente real.**
> Legenda: ✅ feito · 🟡 em andamento · ⬜ a fazer

## Fase 1 — MVP em 8 semanas (1 cliente piloto → carteira inteira)

| Semana | Entrega | Ritual que passa a ser preparado | Critério de pronto | Status |
|---|---|---|---|---|
| 1 | Servidor: n8n em modo fila + worker, Postgres, Redis, Caddy (HTTPS), trilha-api, backup diário e exportação dos fluxos; ambiente de teste; **W10** vigia de falhas | — (base) | `/saude` respondendo pela rede interna; falha forçada chegando no Slack; backup restaurado uma vez | 🟡 compose, Dockerfile, backup.sh e W10 escritos; falta subir num servidor |
| 2 | **W01** conversão real no piloto | todos (é o dado que dá sentido aos demais) | `lead_qualificado` do piloto no Gerenciador de Eventos do Meta, com `META_TEST_EVENT_CODE` e depois em produção | 🟡 trilha-api `/conversao` pronta e testada; W01 exportado; falta importar e ligar no Kommo do piloto |
| 3 | **W02** coleta diária (Meta + Google → BigQuery) + envio das conversões offline ao Google pela biblioteca oficial | dossiê, pacote | dados do dia anterior às 05:30; upload ao Google sem erro parcial | 🟡 payload do Google pronto; coleta e envio a fazer |
| 4 | **W03** urgências + freio de emergência (opção A no piloto) + **W05** leitura diária | contato extra, leitura diária | uma pausa simulada do freio com aviso e desfazer; leitura diária no Slack às 07:30 | 🟡 regra do freio pronta e testada (`/freio/avaliar`) |
| 5 | **W12** dossiê de otimização + histórico de alterações + **W04** pacing | **sessão semanal de otimização** | assessor faz a sessão do piloto só com o dossiê, sem abrir o Gerenciador de Anúncios para levantar dados | ⬜ |
| 6 | **W06** execução do aprovado no ClickUp | sessão semanal de otimização | sugestão aprovada executada, registrada e desfeita com sucesso em teste | ⬜ |
| 7 | **W07** pauta de contato + **W14** painel da carteira; **entrada dos outros 7 clientes** (só configuração, nenhum fluxo novo) | **contato proativo**, **alinhamento com a equipe** | 8 perfis validados por `/clientes`; 8 pautas na véspera; painel na véspera da reunião de equipe | ⬜ |
| 8 | **W11** pacote da reunião + **W13** pós-reunião; calibração de limites; runbook revisado; medição de horas antes × depois | **reunião mensal** | uma reunião preparada em ≤ 15 min; ata virando tarefas; horas por cliente medidas | ⬜ |

**Pronto antes da Fase 1 (base de código):** esquema do `perfil.yaml` com `freio` e `operacao` · calculadora de economia unitária · parser do Kommo · payloads de Meta e Google · trilha-api com `/saude`, `/clientes`, `/validar`, `/calcular`, `/conversao`, `/freio/avaliar` · 36 testes · CI.

**Fora do MVP, de propósito:** motor bayesiano, alocação de verba, landing page nível 3, volante criativo completo, playbooks de outros segmentos, AI Max/PMax/Demand Gen, **W08** SLA (o ponto de atenção de atendimento entra no dossiê pela leitura diária do Kommo até lá) e **W09** onboarding automatizado (onboarding manual com `python -m trilha validar`).

## Fase 2 — Profundidade do que chega preparado (3+ meses de operação)

| Entrega | Melhora qual ritual |
|---|---|
| W08 SLA de atendimento em tempo real | contato proativo (ponto de atenção), gatilho de contato extra |
| Taxonomia de ângulos + renomeação dos anúncios existentes | dossiê: "qual argumento converte" em vez de "qual anúncio" |
| Auditorias de onboarding automatizadas (Meta, Google, desperdício em termos de pesquisa) + W09 | onboarding |
| Varredura de termos de pesquisa (Google M4) como sugestões de negativa no dossiê | sessão de otimização |
| Painel MTD no Looker Studio | reunião mensal, alinhamento |
| Calendário sazonal | dossiê e pacote da reunião antecipam datas |
| Extensão do wizard do briefing-trilha com as etapas de mídia | onboarding (ADR-005) |

## Fase 3 — Inteligência

| Entrega | Depende de |
|---|---|
| Verificador de copy (anúncio, RSA, landing, rascunhos da pauta) | taxonomia + `marca.yaml` |
| Métricas de criativo e framework de testes | taxonomia |
| Estatística modo médio/alto (MAD, correção de atraso, encolhimento bayesiano) | ≥ 1 cliente com 20+ conversões/dia |
| Detector de vencedores por anúncio e por etiqueta, no dossiê | estatística + taxonomia |
| Briefings de criativo sugeridos no dossiê, com esteira no ClickUp e peças no Canva | detector de vencedores |
| Base de referência da carteira (benchmarks anônimos) no pacote da reunião | ≥ 5 clientes no mesmo segmento |

## Fase 4 — Escala

Visão consolidada entre canais e sugestão de alocação de verba · novos playbooks (educação, serviço local, saúde) · TikTok e LinkedIn · Google M7 (negócio local) · landing nível 3 · AI Max, Demand Gen, YouTube e PMax como hipóteses por cliente.

## Indicadores (medidos desde a semana 5)

- Horas do assessor por cliente por semana — meta ≤ 1,5 h (MODELO-OPERACIONAL §4).
- % de semanas com os três rituais cumpridos por cliente — meta 100%.
- % de sugestões do dossiê aprovadas sem alteração — abaixo de 50% = calibrar.
- % de leads de mídia com identificador de clique gravado no Kommo — meta > 80%.
- CPL qualificado do piloto antes × depois do retorno de conversão real.
- Falhas silenciosas — meta zero.
