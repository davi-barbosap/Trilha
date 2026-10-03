# Sistema de Automação Meta Ads com Claude — Arquitetura v0.6

> Status: arquitetura + MVP em construção · 2026-10-03
> **Leia primeiro:** [`ARQUITETURA-NUCLEO.md`](ARQUITETURA-NUCLEO.md) — estratégia, onboarding, perfil, brand kit, playbooks, conversão real, estatística e governança são compartilhados e não se repetem aqui.
> Documento irmão: [`ARQUITETURA-GOOGLE-ADS.md`](ARQUITETURA-GOOGLE-ADS.md)
> Referência inicial: "Claude + Facebook Ads (FULL COURSE)" — Sam Piliero / The Moonlighters, com adaptações e melhorias próprias.

### Changelog
- **v0.6** — Escopo (ADR-009): o "volante criativo" vira **pacote de dados do briefing** — o sistema reúne os dados; briefing, roteiro e peças são do assessor e da equipe de criação. API de Conversões na Graph API v26.0. Atendimento no WhatsApp (Kommo/BotConversa) é ferramenta paralela; aqui só o rastreamento.
- **v0.5** — Alinhado ao [`MODELO-OPERACIONAL.md`](MODELO-OPERACIONAL.md). Regra de "perdedor" passa a ser sugestão no dossiê semanal; pausa automática só pelo freio de emergência (ADR-008). Achados de criativo (fadiga, vencedores, diversidade) entram no dossiê, não em alertas.
- **v0.4** — Campanhas Advantage+ como estrutura padrão a avaliar; diversidade criativa como alavanca principal de entrega; `ctwa_clid` e API de Conversões para mensagens no destino WhatsApp; GTM server-side; alternativas quando o volume não sustenta otimizar por lead qualificado; regra de vencedor relativa (substitui o limite fixo de 5% do gasto); roadmap movido para o `ROADMAP.md` único.
- **v0.3** — Conteúdo comum movido para o núcleo. Novos: estratégia de estrutura de conta, escolha de destino (site, formulário instantâneo, WhatsApp), auditoria de pixel/API de Conversões, framework de testes criativos com taxonomia de ângulos e métricas de criativo, proteção da fase de aprendizado, volante criativo condicionado à maturidade.
- **v0.2** — Implementação híbrida, conectores, normalização, conversão real.
- **v0.1** — Três camadas, perfil, regras derivadas.

---

## 1. Papel do Meta no sistema

O Meta **gera demanda**: alcança quem ainda não está procurando. O principal fator de desempenho é o **criativo** (argumento, gancho, formato), seguido do sinal de conversão que a conta devolve ao algoritmo. Segmentação detalhada e microgestão de lances pesam cada vez menos. A arquitetura reflete isso: o módulo criativo e o retorno de conversões são o centro; o monitoramento protege a verba.

## 2. Implementação

| Função | Ferramenta |
|---|---|
| Acesso aos dados | MCP oficial da Meta (via Claude Code ou chat) |
| O que o MCP não cobrir | Marketing API (Graph API) via scripts |
| Cálculos | núcleo (`core/estatistica`, `core/motores`) |
| Contexto do cliente | `marca.yaml`, `ofertas/`, `avatares.md`, playbook do segmento |
| Consultas do dia a dia | chat com o conector |

**Conector MCP:** URL indicada na referência `https://mcp.facebookads.com/ads`; liberação gradual — validar por conta no onboarding.

**Permissões**
| Ferramenta | Política |
|---|---|
| Insights e leitura de entidades | sempre permitir |
| Edição de orçamento, campanha, conjunto, anúncio | sempre exigir aprovação (com simulação prévia — ver núcleo §10) |
| Criação e publicação | sempre exigir aprovação |

## 3. Auditoria de onboarding (Meta)

Complementa a auditoria geral do núcleo (§3.3):

- [ ] Business Manager do cliente; agência com acesso de parceiro (não dona dos ativos)
- [ ] Pixel instalado e disparando os eventos certos; deduplicação com a API de Conversões
- [ ] API de Conversões ativa (servidor ou via CRM) e qualidade de correspondência dos eventos
- [ ] Domínio verificado e eventos priorizados
- [ ] Evento de otimização atual vs. evento ideal pela maturidade (ver §5)
- [ ] Estrutura atual: nº de campanhas/conjuntos, fragmentação, conjuntos presos em aprendizado
- [ ] Nomenclatura compatível com a taxonomia de ângulos (núcleo §5.4)
- [ ] Histórico de reprovações e restrições da conta; categoria especial de anúncio quando aplicável
- [ ] Biblioteca de criativos existente, etiquetada por eixo/avatar/formato

## 4. Estrutura de conta

Princípio: **consolidar** para dar volume de sinal ao algoritmo e sair rápido da fase de aprendizado.

**Campanhas Advantage+** (vendas, leads, app) são hoje o formato que o Meta empurra como padrão: público, posicionamento e parte do orçamento ficam a cargo do algoritmo. O sistema as trata como **primeira opção a avaliar** em toda conta com evento de conversão confiável, comparando com a estrutura manual consolidada abaixo pelo protocolo de testes do núcleo (§9.4). Pré-requisitos: retorno de conversão real funcionando (sem ele, Advantage+ otimiza para lead barato) e exclusão de clientes atuais configurada quando o objetivo for aquisição. Os nomes e o escopo desses produtos mudam com frequência — validar na conta antes de recomendar.

| Situação do cliente | Estrutura recomendada |
|---|---|
| Verba na mínima viável | 1 campanha de conversão, orçamento no nível da campanha, público amplo, 3–6 criativos por eixo |
| Verba 2–5× mínima | + 1 campanha de teste criativo separada da campanha de escala |
| Várias ofertas (ex.: empreendimentos, cursos) | 1 campanha por oferta só quando a verba sustenta o volume mínimo por campanha; senão, ofertas agrupadas com criativos distintos |
| Base de clientes/leads disponível | públicos semelhantes como teste contra o amplo; exclusão de clientes atuais quando o objetivo for aquisição |
| Remarketing | só com volume de visitantes/engajamento suficiente; senão, deixar o amplo cuidar |

Fase de aprendizado: o sistema estima se cada conjunto tem volume para sair do aprendizado (referência de ~50 eventos de otimização por semana) e recomenda consolidar quando não tiver.

## 5. Destino e evento de otimização

| Destino | Quando usar | Cuidados |
|---|---|---|
| **WhatsApp (clique para conversar)** | atendimento consultivo, ticket médio/alto, público que prefere conversar | gravar o `ctwa_clid` da conversa no lead do Kommo e devolver eventos de qualidade pela API de Conversões para mensagens (`action_source: business_messaging`); o SLA de resposta decide o resultado |
| **Formulário instantâneo** | volume alto, baixo atrito | leads de pior qualidade; usar perguntas qualificadoras e retornar qualificação ao Meta |
| **Site / landing page** | oferta que precisa de explicação ou prova; e-commerce | pixel + API de Conversões via GTM server-side, deduplicados por `event_id`; coerência com o anúncio |

**Escada de evento de otimização** (sobe conforme volume e maturidade):
`lead` → `lead_qualificado` (status "interesse confirmado" no Kommo) → `agendamento` → `venda`.
O sistema recomenda subir de degrau quando o evento superior atinge volume semanal suficiente.

**Viabilidade:** a Camada 0 (núcleo §3.1) calcula a verba mensal de cada degrau. Exemplo imobiliário: ~R$ 6 mil/mês para otimizar por `lead`, ~R$ 24 mil/mês para `lead_qualificado` em um único conjunto. Para a maioria das PMEs o degrau `lead_qualificado` é inviável; nesses casos valem as alternativas do núcleo §7.2 (atrito qualificador na origem, todos os eventos de qualidade enviados mesmo assim, valor ponderado por degrau).

**Implementação do retorno:** `trilha/plataformas/meta/capi.py` monta o evento (dados em hash, `event_id` = `kommo-<lead>-<evento>` para deduplicação, `lead_id` do formulário instantâneo, `fbc` a partir do `fbclid`, `ctwa_clid` para WhatsApp) e envia em modo simulação por padrão.

## 6. Módulo criativo

### 6.1 Taxonomia (obrigatória)

Todo anúncio é nomeado e etiquetado conforme o núcleo §5.4:
`eixo · objeção · avatar · formato · gancho · oferta · versão`

Exemplo imobiliário: `PRECO_parcela-cabe_jovem-casal_video-corretor_pergunta_resid-x_v2`.

### 6.2 Métricas de criativo

| Métrica | O que diz |
|---|---|
| Taxa de retenção nos 3 primeiros segundos | força do gancho |
| Retenção do vídeo (ThruPlay / % assistido) | força do desenvolvimento |
| CTR do link | força da promessa e da chamada |
| Custo por resultado / por lead qualificado | eficiência real |
| Taxa de qualificação por criativo (via Kommo) | se o criativo atrai o público certo |
| Frequência e queda de desempenho ao longo do tempo | fadiga |

Diagnóstico combinado: gancho forte + CTR fraco → promessa ou chamada fraca; CTR alto + qualificação baixa → criativo atraindo público errado.

### 6.3 Framework de testes

- **Conceito novo** (novo eixo, avatar ou formato): busca grandes saltos; testado na campanha de teste.
- **Iteração** (mesmo conceito, novo gancho/título/abertura): explora um vencedor.
- Proporção inicial sugerida: ~30% da produção em conceitos novos, ~70% em iterações — ajustada pelo registro de decisões.
- **Diversidade criativa é a nova segmentação.** Com público amplo e Advantage+, o algoritmo usa as diferenças entre criativos para encontrar públicos diferentes. Variações quase iguais (mesma imagem, título trocado) competem entre si; conceitos realmente distintos (eixo, avatar, formato, pessoa em cena) ampliam alcance. A taxonomia de ângulos mede essa diversidade: o sistema alerta quando os criativos ativos se concentram em um único eixo ou formato.
- Todo teste segue o protocolo do núcleo (§9.4): hipótese, amostra mínima, duração máxima, regra de decisão.
- Cobertura: o sistema aponta eixos do playbook sem criativo ativo ou sem teste recente.

### 6.4 Vencedores e potenciais

A regra da referência ("> 5% do gasto da campanha") não discrimina nada com 3–6 criativos — quase todos passam de 5%. Substituída por critérios **relativos**, avaliados no modo estatístico da conta (núcleo §9.0):
- **Participação relativa de entrega** = participação no gasto ÷ participação esperada (1 ÷ nº de criativos ativos no conjunto). Acima de 1,5 = o algoritmo está preferindo o criativo.
- **Vencedor:** participação relativa ≥ 1,5 **e** métrica principal dentro da meta (em baixo volume: CPL na janela de 14–28 dias ≤ máximo, com gasto mínimo de 2× CPL máximo; em alto volume: `P(CPL < máximo) > 0,8` pelo encolhimento bayesiano) → iterar.
- **Potencial:** só uma das condições → ajustar (gancho, título, formato).
- **Perdedor:** gasto ≥ 2× CPL máximo sem lead, ou participação relativa < 0,5 por 14 dias com métrica fora da meta → ponto de atenção no dossiê semanal (o assessor decide se pausa). Pausa automática só quando o gasto passa do limite do freio de emergência (3× CPL máximo sem lead, ADR-008).
- Análise também por **etiqueta**: quais eixos, avatares e ganchos vencem de forma persistente.

### 6.5 Pacote de dados do briefing

O briefing é do assessor; o sistema reúne os dados que ele precisaria levantar à mão (fluxo W08, [MODELO-OPERACIONAL.md](MODELO-OPERACIONAL.md) §3.3):

| Dado | Fonte |
|---|---|
| Vencedores e potenciais, por anúncio e por etiqueta (eixo, avatar, formato, gancho) | §6.4 |
| Criativos em fadiga | §7 |
| Eixos do segmento sem criativo ativo ou sem teste recente | taxonomia (núcleo §5.4) |
| Objeções e motivos de perda registrados no Kommo | Kommo |
| Diferenciais, objeções e respostas do time, voz e assinatura da marca | `ofertas/`, `marca.yaml` |
| Limite de criativos ativos por conjunto e capacidade criativa do cliente | perfil, nota de maturidade (núcleo §3.2) |

Saída: o modelo de briefing do time de criação com esses campos preenchidos. Ângulo, gancho, roteiro e pedido ao time de criação são escritos pelo assessor; peças são produzidas pela equipe de criação.

## 7. Monitoramento específico do Meta

Somam-se aos motores do núcleo:

Urgências vão para o Slack na hora; o resto entra no dossiê semanal de otimização (MODELO-OPERACIONAL §3.1).

| Achado | Gatilho | Vai para |
|---|---|---|
| Conjunto preso em aprendizado / aprendizado limitado | sem volume para sair | dossiê |
| Fadiga de criativo | frequência subindo + queda de CTR/retenção no mesmo criativo | dossiê |
| CPM anômalo | estatística do núcleo (mediana/MAD, dia da semana) | dossiê |
| Reprovação ou restrição | sempre | urgência |
| Qualidade de correspondência da API de Conversões caiu | sempre | urgência |
| Divergência pixel × CRM | leads no Meta muito acima/abaixo dos leads no Kommo | dossiê (urgência se > 50%) |

## 8. Estrutura no repositório

```
trilha/plataformas/meta/
├── conector/        # MCP / Marketing API, normalização para o esquema comum
├── auditoria/       # checklist de onboarding
├── estrutura/       # recomendações de consolidação e aprendizado
├── criativos/       # taxonomia, métricas, testes, pacote de dados do briefing
└── capi.py          # ✅ retorno de eventos de qualidade (via Kommo) — trilha/plataformas/meta/capi.py
```

## 9. Roadmap Meta

Movido para o [`ROADMAP.md`](ROADMAP.md) único (núcleo + plataformas, com corte de MVP).

## 10. Riscos específicos

- Acesso ao MCP em liberação gradual.
- Formulário instantâneo sem qualificação gera volume enganoso.
- Excesso de criativos fragmenta a verba e mantém conjuntos em aprendizado.
- Categoria especial de anúncio (habitação, crédito, emprego) restringe segmentação — verificar regras vigentes por país.
- Mudanças frequentes de estrutura reiniciam o aprendizado; daí as janelas de recomendação do núcleo.
- Advantage+ sem conversão real otimiza para o lead mais barato, não para o melhor.
- Os nomes, limites e requisitos dos produtos do Meta (Advantage+, API de Conversões para mensagens, categorias especiais) mudam com frequência — toda recomendação estrutural é validada na conta do cliente.
