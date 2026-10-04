# Origem dos padrões operacionais

Padrões extraídos dos repositórios de `github.com/beatriz-moraes082` (operação da Trilha Performance) e onde cada um entrou neste sistema.

## Repositórios lidos

| Repositório | O que é | Padrões extraídos | Onde entrou |
|---|---|---|---|
| `mensuracao-ibr` | Painel de mídia e funil do Ipioca Beach Residence (Kommo + Meta + Google) | dicionário oficial de métricas; vários funis (SDR, Closer, Nutrição, base importada, teste) com o 142 mudando de sentido; venda pela data de fechamento; deduplicação de leads por telefone e mês e de vendas por pessoa/dia/valor/produto; canal normalizado com "Não rastreado"; CAC teto e ROAS piso; CPO por canal; origem no contato quando o lead está vazio; coleta que falha alto em credencial recusada e mantém os últimos dados bons; dados pessoais mascarados na origem | [métricas](metricas.md), `crm.funis`, `funil.deduplicar`, `atribuicao.py`, [Kommo](integracoes/kommo.md) §3.2 |
| `mensuracao-mme` | Painel do Ipioca Mar Resort + fluxos do bot + relatórios de análise | régua oficial de lead score (A–D) definida pela gestora do CRM; respostas do bot mudam entre versões; tag "Interagiu" (resgate humano); relatório mensal (resumo, funil por semana w1–w4, metas, financeiro, público, criativo, score, vendas e jornada, sem atribuição, recomendações) | funil por score, pré-atendimento no raio-x, semanas w1–w4, pacote da reunião ([modelo operacional](modelo-operacional.md) §3.4) |
| `trilha-painel` | Painel de saúde da carteira (todos os clientes, por assessor) | catálogo da carteira (segmentos automotivo, hotelaria, imobiliário; assessores); saldo pré-pago, dias de saldo, recarga de 30 dias, status da conta; alertas P1/P2 com ação e responsável; relatório automático sem atualizar | `saude.py`, rota `/contas/saude`, painel da carteira |
| `ranking-corretores-lion` | Ranking de corretores para TV (Supremo CRM) | leads parados há +15 dias; baldes do sistema que não são pessoas; qualificador × corretor; vendas pela data da venda; perfil comparativo com score composto | leads parados, `por_closer`, exclusão de baldes, amostra mínima |
| `ni-report` | Relatório comercial a partir de planilhas de corretores + Meta | status livres normalizados em categorias; motivos de perda categorizados; plano de ação por regra (perdas "não responde" > 30% → resgatar a base antes de aumentar volume; leads sem status → padronizar) | sinais do raio-x, motivos do playbook padrão |
| `maia-dash` | Painel comercial (TeciMob + Meta) | estrutura do painel: visão geral, funil, corretores, horários, campanhas, plano de ação | material do relatório e do pacote da reunião |
| `bossa-site` | Landing page (GitHub Pages) | atribuição first-touch por sessão (UTMs, gclid, gbraid, wbraid, fbclid); payload com esquema fixo para o webhook do CRM; GTM | contrato de interface das landing pages ([ecossistema](ecossistema.md) §3) |
| `briefing-trilha` | Wizard de briefing de empreendimento → fluxos Kommo → ClickUp | estrutura do ClickUp (espaço de clientes, uma pasta por cliente, lista "Operação"); contexto do atendimento (assinatura, abordagem, handoff); objeções reais; regras de copy | ficha da oferta, `marca.yaml`, [ClickUp](integracoes/clickup.md), ADR-005 |

## Não lidos

O pedido foi de 32 repositórios. Neste ambiente, a listagem da conta no GitHub está bloqueada; os nomes acima foram encontrados por busca. O `trilha-painel` cita 17 repositórios de relatório por cliente (`motochefe-report`, `taiyo-report`, `pontaverde-report`, `niterceiros-report`, `lion-report`, `cros-report`, `inove-report`, `thiago-report`, `maia-report`, `fellipe-report`, `adelmo-report`, `andaza-report`, `queiroz-report`, `henrique-report`, `ype-report`, `rafaella-report`, `renato-vidal-report`), todos privados para a conta usada aqui. Os demais não foram identificados.

## Também observado (fora do escopo)

- Outros CRMs na carteira (Supremo, TeciMob, planilhas). O sistema segue só com Kommo ([ADR-007](decisoes/007-escopo-do-sistema.md)); os padrões de normalização valem para quando outro CRM for necessário.
- Rotinas de tags no Kommo (estado do bot, "Interagiu") rodam como automação paralela; o raio-x lê as tags.
- Painéis por cliente publicados no GitHub Pages: são a camada de relatório existente e devem seguir o mesmo [dicionário de métricas](metricas.md).
