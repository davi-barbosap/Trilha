# Modelo Operacional — quem faz o quê · v0.5

> Status: aceito · 2026-10-03
> Este documento manda sobre os demais quando houver conflito sobre **quem faz o quê**.
> Técnico: [`ARQUITETURA-NUCLEO.md`](ARQUITETURA-NUCLEO.md) · Orquestração: [`docs/integracoes/N8N.md`](docs/integracoes/N8N.md) · Decisões: [ADR-007](docs/decisoes/007-n8n-orquestrador.md), [ADR-008](docs/decisoes/008-freio-de-emergencia.md)

## 1. Princípio

**O sistema faz o trabalho manual e prepara. O assessor decide, se relaciona com o cliente e alinha a equipe.**

O Trilha existe para devolver tempo. Não substitui o julgamento nem o relacionamento: chega **antes** de cada compromisso humano com o trabalho braçal pronto — dados coletados, conferidos com o CRM, comparados com a meta, sugestões ordenadas por impacto e rascunhos escritos.

## 2. Divisão de responsabilidades

| O assessor faz (sempre) | O sistema faz (sempre) |
|---|---|
| Pelo menos **uma sessão de otimização por cliente por semana** — decide e aprova toda mudança | Coleta diária de Meta, Google e Kommo; conferência plataforma × CRM |
| Pelo menos **um contato proativo por cliente por semana** | Retorno de conversão real (Kommo → Meta/Google) |
| Pelo menos **uma reunião mensal com cada cliente** | Cálculo de metas, pacing, desvios, testes em andamento |
| Pensar a estratégia e **combinar com a equipe** | Dossiês, pautas, pacotes de reunião, atas e painel da carteira |
| Toda comunicação com o cliente: canal, tom, conteúdo | Alertas de urgência fora da rotina |
| Toda decisão de verba, estrutura, criativo e oferta | Executar o que foi aprovado, registrar e guardar como desfazer |
| | Freio de emergência (§5) — a única ação sem aprovação prévia |

**O sistema nunca:** envia mensagem ao cliente · decide verba ou estratégia · fala com a equipe em nome do assessor · altera uma conta sem aprovação (exceto o freio) · promete algo ao consumidor.

## 3. Os rituais e o que o sistema entrega para cada um

### 3.1 Sessão semanal de otimização — por cliente

**Entrega: dossiê de otimização**, na véspera do `operacao.dia_otimizacao` do cliente, como tarefa no ClickUp (fluxo W12).

| Bloco do dossiê | Conteúdo |
|---|---|
| Placar da semana | gasto, leads, leads qualificados, agendamentos e vendas **pelo Kommo**, contra a meta da versão vigente do perfil; pacing do mês |
| O que mudou | alterações na conta desde a última sessão — nossas, do cliente, da plataforma — e o que aconteceu depois de cada uma |
| Decisões da semana passada | o que foi aprovado, o efeito observado, se confirmou ou não a hipótese |
| Sugestões (3 a 5) | ordenadas por R$ em jogo; cada uma com motivo, simulação antes → depois e risco (ex.: reinicia aprendizado) |
| Testes em andamento | hipótese, amostra atual × mínima, previsão de conclusão |
| Freio de emergência | o que foi pausado na semana, por quê, e se deve voltar |
| Atendimento | tempo até o primeiro contato e qualificação por corretor/atendente — antes de culpar a mídia |

**O assessor:** lê, decide, aprova/ajusta/recusa cada sugestão na própria tarefa. O sistema executa o aprovado, registra no histórico de alterações e comenta o resultado.
**Tempo-alvo:** 30–45 min por cliente.

### 3.2 Contato proativo semanal — por cliente

**Entrega: pauta de contato**, na véspera do `operacao.dia_contato` (fluxo W07).

- **Uma boa notícia com número** ("menor custo por visita agendada do trimestre: R$ 410").
- **Um ponto de atenção** ("6 leads qualificados sem retorno do corretor há mais de 48h").
- **Uma pergunta que só o cliente responde** ("os leads do Residencial X estão chegando com renda compatível?").
- **Rascunho de mensagem** no tom do `marca.yaml` e no `operacao.canal_contato` — para o assessor reescrever como quiser. **Nunca enviado pelo sistema.**

**Gatilhos de contato extra** (avisados ao assessor, não ao cliente): recorde positivo, queda brusca, verba acabando antes do fim do mês, problema de atendimento detectado no Kommo, freio acionado.
**Tempo-alvo:** 10–15 min por cliente.

### 3.3 Reunião mensal — por cliente

**Antes — pacote da reunião**, dois dias úteis antes (fluxo W11):
resultado contra a meta vigente no mês · o que foi testado e aprendido · decisões do mês e efeito · proposta para os próximos 30 dias · perguntas para o cliente · documento ou slides prontos para revisão.

**Depois — ata e encaminhamentos** (fluxo W13): o assessor grava ou dita os pontos; o sistema transforma em ata, abre tarefas no ClickUp com responsável e prazo, e — se meta, verba ou oferta mudaram — prepara a nova versão do `perfil.yaml` para validação.
**Tempo-alvo:** 15 min de preparação + a reunião.

### 3.4 Alinhamento com a equipe

**Entrega: painel da carteira e proposta de pauta**, na véspera da reunião de equipe (fluxo W14): semáforo por cliente (dentro da meta · atenção · crítico), tarefas atrasadas por pessoa, criativos pendentes, contratos e tokens perto de vencer, clientes sem contato na semana.
**O assessor:** pensa, combina e distribui.

## 4. Capacidade

Tempo do assessor por cliente, com o sistema preparando tudo:

| Ritual | Horas/semana |
|---|---|
| Sessão de otimização | 0,75 |
| Contato proativo | 0,25 |
| Reunião mensal + preparação (1h15 ÷ 4,3) | 0,30 |
| Parcela do alinhamento com a equipe | 0,25 |
| **Total por cliente** | **≈ 1,5** |

- **8 clientes ≈ 12 h/semana** de trabalho de alto valor (contra 80+ h no modelo manual).
- Teto saudável: **15–20 clientes** por assessor, sem perder a qualidade do relacionamento.
- O tempo liberado vai para estratégia, prospecção (calculadora da Camada 0, núcleo §3.5) e desenvolvimento da equipe.

Estimativas de partida — medir de verdade com os indicadores da §8.

## 5. Freio de emergência

A única ação automática ([ADR-008](docs/decisoes/008-freio-de-emergencia.md)). Protege a verba **entre** as sessões semanais, à noite e no fim de semana.

| Gatilho | Padrão (configurável no `perfil.yaml`) |
|---|---|
| Gasto sem lead | campanha gastou ≥ 3× o CPL máximo desde o último lead |
| Rastreamento quebrado | campanha gastando há ≥ 6h sem nenhum evento de conversão registrado |

| Modo | Comportamento |
|---|---|
| **`pausar` (opção A — padrão)** | pausa, avisa o assessor na hora com o motivo e o botão de desfazer; a decisão de reativar fica para o assessor |
| `avisar` (opção B) | só avisa; a pausa fica com o assessor |

Toda ação do freio entra no histórico de alterações e no dossiê da semana seguinte. Qualquer outra pausa, corte ou ajuste é **sugestão** no dossiê.

## 6. Agenda de referência para 8 clientes

| | Manhã | Tarde |
|---|---|---|
| **Segunda** | painel da carteira + reunião de equipe | otimização: clientes 1–2 |
| **Terça** | otimização: clientes 3–4 | contatos proativos: 1–4 |
| **Quarta** | otimização: clientes 5–6 | estratégia e prospecção |
| **Quinta** | otimização: clientes 7–8 | contatos proativos: 5–8 |
| **Sexta** | 2 reuniões mensais (4 semanas = 8 clientes) | fechamento da semana |

Cada cliente tem seus dias no bloco `operacao` do `perfil.yaml`; o sistema gera cada entrega na véspera, com dados frescos.

## 7. Faixas de serviço

Classificação pela nota de maturidade (núcleo §3.2), registrada em `operacao.faixa`:

| Faixa | Perfil do cliente | O que o sistema prepara | Exigência mínima |
|---|---|---|---|
| **Essencial** | rastreamento 0–1, verba perto da mínima | dossiê com placar e pacing, pauta de contato, pacote da reunião, freio | Kommo com etapas padronizadas |
| **Performance** | CRM integrado, verba 2–5× a mínima | + conversão real, conferência plataforma × CRM, análise por atendente | campos personalizados preenchidos em > 80% dos leads de mídia |
| **Escala** | histórico > 12 meses, verba > 5× a mínima | + testes estruturados, detector de vencedores, sugestão de alocação de verba | volume para o modo estatístico médio (núcleo §9.0) |

O ritual humano é o mesmo nas três faixas; muda a profundidade do que chega preparado.

## 8. Indicadores

**Da operação (mensais):**
- Horas do assessor por cliente por semana (meta: ≤ 1,5 h).
- % de semanas com sessão de otimização, contato proativo e reunião mensal cumpridos por cliente (meta: 100%).
- % de sugestões aprovadas sem alteração — mede a qualidade do dossiê; abaixo de 50% = sistema precisa de calibração.
- Falhas silenciosas (meta: zero).

**Da carteira:**
- % de clientes dentro da meta de CPL qualificado.
- % de leads de mídia com identificador de clique gravado no Kommo.
- Cancelamento (churn) e receita líquida retida.
- Margem por cliente.

## 9. Papéis

| Papel | Responsabilidade |
|---|---|
| **Assessor sênior** | todos os rituais da §3; estratégia; aprovações; relação com o cliente |
| **Analista** (quando houver) | primeira leitura dos alertas, produção e subida de criativos, onboarding técnico (campos do Kommo, rastreamento) |
| **Responsável técnico** (interno ou freelancer) | n8n, trilha-api, credenciais, backups — segue o runbook de [`N8N.md`](docs/integracoes/N8N.md) |
| **Sistema** | tudo da coluna direita da §2 |
