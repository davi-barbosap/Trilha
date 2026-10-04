# Dicionário de métricas da Trilha

> Fonte: metodologia dos painéis de mensuração da Trilha (`mensuracao-ibr`, `mensuracao-mme`), conferida com `ranking-corretores-lion` e `ni-report`. Ver [origem dos padrões](origem-dos-padroes.md).
> Implementação: `trilha/core/funil.py` (raio-x), `trilha/core/atribuicao.py` (canal), `trilha/core/saude.py` (contas).

Todo número que o sistema mostra — dossiê, relatório, pacote da reunião, painel — segue estas definições. Painéis de cliente que usam outra regra precisam ser alinhados a esta, não o contrário.

## Entrada

| Métrica | Definição |
|---|---|
| **Lead** | Negócio criado nos funis de **entrada** (SDR) e de **nutrição** dentro do período. O funil de **fechamento** (Closer) não entra: ele recria o mesmo lead com outro id. Funis de **base** importada e de **teste** ficam fora de leads, CPL e taxa de qualificação. |
| **Deduplicação de leads** | A mesma pessoa (telefone) conta **uma vez por mês de entrada**. Quem entrou em julho e voltou em agosto é uma entrada de julho e uma de agosto. Quem tem card no SDR e na Nutrição conta uma vez, pelo SDR. |
| **Canal** | Campo "Origem" (do lead ou do contato) normalizado: Meta+Ads/Facebook/Instagram → **Meta Ads**; google → **Google Ads**; vazio, "unknown" ou lixo → **Não rastreado**. Origem sem regra sai com o nome que o CRM registrou, nunca num balde "outros". |
| **Leads de mídia paga** | Leads com canal Meta Ads ou Google Ads. É o divisor dos custos. |

## Funil

| Métrica | Definição |
|---|---|
| **Lead qualificado** | Chegou à etapa de qualificado, a reunião agendada ou a reunião realizada — ou tem tag de reunião. Quem agendou passou pela qualificação, mesmo que o card tenha voltado de etapa. |
| **Reunião agendada** | Contada **por pessoa** e pela **data marcada**; quem remarca conta 1. As marcações (remarcação = 2) aparecem como número secundário. |
| **Reunião realizada / comparecimento** | No funil de entrada, o "ganho" (142) costuma significar reunião realizada — configurado em `crm.funis[].ganho_significa`. Entra no período pela **data em que aconteceu**, por pessoa. |
| **Oportunidade** | Lead que chegou a reunião realizada: o no-show já está descontado. |
| **Proposta** | Card do Closer nas etapas de proposta (enviada, follow-up, sinal verde, dados de venda solicitados). |
| **Venda** | Só o "ganho" (142) do funil de **fechamento**, com **data de fechamento** dentro do período (não a data de criação do lead). O mesmo 142 num funil de entrada não é venda. |
| **Deduplicação de vendas** | Mesma pessoa, mesmo dia, mesmo valor e mesmo produto = o mesmo negócio cadastrado duas vezes. Duas unidades para a mesma pessoa no mesmo dia são duas vendas. |
| **Valor vendido / receita** | Soma do valor dos negócios ganhos no período (VGV no imobiliário). |
| **Ciclo de vendas** | Mediana de dias entre o **primeiro card da pessoa** nos funis de entrada e o fechamento (cards casados pelo telefone). |
| **Conversão SDR** | Reuniões realizadas ÷ leads de entrada. |
| **Conversão Closer** | Vendas ÷ reuniões realizadas (aproximada em janela curta; converge em janela longa). |

## Custo e retorno

| Métrica | Fórmula | Leitura |
|---|---|---|
| **Investimento** | gasto de mídia paga (Meta por conjunto, Google por campanha), dia a dia | — |
| **CPL** | investimento ÷ leads de mídia paga | **diagnóstico**, nunca resultado; não divide pelo total de leads |
| **CPL qualificado** | investimento ÷ qualificados de mídia paga | métrica principal de plataforma |
| **Custo por reunião** | investimento ÷ todas as reuniões realizadas | **piso** (inclui reuniões de lead orgânico) |
| **CPO por canal** | investimento do canal ÷ reuniões realizadas do canal | o número honesto para comparar canais |
| **CAC / custo por venda** | investimento ÷ vendas com canal Meta ou Google | **teto**: vendas sem rastreio ficam fora |
| **Retorno (ROAS)** | valor das vendas de mídia paga ÷ investimento | **piso**: receita sem rastreio fica fora |

Canais sem gasto medido (orgânico, indicação, não rastreado) ficam com custo **em branco**, não zero.

## Time comercial do cliente

| Métrica | Definição |
|---|---|
| **Primeiro contato** | Tempo entre a entrada do lead e o primeiro contato (ou a qualificação, quando o CRM não registra a primeira resposta). |
| **Interagiu (resgate)** | Houve mensagem enviada **por um humano** e o lead respondeu **depois** dela. Resposta espontânea ao bot não conta. |
| **Pré-atendimento (bot)** | não iniciado (nunca respondeu) · incompleto · concluído (respondeu a última pergunta). |
| **Leads parados** | Leads ativos (sem venda nem perda) sem nenhuma movimentação há mais de 15 dias, por responsável. |
| **Perfil por pessoa** | Comparado ao melhor do time no período (100 = alguém do time, não uma meta). Só entra quem tem amostra: SDR com 20+ leads, closer com 5+ reuniões. Baldes do sistema ("DESCARTE", "sem corretor") não são pessoas. |
| **Ritmo e prazo de tarefas** | Ritmo = mediana de dias entre criar e concluir; prazo = concluídas dentro do vencimento. O Kommo não expõe data de conclusão: usa-se a última alteração da tarefa. |

## Qualidade do lead

| Métrica | Definição |
|---|---|
| **Lead score** | Classificação (A, B, C…) feita pelo bot ou pela régua do CRM do cliente. A régua é do cliente (ex.: régua oficial definida pela gestora do CRM) e muda entre versões do bot; o sistema lê o score gravado no Kommo e mostra o funil **por score**. |

## Períodos e comparações

- **Semanas do mês:** w1 = dias 1–7, w2 = 8–14, w3 = 15–21, w4 = 22 até o fim do mês.
- **Comparação:** sempre com a janela imediatamente anterior, do mesmo tamanho.
- **Eventos datados:** reunião pela data em que aconteceu, venda pela data de fechamento. O raio-x de safra (leads que entraram no período) e os indicadores do período (eventos que aconteceram no período) são leituras diferentes e aparecem identificadas.
- **Períodos com apagão de rastreio** ficam fora do comparativo de CPL (mediriam o rastreio, não a mídia), mas os leads seguem contados.

## Contas de anúncio

| Métrica | Definição |
|---|---|
| **Dias de saldo** | saldo pré-pago ÷ gasto médio diário dos últimos 7 dias. Menos de 5 dias = P1 (recarga esta semana); menos de 10 = P2 (avisar o cliente). |
| **Recarga sugerida** | gasto médio diário × 30. |
| **Status da conta** | qualquer status diferente de ativa (desativada, em revisão, suspensa) = P1. |
