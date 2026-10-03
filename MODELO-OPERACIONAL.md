# Modelo Operacional — quem faz o quê · v0.6

> Status: aceito · 2026-10-03
> Escopo do sistema e ferramentas paralelas: [`ECOSSISTEMA.md`](ECOSSISTEMA.md) · Técnico: [`ARQUITETURA-NUCLEO.md`](ARQUITETURA-NUCLEO.md) · Orquestração: [`docs/integracoes/N8N.md`](docs/integracoes/N8N.md)
> Decisões: [ADR-007](docs/decisoes/007-n8n-orquestrador.md) (n8n), [ADR-008](docs/decisoes/008-freio-de-emergencia.md) (freio), [ADR-009](docs/decisoes/009-escopo-do-sistema.md) (escopo)

## 1. Princípio

**O sistema executa o trabalho manual. O assessor pensa, decide e se relaciona com o cliente.**

O Trilha deixa pronto, na véspera, o material de cada compromisso do assessor: dados coletados, conferidos com o Kommo, comparados com a meta, organizados e com as contas feitas. O que fazer com isso é decisão do assessor.

## 2. O cargo e o sistema

Responsabilidades e indicadores do cargo de Assessor de Marketing, e o que o sistema faz em cada um:

| No cargo | O assessor | O sistema |
|---|---|---|
| **Gestão de tráfego** — criação, otimização e monitoramento (Meta, Google) | decide tudo na sessão semanal; cria campanhas e anúncios | coleta, pacing, urgências, freio; dossiê da sessão; executa o que for aprovado |
| **Copy & briefing** — briefings para criação com base em dados | escreve a estratégia do briefing e a copy | pacote de dados do briefing (o que converte, o que cansou, objeções e motivos de perda) |
| **Relatórios** — análises semanais e mensais com insights | escreve os insights e apresenta | números e gráficos do relatório semanal (leads · criativos · ações) e do pacote mensal |
| **Atendimento** — principal ponto de contato | **100% humano** | — |
| **CRM** — jornada do lead no funil | acompanha e cobra o time comercial do cliente | conversão real e dados do funil do Kommo nos relatórios |
| **Automações** — fluxos de CRM, disparos, landing pages | configura | **fora deste sistema** — ferramentas paralelas ([ECOSSISTEMA.md](ECOSSISTEMA.md)) |
| KPI: 1 otimização semanal por cliente | faz | dossiê na véspera |
| KPI: ≥ 1 reunião mensal por cliente | conduz | pacote dois dias úteis antes |
| KPI: feedbacks semanais (leads, criativos, ações) | dá o feedback | o relatório semanal traz os números dos três blocos |
| KPI: ≥ 3 contatos proativos por cliente por semana | **faz, sem participação do sistema** | — |
| KPI: tempo de resposta no grupo ≤ 2 h | **faz, sem participação do sistema** | — |
| KPI: 100% das tarefas no ClickUp no mesmo dia | registra | **fora deste sistema** — automação paralela no n8n |

**O sistema nunca:** fala com o cliente · escreve mensagem, roteiro ou estratégia · decide verba, estrutura ou criativo · altera uma conta sem aprovação (exceto o freio, §4) · mede ou cobra o contato do assessor com o cliente.

## 3. O que fica pronto para cada compromisso

### 3.1 Sessão semanal de otimização (por cliente)

**Dossiê de otimização**, na véspera do `operacao.dia_otimizacao`, como tarefa no ClickUp:

| Bloco | Conteúdo |
|---|---|
| Placar | gasto, leads, leads qualificados, agendamentos e vendas **pelo Kommo**, contra a meta vigente do perfil; pacing do mês |
| O que mudou | alterações na conta desde a última sessão (nossas, do cliente, da plataforma) e o que veio depois |
| Decisões anteriores | o que foi aprovado na semana passada e o efeito observado |
| Pontos de atenção | 3 a 5 achados ordenados por R$ em jogo, cada um com os números que o sustentam e a simulação das ações possíveis |
| Testes em andamento | amostra atual × mínima, previsão de conclusão |
| Freio | o que foi pausado na semana e por quê |
| Funil do cliente | tempo até o primeiro contato e qualificação por corretor/atendente (dados do Kommo) |

**O assessor** decide o que fazer. Mudanças simples (orçamento, pausar/ativar) ele marca na tarefa e o sistema executa, registra e guarda como desfazer. Campanhas e anúncios novos, ele cria.
**Tempo-alvo:** 30–45 min por cliente.

### 3.2 Relatório semanal ao cliente

**Números do relatório**, na véspera do `operacao.dia_relatorio`, em três blocos — os mesmos três tipos de feedback que o cargo pede:

| Bloco | Números |
|---|---|
| **Leads** | quantos chegaram, qualificaram, agendaram e compraram; custo de cada etapa; motivos de perda; comparação com a semana anterior e com a meta |
| **Criativos** | desempenho por anúncio e por argumento; o que está cansando; o que entrou e saiu |
| **Ações** | o que foi feito na conta na semana (do histórico de alterações) e o resultado até agora |

**O assessor** escreve os insights, decide o formato e entrega. O sistema não envia nada ao cliente.
**Tempo-alvo:** 15 min por cliente.

### 3.3 Briefing de criativo

**Pacote de dados do briefing**, junto com o dossiê e sob demanda:
- argumentos (eixos), públicos e formatos com melhor e pior resultado;
- criativos que estão cansando;
- objeções e motivos de perda registrados no Kommo;
- diferenciais e objeções da oferta (`ofertas/*.yaml`);
- o modelo de briefing do time de criação com esses campos preenchidos.

**O assessor** escreve a estratégia: o ângulo, a mensagem, o pedido ao time de criação.
**Tempo-alvo:** 20–30 min por briefing.

### 3.4 Reunião mensal

**Pacote da reunião**, dois dias úteis antes: resultado contra a meta vigente no mês, testes e aprendizados, decisões do mês e efeito, números de apoio para a proposta dos próximos 30 dias, e documento ou slides com os dados para o assessor completar.

**O assessor** prepara a narrativa, conduz e registra os combinados. (Transformar a ata em tarefas é da automação paralela de captura de tarefas.)

### 3.5 Alinhamento com a equipe

**Painel da carteira**, na véspera da reunião de equipe: semáforo por cliente (dentro da meta · atenção · crítico), freio acionado na semana, tarefas atrasadas por pessoa e criativos pendentes (lidos do ClickUp), tokens de integração perto de vencer.

## 4. Freio de emergência

A única ação sem aprovação prévia ([ADR-008](docs/decisoes/008-freio-de-emergencia.md)). Protege a verba entre as sessões semanais, à noite e no fim de semana.

| Gatilho | Padrão (configurável no `perfil.yaml`) |
|---|---|
| Gasto sem lead | campanha gastou ≥ 3× o CPL máximo desde o último lead |
| Rastreamento quebrado | campanha gastando há ≥ 6 h sem nenhum evento de conversão |

| Modo | Comportamento |
|---|---|
| **`pausar` (opção A, padrão)** | pausa, avisa o assessor na hora com o motivo e o botão de desfazer |
| `avisar` (opção B) | só avisa |

Reativar é sempre decisão do assessor.

## 5. Capacidade (estimativa realista)

Horas do assessor por cliente por semana:

| Atividade | Sem o sistema | Com o sistema |
|---|---|---|
| Sessão de otimização (levantar dados + decidir) | 2,5 | 0,75 |
| Execução que continua manual (criar campanhas e anúncios, subir criativos) | 0,75 | 0,75 |
| Relatório semanal (números + insights) | 1,5 | 0,25 |
| Briefing de criativo (dados + estratégia) | 1,0 | 0,4 |
| Contatos proativos (≥ 3) e respostas no grupo (≤ 2 h) | 1,0 | 1,0 |
| Reunião mensal + preparação (÷ 4,3 semanas) | 0,6 | 0,3 |
| Equipe e registro no ClickUp | 0,3 | 0,3 |
| **Total por cliente** | **≈ 7,6 h** | **≈ 3,75 h** |

- **8 clientes ≈ 30 h por semana** com o sistema, contra ~60 h sem ele.
- **Teto saudável: cerca de 10 clientes por assessor.** O sistema corta o trabalho de levantar e organizar dados; o relacionamento e a execução criativa continuam tomando tempo, e é assim que deve ser.
- Estimativas de partida. A semana 5 do [ROADMAP](ROADMAP.md) mede as horas reais.

## 6. Agenda de referência para 8 clientes

| | Manhã | Tarde |
|---|---|---|
| **Segunda** | painel da carteira + reunião de equipe | otimização: clientes 1–3 |
| **Terça** | otimização: clientes 4–6 | execução e briefings |
| **Quarta** | otimização: clientes 7–8 | execução e briefings |
| **Quinta** | relatórios semanais: clientes 1–8 | execução |
| **Sexta** | 2 reuniões mensais (4 semanas = 8 clientes) | fechamento da semana |

Contatos proativos e respostas no grupo acontecem ao longo de todos os dias. Os dias de cada cliente ficam no bloco `operacao` do `perfil.yaml`.

## 7. Faixas de serviço

Classificação pela nota de maturidade (núcleo §3.2), em `operacao.faixa`:

| Faixa | Perfil do cliente | Profundidade do material | Exigência mínima |
|---|---|---|---|
| **Essencial** | rastreamento 0–1, verba perto da mínima | placar, pacing, freio, relatório semanal | Kommo com etapas padronizadas |
| **Performance** | Kommo integrado, verba 2–5× a mínima | + conversão real, plataforma × Kommo, dados por atendente, pacote de briefing | identificador de clique em > 80% dos leads de mídia |
| **Escala** | histórico > 12 meses, verba > 5× a mínima | + testes estruturados, vencedores por argumento | volume para o modo estatístico médio (núcleo §9.0) |

## 8. Indicadores do sistema

Medem se o sistema está cumprindo o papel dele (os indicadores do cargo são do assessor):

- Horas do assessor por cliente por semana (meta ≤ 3,75 h).
- Dossiês, relatórios e pacotes entregues **na véspera** (meta 100%).
- % de leads de mídia com identificador de clique no Kommo (meta > 80%).
- % de conversões aceitas por Meta e Google sem erro.
- Falhas silenciosas (meta zero).

## 9. Papéis

| Papel | Responsabilidade |
|---|---|
| **Assessor** | tudo da coluna "o assessor" da §2 |
| **Analista** (quando houver) | criação e subida de campanhas aprovadas, organização de criativos |
| **Responsável técnico** (interno ou freelancer) | n8n, trilha-api, credenciais, backups — segue o runbook de [N8N.md](docs/integracoes/N8N.md); também é o ponto de contato com quem cuida das ferramentas paralelas |
