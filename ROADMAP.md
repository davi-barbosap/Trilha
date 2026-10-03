# Roadmap único — Trilha

> Substitui os roadmaps separados do núcleo, do Meta e do Google (v0.3).
> Regra: **nenhuma fase começa antes da anterior estar rodando em pelo menos um cliente real.**
> Legenda: ✅ feito · 🟡 em andamento · ⬜ a fazer

## Fase 1 — MVP (6 semanas)

Objetivo: um cliente imobiliário real com conversão real voltando às plataformas, relatório diário com CPL qualificado e aprovação de ações pelo ClickUp.

| Semana | Entrega | Critério de pronto | Status |
|---|---|---|---|
| 1 | Esquema validado do `perfil.yaml` + calculadora de economia unitária (CLI) + playbook imobiliário | `python -m trilha validar` e `python -m trilha calcular` rodando no cliente piloto; diagnóstico usado em uma prospecção | 🟡 código pronto, falta o cliente piloto |
| 2 | Webhook Kommo → mapa de eventos → API de Conversões do Meta | evento `lead_qualificado` do piloto aparecendo no Gerenciador de Eventos com deduplicação | 🟡 parser, mapa e payload prontos (modo simulação); falta implantar o endpoint e testar com a conta real |
| 3 | Conversões offline no Google (biblioteca oficial) + campos personalizados padrão no Kommo do piloto | upload aceito sem erro parcial; `gclid`/`fbclid`/`ctwa_clid` preenchidos em > 80% dos leads de mídia | 🟡 payload pronto; falta o envio |
| 4 | Normalização (`fato_midia`, `fato_eventos_crm`) + relatório diário + alertas operacionais (gasto zerado, entrega parada, reprovação, orçamento esgotado, tag sem disparar, SLA de WhatsApp) | relatório chegando todo dia no canal da operação, com CPL e CPL qualificado reais por campanha | ⬜ |
| 5 | Histórico de alterações + pacing mensal | toda alteração (nossa ou do cliente) registrada; projeção de gasto do mês no relatório | ⬜ |
| 6 | Fila de aprovação no ClickUp (L1) | uma sugestão aprovada no ClickUp executada e registrada, com reversão testada | ⬜ |

**Fora do MVP, de propósito:** motor bayesiano, alocação de verba, landing page nível 3, volante criativo completo, playbooks de outros segmentos, AI Max/PMax/Demand Gen.

## Fase 2 — Operação com 3–5 clientes

| Entrega | Depende de |
|---|---|
| Taxonomia de ângulos + renomeação dos anúncios existentes (Meta e Google) | MVP |
| Auditorias de onboarding automatizadas (Meta, Google, com estimativa de desperdício em termos de pesquisa) | conectores do MVP |
| Google M4 — negativas (varredura recorrente, L2 para categorias óbvias) | auditoria |
| Painel MTD no Looker Studio | normalização |
| Resumo semanal por WhatsApp ao cliente + relatório mensal | relatório diário |
| Níveis de autonomia L2 por tipo de ação | 30 dias de histórico de aprovações |
| Calendário sazonal | perfil + playbook |
| Extensão do wizard do briefing-trilha com as etapas de mídia | ADR-005 resolvido |

## Fase 3 — Inteligência

| Entrega | Depende de |
|---|---|
| Verificador de copy (anúncio, RSA, landing, WhatsApp) | taxonomia + `marca.yaml` |
| Métricas de criativo e framework de testes (Meta) | taxonomia |
| Estatística modo médio/alto: linha de base MAD, correção de atraso, encolhimento bayesiano | ≥ 1 cliente com 20+ conversões/dia |
| Detector de vencedores por anúncio e por etiqueta | estatística + taxonomia |
| Google M1/M2/M3 com padrões de proteção; M5 landing nível 2 | verificador de copy |
| Briefings e volante criativo, com esteira no ClickUp e peças no Canva | detector de vencedores |
| Base de referência da carteira (benchmarks anônimos) | ≥ 5 clientes no mesmo segmento |

## Fase 4 — Escala

Visão consolidada entre canais e alocação de verba · novos playbooks (educação, serviço local, saúde) · TikTok e LinkedIn · Google M7 (negócio local) · landing nível 3 · testes de AI Max, Demand Gen, YouTube e PMax como hipóteses por cliente.

## Indicadores do próprio sistema

Medidos desde o MVP, para saber se o Trilha está valendo a pena:
- Horas de operação por cliente por semana (meta: −50% em 6 meses).
- % de leads de mídia com identificador de clique gravado no CRM.
- CPL qualificado do cliente piloto antes × depois do retorno de conversão real.
- % de sugestões aprovadas sem alteração (calibra a liberação do nível L2).
- Retenção de clientes e tempo de onboarding.
