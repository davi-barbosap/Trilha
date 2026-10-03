# Núcleo Compartilhado — Sistema de Automação de Mídia Paga com Claude · v0.4

> Status: arquitetura + MVP em construção · 2026-10-03
> Este documento reúne tudo o que é **comum a todas as plataformas**: estratégia, onboarding, perfil do cliente, brand kit, playbooks de segmento, conversão real, motores estatísticos, governança.
> Módulos específicos: [`ARQUITETURA-META-ADS.md`](ARQUITETURA-META-ADS.md) · [`ARQUITETURA-GOOGLE-ADS.md`](ARQUITETURA-GOOGLE-ADS.md)
> Ordem de construção: [`ROADMAP.md`](ROADMAP.md) (único) · Decisões: [`docs/decisoes/`](docs/decisoes/) · Integrações: [`docs/integracoes/`](docs/integracoes/)
> Fonte do modelo de briefing de oferta e do playbook imobiliário: [`briefing-trilha`](https://github.com/beatriz-moraes082/briefing-trilha) — dependência formalizada em [ADR-005](docs/decisoes/005-dependencia-briefing-trilha.md).

### Changelog
- **v0.4** — Corte de MVP e roadmap único. Correções: `modelo_receita` (comissão ≠ ticket), fórmula de verba mínima viável e viabilidade da escada de otimização, modo de baixo volume como padrão estatístico, `ctwa_clid` no WhatsApp, GA4 e GTM server-side, portais imobiliários como fonte de lead, mapa de eventos do CRM por cliente, dados de clientes fora do repositório de código, esquema validado do perfil. Novos: níveis de autonomia, ritmo de gasto (pacing), calendário sazonal, base de referência da carteira, calculadora como ferramenta comercial, especificação de Kommo e ClickUp (fila de aprovação), registro de decisões de arquitetura (ADRs), código inicial em `trilha/`.
- **v0.3** — Documento de núcleo separado das plataformas. Novos: Camada 0 (diagnóstico e estratégia), onboarding em níveis, playbooks de segmento, brand kit em hierarquia marca → oferta (baseado no briefing-trilha), verificador de copy, taxonomia de ângulos, módulo WhatsApp, eventos de qualidade de lead via Kommo, correção de atraso de atribuição, histórico de alterações, alertas por impacto financeiro, visão consolidada entre canais, relatório ao cliente, governança e LGPD.
- **v0.2** — Implementação híbrida (MCP + código), conectores, normalização, conversão real.
- **v0.1** — Três camadas, perfil, regras derivadas.

---

## 1. Princípios

1. **Núcleo fixo, personalização por dados.** Nenhuma regra, meta ou número de cliente vive no código do núcleo.
2. **Negócio antes da conta de anúncios.** Metas derivam da economia unitária do cliente, não de chute.
3. **Opera com dado incompleto.** O sistema se ajusta ao nível de maturidade do cliente em vez de exigir tudo preenchido.
4. **Cálculo em código, nunca "de cabeça".** O modelo interpreta e recomenda; Python/R calcula.
5. **Conversão real acima da métrica da plataforma.**
6. **Concretude obrigatória.** Copy sem número, fato ou nome próprio é barrada.
7. **Coerência do funil inteiro.** Anúncio → landing page → WhatsApp → atendimento comercial falam a mesma coisa.
8. **Leitura livre, escrita com aprovação**, com simulação prévia e possibilidade de reversão.
9. **Respeito ao algoritmo.** Menos mexidas, mais bem fundamentadas; proteção da fase de aprendizado.
10. **Filtro humano obrigatório** em toda decisão que envolva verba ou promessa ao consumidor.

## 2. Visão geral das camadas

```
┌──────────────────────────────────────────────────────────────┐
│ CAMADA 0 — DIAGNÓSTICO E ESTRATÉGIA (onboarding)             │
│  economia unitária · maturidade · auditoria · plano 90 dias  │
└──────────────────────────────┬───────────────────────────────┘
┌──────────────────────────────▼───────────────────────────────┐
│ CONECTORES   Meta (MCP/API) · Google Ads API · GA4 ·         │
│              CRM (Kommo) · WhatsApp · portais · planilhas    │
└──────────────────────────────┬───────────────────────────────┘
┌──────────────────────────────▼───────────────────────────────┐
│ CAMADA 1 — NÚCLEO                                            │
│  normalização · motores · estatística · histórico de         │
│  alterações · conversão real · saídas · registro de decisões │
└──────────────────────────────┬───────────────────────────────┘
┌──────────────────────────────▼───────────────────────────────┐
│ CAMADA 2 — CLIENTE = playbook do segmento + respostas do     │
│  onboarding + ajustes   (perfil · marca · ofertas · avatares)│
└──────────────────────────────┬───────────────────────────────┘
┌──────────────────────────────▼───────────────────────────────┐
│ CAMADA 3 — REGRAS DERIVADAS (calibração automática)          │
└──────────────────────────────────────────────────────────────┘
```

### 2.1 Infraestrutura (decidida)

| Peça | Decisão | Registro |
|---|---|---|
| Armazenamento | Postgres gerenciado para eventos, alterações e decisões; BigQuery para histórico de mídia (transferência nativa do Google Ads, exportação do Meta) | [ADR-001](docs/decisoes/001-armazenamento.md) |
| Orquestração | Funções em contêiner (Cloud Run) acionadas por webhook (Kommo, ClickUp) e por agendador; sem ferramenta no-code no caminho crítico | [ADR-002](docs/decisoes/002-orquestracao.md) |
| Painel | Looker Studio sobre BigQuery (padrão); Metabase se o cliente exigir login próprio | [ADR-003](docs/decisoes/003-painel.md) |
| Dados de clientes | Fora do repositório de código: repositório privado `trilha-clientes` ou banco; aqui só `clientes/_exemplo/` | [ADR-004](docs/decisoes/004-dados-de-clientes.md) |
| Esquema comum | Tabela `fato_midia` diária (data, plataforma, conta, campanha, conjunto/grupo, anúncio, etiquetas da taxonomia, gasto, impressões, cliques, conversões por evento) e `fato_eventos_crm` (lead, evento, data, origem, IDs de clique) | §7 e `trilha/` |
| Validação de configuração | Todo YAML de cliente é validado por esquema (`python -m trilha validar`) antes de ligar qualquer módulo | `trilha/core/perfil.py` |

## 3. Camada 0 — Diagnóstico e estratégia

Roda no onboarding de todo cliente e é revisada a cada trimestre. Produz quatro saídas antes de qualquer campanha.

### 3.1 Calculadora de economia unitária (matemática reversa)

**Primeiro passo: qual é a receita real de uma venda.** O campo `modelo_receita` evita o erro mais caro do onboarding — usar o preço do produto como se fosse receita.

| `modelo_receita` | Receita bruta por venda | Exemplo |
|---|---|---|
| `venda_direta` | ticket médio | curso de R$ 3.000 |
| `comissao` | valor médio do bem × % de comissão × participação do cliente na comissão | imóvel de R$ 450.000 × 5% × 50% = **R$ 11.250** (não R$ 450.000) |
| `recorrencia` | mensalidade × meses médios de retenção (LTV) | R$ 300 × 14 meses = R$ 4.200 |

| Entrada | Exemplo imobiliário |
|---|---|
| Receita bruta por venda (acima) | R$ 11.250 |
| Margem de contribuição sobre a receita | 50% |
| % da margem que aceita investir em aquisição | 50% |
| Taxa de fechamento (lead → venda) | 1% |
| Taxa de qualificação (lead → lead qualificado) | 25% |
| Taxa de agendamento (lead → visita/reunião) — opcional | 5% |

Saídas derivadas (implementadas em `trilha/core/economia.py`):
- **CAC máximo** = receita bruta × margem × % investível → R$ 2.812
- **CPL máximo** = CAC máximo × taxa de fechamento → R$ 28
- **CPL qualificado máximo** = CAC máximo × (fechamento ÷ qualificação) → R$ 112
- **Custo máximo por agendamento** = CAC máximo × (fechamento ÷ agendamento) → R$ 562
- **Verba mensal por degrau da escada de otimização** = eventos semanais para sair do aprendizado (padrão 50, configurável) × custo máximo do evento × 4,35 semanas
  - `lead` → R$ 6.115 · `lead_qualificado` → R$ 24.459 · `agendamento` → R$ 122.294 · `venda` → R$ 611.468
- **Verba mínima viável** = verba do degrau `lead` (o mais barato) para **um** conjunto/campanha. Abaixo dela, o sistema recomenda uma plataforma, uma oferta, uma campanha — e avisa que os números serão de leitura lenta.
- **Degraus viáveis** = degraus cuja verba cabe na verba planejada. O sistema **diz explicitamente** ao cliente quando otimizar por lead qualificado é inviável para a verba dele (é o caso da maioria das PMEs) e aplica as alternativas da §7.2.
- **Ponto de equilíbrio** e metas por fase (aprendizado, otimização, escala).

Validação: taxa de qualificação ≥ agendamento ≥ fechamento; quando o cliente não sabe uma taxa, usa-se o padrão do playbook do segmento, marcado como **estimado** até haver dado próprio. Os padrões do playbook são conservadores (imobiliário: fechamento 1%, não 5%).

### 3.2 Nota de maturidade

| Dimensão | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Rastreamento | nada | pixel/tag básico | eventos + API de Conversões/tag avançada | conversão real retornando à plataforma |
| CRM | nenhum | planilha/WhatsApp manual | CRM sem integração | CRM integrado com status de qualificação |
| Capacidade criativa | sem material | fotos/artes avulsas | produção mensal | produção recorrente + vídeo/UGC |
| Histórico de conta | conta nova | < 3 meses | 3–12 meses | > 12 meses com conversões |
| Verba | abaixo da mínima viável | na mínima | 2–5× mínima | > 5× mínima |

A nota **liga e desliga módulos** e define regras: um cliente com rastreamento 0 não recebe detector de vencedores por conversão (só por métricas intermediárias, sinalizadas como tal); um cliente com verba abaixo da mínima recebe recomendação de concentrar em uma plataforma e uma oferta.

### 3.3 Auditoria inicial

Checklist técnico por plataforma (pixel/API de Conversões, tag, eventos, estrutura, nomenclatura, políticas, acessos, histórico de reprovações), gerado automaticamente onde houver acesso de leitura. Saída: lista priorizada de correções.

### 3.4 Plano de 90 dias

| Fase | Duração típica | Objetivo | Meta |
|---|---|---|---|
| Fundação | semanas 1–2 | rastreamento, estrutura, primeiros criativos | conta pronta, eventos validados |
| Aprendizado | semanas 3–6 | volume de dados, testes de ângulo | CPL ≤ 1,3× máximo |
| Otimização | semanas 7–10 | cortar perdedores, iterar vencedores | CPL ≤ máximo, qualificação ≥ meta |
| Escala | semanas 11–13 | aumentar verba com controle | manter CPL qualificado com mais volume |

### 3.5 Calculadora como ferramenta comercial da agência

A mesma calculadora roda **antes do contrato**, na prospecção: em 15 minutos de conversa, o prospect vê quanto pode pagar por lead, qual verba mínima faz sentido e o que é inviável para o tamanho dele. Isso qualifica o prospect (verba abaixo da mínima = proposta diferente ou recusa) e posiciona a agência como consultoria de negócio, não como operadora de botão.

- Saída: uma página de diagnóstico com marca da agência (CAC/CPL máximos, verba por degrau, plano de 90 dias resumido).
- Os dados de prospecção alimentam o onboarding se o contrato fechar — nada é preenchido duas vezes.

## 4. Onboarding flexível

### 4.1 Composição do cliente

```
cliente final = playbook do segmento  (padrões)
              + respostas do onboarding (sobrescrevem)
              + ajustes manuais        (sobrescrevem tudo)
```

Cada campo tem um nível:
- **Obrigatório** — sem ele o sistema não liga (ex.: métrica principal, conta de anúncios, oferta).
- **Recomendado** — usa padrão do playbook, marcado como `estimado`, e lembra de pedir.
- **Opcional** — enriquece, nunca bloqueia.

O sistema sempre informa **o que está usando como padrão** e qual o impacto de não ter o dado real.

### 4.2 Wizard único de onboarding

Reaproveitar o wizard do `briefing-trilha` (Streamlit, validação por etapa, avisos contextuais, publicação no ClickUp), acrescentando etapas de mídia. O `briefing-trilha` pertence a outro repositório; a forma de consumo (versão fixada, contrato de dados, responsável) está em [ADR-005](docs/decisoes/005-dependencia-briefing-trilha.md). O contrato entre os dois é o esquema validado do perfil: o wizard produz YAML, o Trilha valida. Uma reunião com o cliente gera de uma vez:

| Saída | Usada por |
|---|---|
| `marca.yaml` | anúncios, landing pages, fluxos de WhatsApp |
| `ofertas/<oferta>.yaml` | criativos, RSAs, landing pages, fluxos Kommo |
| `perfil.yaml` | motores, metas, regras derivadas |
| Fluxos Kommo (JSON) | atendimento (já existente no briefing-trilha) |
| Task no ClickUp | operação |

Etapas adicionais ao wizard atual:
1. Negócio e economia unitária (§3.1)
2. Maturidade (§3.2)
3. Identidade visual e voz da marca (§5.1)
4. Plataformas, contas e acessos
5. Métrica principal, metas e sazonalidade
6. Entrega de relatórios e alertas

### 4.3 Versionamento do perfil

Metas, ofertas e condições comerciais mudam. Cada alteração no perfil gera nova versão com data, e os relatórios comparam resultados contra a meta **vigente na época**, não a atual.

## 5. Brand kit

Hierarquia em três níveis. O nível **oferta** segue o molde do briefing de empreendimento do `briefing-trilha`, generalizado para qualquer segmento.

```
MARCA      identidade, voz, compliance, regras comerciais — vale para tudo
  └── OFERTA   produto/serviço/empreendimento/curso — diferenciais, objeções, condições
        └── CAMPANHA   ângulo, avatar, criativos, período
```

### 5.1 `marca.yaml`

```yaml
marca:
  nome: ""
  segmento: ""                      # aponta para playbooks/<segmento>/
identidade_visual:
  cores: { primaria: "", secundaria: "", apoio: [] }
  tipografia: { titulos: "", texto: "" }
  logo: { arquivo: "", versoes: [] }
  estilo_imagem: ""                 # ex.: fotos reais da obra; sem banco de imagem genérico
voz:
  assinatura: ""                    # marca | pessoa | marca_pessoa
  nome_pessoa: ""                   # quando assinatura inclui pessoa
  abordagem: ""                     # scripted | conversacional | misto
  pessoa_gramatical: ""             # eu | nós | impessoal (derivado da assinatura)
  tom: []                           # ex.: próximo, direto, sem gíria
  assim_sim: []                     # 3–5 exemplos reais aprovados
  assim_nao: []                     # 3–5 exemplos reprovados e por quê
  termos_obrigatorios: []
  termos_proibidos: []
atendimento:
  sla_resposta: ""                  # 30min | 2h | dia | 24h+
  handoff: ""                       # direto | bot | horario
  canais: []                        # WhatsApp, Instagram Direct...
  horario_comercial: ""
regras_comerciais:                  # o que pode aparecer em cada canal
  preco:
    anuncio: ""                     # nunca | a_partir_de | parcela | valor_cheio
    whatsapp: ""                    # padrão imobiliário: nunca valor fechado → simulação/agendamento
    landing: ""
  promessas_proibidas: []           # ex.: "aprovação garantida", "sem consulta"
compliance:
  registros_profissionais: []       # ex.: CRECI, CRM, OAB — com número e onde exibir
  categoria_especial_anuncio: null  # verificar regras da plataforma por país
  avisos_legais: []
  lgpd: { base_legal: "", politica_privacidade_url: "" }
prova_social:
  depoimentos_video: []
  depoimentos_texto: []
  numeros: []                       # ex.: "+500 famílias atendidas" — com fonte
```

Regra de derivação: a **assinatura** define a pessoa gramatical e o formato criativo preferencial. `pessoa` → primeira pessoa, criativos com o próprio profissional em vídeo; `marca` → institucional; `marca_pessoa` → apresentação pessoal com respaldo da marca.

### 5.2 `ofertas/<oferta>.yaml`

Generalização das etapas 2–7 e 10 do wizard do `briefing-trilha`:

```yaml
oferta:
  nome: ""
  tipo: ""                          # empreendimento, curso, serviço, produto
  estagio: ""                       # lançamento, em andamento, pronto, últimas vagas/unidades
  localizacao: { bairro: "", cidade_uf: "", regiao: "" }   # quando aplicável
diferenciais:                       # mínimo 3 — número, fato ou nome próprio
  - ""
raridade: ""                        # diferencial único no mercado local
ancoras:                            # mínimo 3 quando localização importa — nome próprio + distância/tempo
  - ""
condicoes_comerciais:
  faixa_preco: ""
  ticket_medio: null
  pagamento: ""
  condicao_excepcional: ""          # com prazo de validade, se houver
  validade: ""
  posicionamento_preco: ""          # abaixo | média | acima dos concorrentes — e por quê
objecoes:                           # o insumo mais importante
  - eixo: ""                        # eixos definidos pelo playbook do segmento
    objecao: ""
    resposta_do_time: ""            # frase real usada ao vivo
perfil_lead:
  origem_principal: ""
  perfil: ""
  jornada_media_dias: null          # alimenta janela de atribuição e atraso de conversão
  motivo_perda: ""
assets:
  imagens: []
  videos: []
  materiais: []                     # PDFs, tabelas, plantas
```

### 5.3 Verificador de copy

Roda antes de qualquer peça ir para revisão humana (anúncio Meta, RSA Google, landing page, mensagem de WhatsApp):

| Verificação | Origem |
|---|---|
| Afirmação sem número, fato ou nome próprio → bloquear ou pedir dado | princípio de concretude do briefing-trilha |
| Termo proibido / promessa proibida / preço fora da regra do canal | `marca.yaml` |
| Pessoa gramatical incoerente com a assinatura | `marca.yaml` |
| Registro profissional ausente quando obrigatório | `compliance` |
| Limites de caracteres e políticas da plataforma | módulo da plataforma |
| Coerência com a oferta e com a landing de destino | `ofertas/` |

### 5.4 Taxonomia de ângulos (liga brand kit e motores)

Todo criativo, anúncio e mensagem recebe etiquetas, de preferência codificadas no nome:

`eixo · objeção tratada · avatar · formato · gancho · oferta · versão`

- **Eixos** vêm do playbook do segmento (imobiliário: preço, produto, localização).
- Com as etiquetas, o detector de vencedores responde **qual argumento converte** para qual avatar, não apenas qual anúncio.
- Cobertura obrigatória: a régua de criativos (e de nutrição no WhatsApp) cobre todos os eixos do segmento; o sistema sinaliza eixos sem teste.

## 6. Playbooks de segmento

```
playbooks/<segmento>/
├── playbook.yaml        # eixos de objeção, métricas típicas, taxas padrão, sazonalidade,
│                        # regras comerciais padrão, compliance do setor
├── negativas.md         # palavras-chave negativas do segmento (Google)
├── avatares_base.md     # pontos de partida, refinados por cliente
├── objecoes_e_apelos.md # framework de objeção → copy
└── fluxos/              # fluxos de atendimento padrão
```

**Imobiliário (primeiro playbook)** — derivado do `briefing-trilha`; arquivo em [`playbooks/imobiliario/playbook.yaml`](playbooks/imobiliario/playbook.yaml):
- `modelo_receita: comissao` por padrão — a receita é a comissão retida, não o valor do imóvel.
- Taxas padrão conservadoras: fechamento 1%, qualificação 25%, agendamento 5% (sempre marcadas como estimadas).
- **Portais imobiliários** (ZAP, VivaReal, OLX e similares) são fonte de lead de primeira classe: entram no Kommo com origem própria, contam no CAC total e na visão consolidada, e servem de referência de custo por lead para comparar com mídia paga.
- Eixos: preço, produto, localização — todos obrigatórios na régua.
- Regra padrão: preço pedido no WhatsApp → simulação/agendamento, nunca valor fechado. Em anúncio, configurável (ex.: valor de parcela pode filtrar lead).
- Compliance: CRECI; verificar regras de categoria especial de anúncio para habitação conforme país e plataforma.
- Fluxos: pré-atendimento, follow-up curto, nutrição por eixo, apresentação escalonada, pré-atendimento 1x1 escalonado (corretor autônomo).
- Reaproveita: `objecoes_e_apelos.md`, `anatomia_*.md`, `build_kommo_json.py`, guarda anti-saudação.

Próximos playbooks: educação, serviço local, saúde, e-commerce — mesmo molde, com eixos próprios (ex.: educação → preço, resultado, método/tempo).

## 7. Conversão real e qualidade de lead

### 7.1 Fluxo

```
Anúncio → landing / formulário / WhatsApp
   → captura de IDs de clique e UTMs:
       site: fbclid · gclid · gbraid/wbraid · UTMs (campos ocultos; GTM server-side grava cookies próprios)
       clique para WhatsApp: ctwa_clid (vem no webhook da conversa) · site → WhatsApp: código curto na mensagem
       formulário instantâneo do Meta: lead_id do Meta
   → CRM (Kommo): lead + origem + campanha + criativo (campos personalizados padrão — ver integração Kommo)
   → mudança de etapa no funil (webhook do Kommo)
   → mapa etapa → evento, configurado por cliente (crm.mapa_eventos no perfil.yaml)
   → (a) banco: fato_eventos_crm → painel com CPL, CPL qualificado, CAC e ROAS reais por campanha, ângulo e termo
   → (b) retorno às plataformas: Meta (API de Conversões, event_id para deduplicação) · Google (conversões offline por gclid; conversões otimizadas para leads com dados em hash quando o gclid se perde)
```

**GA4 e GTM server-side.** GA4 é a referência de comportamento no site (origem, engajamento, funil da landing) e a fonte de públicos; não é a fonte da verdade de conversão — o CRM é. O GTM server-side é o caminho padrão para o pixel + API de Conversões do Meta e a tag do Google em domínio próprio, reduzindo perda por bloqueadores e restrições de cookie.

Especificação técnica completa: [`docs/integracoes/KOMMO.md`](docs/integracoes/KOMMO.md). Código: `trilha/integracoes/kommo.py`, `trilha/plataformas/meta/capi.py`, `trilha/plataformas/google/conversoes_offline.py`.

### 7.2 Mapa de eventos de qualidade

Os status do funil Kommo (já previstos no briefing-trilha) viram eventos padronizados. **Os IDs de funil e de etapa mudam em cada conta Kommo**, então o mapa vive no `perfil.yaml` de cada cliente (`crm.mapa_eventos`); apenas as etapas de sistema do Kommo são fixas (142 = venda ganha, 143 = perdida) e entram como padrão.

| Status Kommo | Evento padrão | Retorno à plataforma |
|---|---|---|
| Lead entrou | `lead` | sim (otimização inicial) |
| Interesse confirmado (pós pré-atendimento) | `lead_qualificado` | sim — **evento de otimização preferido** quando houver volume |
| Visita/reunião agendada | `agendamento` | sim |
| Venda (etapa 142) | `venda` (+ valor) | sim — base para ROAS-alvo |
| Descartado / não cadastrou (etapa 143) | `desqualificado` | uso interno (e sinal negativo onde suportado) |
| Reativado (respondeu nutrição) | `reativado` | uso interno |

**Quando o volume não sustenta otimizar por `lead_qualificado`** (§3.1 — o caso comum em PME):
1. Otimizar por `lead`, mas com atrito qualificador na origem (perguntas no formulário, mensagem pré-preenchida que exige uma escolha, faixa de preço/parcela no anúncio quando a regra comercial permite).
2. Enviar todos os eventos de qualidade mesmo assim: eles alimentam o painel, os relatórios e, nas plataformas, os modelos de qualidade de lead.
3. Quando a plataforma aceitar valor por evento, atribuir **valor ponderado** a cada degrau (ex.: `lead` = CPL máximo; `lead_qualificado` = CPL qualificado máximo; `venda` = receita) e otimizar por valor — sinal mais rico sem exigir volume de um único evento.
4. Reavaliar a cada mês: o sistema recomenda subir de degrau quando o evento superior atinge o volume semanal configurado.

### 7.3 Módulo WhatsApp

No Brasil, a conversão principal costuma ser a conversa, não o formulário.
- **Rastreamento — anúncio de clique para WhatsApp:** a conversa iniciada pelo anúncio traz o `ctwa_clid`, que o Kommo (ou a integração com a API do WhatsApp Business) grava no lead. É esse identificador que permite devolver ao Meta os eventos de qualidade da conversa pela API de Conversões para mensagens.
- **Rastreamento — site → WhatsApp:** botão com mensagem pré-preenchida contendo um código curto da campanha/criativo, lido pelo Kommo e gravado no lead.
- **Atendimento:** fluxos do playbook (pré-atendimento, follow-up, nutrição) gerados a partir da mesma oferta usada nos anúncios — coerência garantida pela fonte única.
- **Velocidade de resposta:** o SLA do `marca.yaml` é monitorado; SLA estourado vira alerta, porque destrói a taxa de qualificação e contamina a leitura de desempenho dos anúncios.
- **Atendimento × mídia:** tempo até o primeiro contato e taxa de qualificação **por atendente/corretor** separam problema de mídia de problema de atendimento — antes de cortar uma campanha, verifica-se quem atendeu os leads dela.

### 7.4 Outras fontes de lead

Portais (imobiliário), indicação, orgânico e lista própria entram no CRM com `origem` padronizada. Não recebem retorno de conversão, mas entram no CAC total e na visão consolidada (§8) para que a mídia paga não seja julgada isoladamente nem receba crédito por vendas de outra origem.

## 8. Motores do núcleo

| Motor | O que faz | Detalhes de plataforma |
|---|---|---|
| Relatórios | pontual, histórico, MTD com metas da versão vigente do perfil | em cada documento de plataforma |
| Anomalias | contas e campanhas, boas e más | §9 |
| Vencedores/potenciais | por anúncio, ângulo e termo | §9 |
| Histórico de alterações | registra toda edição (nossa ou do cliente) com data, autor, antes/depois | correlaciona com anomalias |
| Conversão real | §7 | — |
| Visão consolidada | Meta + Google + orgânico: CAC total, custo de mídia ÷ receita, participação de cada canal | evita contar a mesma venda duas vezes |
| Alocação de verba | recomenda distribuição entre canais e ofertas pelo CAC marginal | sempre como recomendação |
| Relatório ao cliente | narrativa mensal em linguagem de negócio, marca branca | §11 |
| Ritmo de gasto (pacing) | projeta o gasto até o fim do mês contra a verba contratada, por plataforma e campanha; avisa sub ou sobre-entrega com dias de antecedência | complementa o alerta de "orçamento esgotado cedo" |
| Calendário sazonal | datas do segmento (lançamentos, feirões, Black Friday, matrículas) e do cliente; marca períodos fora da linha de base e antecipa ajustes de verba e criativo | `playbooks/<segmento>/playbook.yaml` + `perfil.yaml` |
| Base de referência da carteira | benchmarks anônimos por segmento, região e plataforma (CPL, taxa de qualificação, CPM) calculados sobre todos os clientes; recalibra os padrões dos playbooks | só agregados, nunca dado de um cliente exposto a outro |

## 9. Estatística e alertas

### 9.0 Modo por volume (padrão: baixo volume)

A maioria da carteira-alvo (PME, imobiliário, serviço local) tem **menos de 20 conversões por dia** — muitas vezes menos de 1 lead qualificado por dia. O motor estatístico é ligado em camadas, pela nota de volume de cada conta:

| Modo | Quando | O que roda |
|---|---|---|
| **Baixo volume** (padrão) | < 20 conversões/dia na conta | alertas operacionais (§9.3) · pacing · comparação de janelas de 7/14/28 dias contra meta · divergência plataforma × CRM · regras simples de corte com gasto mínimo (ex.: anúncio com gasto ≥ 2× CPL máximo e zero lead) |
| **Médio** | 20–100/dia | + linha de base mediana/MAD por dia da semana, correção de atraso de atribuição |
| **Alto** | ≥ 100/dia | + encolhimento bayesiano, controle de falsos alarmes entre muitas comparações |

Nenhum alerta estatístico é exibido sem o mínimo de dados da faixa; abaixo disso, o sistema diz "dados insuficientes para conclusão" em vez de produzir um número instável.

### 9.1 Correções obrigatórias antes de ligar alertas

- **Atraso de atribuição:** conversões chegam com atraso (janela de atribuição + jornada média da oferta). Os últimos N dias são corrigidos pela curva histórica de maturação da conta, ou excluídos da comparação, e marcados como "parciais".
- **Contagens, não razões:** com poucas conversões, CPA/CPL diário é instável. Modelar conversões como contagem dado o gasto (Poisson / binomial negativa) e só então derivar o custo.
- **Sazonalidade semanal:** linha de base comparando com os mesmos dias da semana.
- **Períodos marcados** no perfil (promoções, lançamentos, datas) ficam fora da linha de base.
- **Muitas comparações:** controlar a taxa de falsos alarmes ao testar várias campanhas × métricas × janelas (ex.: limiar ajustado ou controle de taxa de descoberta falsa).

### 9.2 Método

- Linha de base robusta: mediana + MAD (métricas contínuas, como CPM) ou modelo de contagem (conversões).
- Vencedores: encolhimento bayesiano em direção à média da conta/campanha (Beta-Binomial para taxas, Gamma-Poisson para conversões por gasto); classificação por probabilidade posterior de bater a meta, ex.: `P(CPL < máximo) > 0,8`.
- Janelas e frequência calibradas pelo volume:

| Conversões/dia | Janelas | Frequência de alertas | Requisito mínimo |
|---|---|---|---|
| ≥ 100 | 1, 3, 7 dias | até 4×/dia | gasto baixo |
| 20–100 | 3, 7, 14 dias | 1–2×/dia | gasto moderado |
| < 20 | 7, 14 dias | 1×/dia | gasto alto + mínimo de conversões |

### 9.3 Priorização por impacto

- Todo alerta mostra **R$ em risco por dia** (ou oportunidade) e é ordenado por isso.
- Limite de alertas por relatório; o resto vai para um anexo.
- **Alertas operacionais** sempre passam, independentemente de estatística: gasto zerado, entrega parada, reprovação, orçamento esgotado cedo, tag/pixel sem disparar, SLA de WhatsApp estourado.
- Alerta logo após uma alteração registrada é anotado como "possivelmente causado por alteração de <data>".

### 9.4 Protocolo de testes

Todo teste (criativo, ângulo, landing, lance) é registrado antes de começar:
`hipótese · variável testada · métrica de decisão · amostra mínima · duração máxima · regra de decisão`.
Testes sem volume para atingir a amostra mínima não são abertos — o sistema sugere testar uma variável de maior impacto ou concentrar verba.

## 10. Operação, segurança e governança

- **Níveis de autonomia** (configurados por cliente e por tipo de ação, no `perfil.yaml`):

  | Nível | O sistema… | Exemplos |
  |---|---|---|
  | L0 | só lê | relatórios, auditoria |
  | L1 | sugere; humano aprova (padrão) | orçamento, estrutura, novos anúncios, lances |
  | L2 | aplica sozinho **dentro de limites** e avisa | negativas de categorias óbvias (emprego, grátis, concorrente já decidido); pausar anúncio com gasto ≥ 2× CPL máximo e zero lead; reativar anúncio pausado por engano dentro do mesmo dia |
  | L3 | nunca automático | qualquer aumento de verba acima do teto contratado, promessa ao consumidor, ação em conta sem histórico |

  Toda ação L2 entra no histórico de alterações, é reversível e aparece no relatório do dia. Um cliente novo começa em L1 em tudo; L2 é liberado por tipo de ação depois de 30 dias sem reversão de sugestões daquele tipo.
- **Fila de aprovação no ClickUp:** ações L1 viram tarefas com a simulação antes → depois; mudar o status para "Aprovado" executa a ação (ver [`docs/integracoes/CLICKUP.md`](docs/integracoes/CLICKUP.md)).
- **Simulação antes de escrever:** toda alteração mostra o "antes → depois" e o impacto estimado; aplicação só após aprovação.
- **Reversão:** toda escrita guarda o estado anterior para desfazer.
- **Proteção do algoritmo:** recomendações agrupadas em janelas (ex.: 1–2×/semana por campanha); bloqueio de alterações estruturais durante fase de aprendizado, salvo emergência.
- **Monitoramento das rotinas:** se uma tarefa agendada não rodar ou falhar, aviso imediato (falha silenciosa é o pior cenário).
- **Acessos:** o cliente é dono das contas; a agência entra como parceira. Checklist de entrada e de saída do cliente (remover acessos, entregar dados e relatórios).
- **Segredos:** `.env` fora do Git; `.env.example` só com os nomes.
- **Dados de clientes fora do repositório de código** ([ADR-004](docs/decisoes/004-dados-de-clientes.md)): margens, tickets, regras comerciais e qualquer dado pessoal vivem em repositório privado separado ou no banco. Aqui fica só `clientes/_exemplo/`; o `.gitignore` bloqueia o resto.
- **LGPD:** base legal e aviso de privacidade nas landing pages e formulários; dados pessoais enviados às plataformas sempre com hash; captura do mínimo necessário; política de retenção e exclusão no CRM; registro de quais dados vão para quais plataformas.
- **Custo de tokens:** dados volumosos processados no script; só resumos chegam ao modelo.

## 11. Saídas

| Saída | Público | Frequência | Conteúdo |
|---|---|---|---|
| Alertas | operação | conforme volume | priorizados por R$ em risco |
| Relatório diário | operação | diário | métrica principal vs. meta, anomalias, vencedores, ações sugeridas |
| Painel MTD | operação | ao vivo | mesmo layout para todos os clientes |
| Auditoria semanal | operação | semanal | o que pausar, escalar, corrigir, testar |
| Relatório ao cliente | cliente | mensal | resultado de negócio, o que foi testado e aprendido, próximos passos — sem jargão |
| Resumo por WhatsApp | cliente | semanal | 5 linhas (ou áudio curto): leads, qualificados, vendas, gasto vs. plano, próxima ação — o cliente de PME não abre painel |
| Registro de decisões | operação | contínuo | sugestão → decisão → resultado; base de calibração |

**Canais de entrega:** alertas e relatório diário vão para um canal da operação (Slack ou grupo de WhatsApp interno), com link para o painel; ações pendentes vão para a fila de aprovação no ClickUp.

**Hierarquia de métricas por cliente** (definida no perfil): métrica de negócio (vendas, CAC) → métrica principal da plataforma (CPL qualificado, ROAS) → métricas de diagnóstico (CPM, CTR, retenção de vídeo). Relatórios nunca apresentam métrica de diagnóstico como resultado.

## 12. Estrutura do repositório

Legenda: ✅ existe · 🔜 próximo no [ROADMAP](ROADMAP.md) · ⏳ depois.

```
/
├── README.md · ROADMAP.md · ARQUITETURA-*.md
├── docs/
│   ├── decisoes/              ✅ ADRs (armazenamento, orquestração, painel, dados de clientes, briefing-trilha, autonomia)
│   └── integracoes/           ✅ KOMMO.md · CLICKUP.md · OUTRAS.md
├── trilha/                    pacote Python
│   ├── core/
│   │   ├── perfil.py          ✅ esquema validado do perfil.yaml
│   │   ├── economia.py        ✅ calculadora de economia unitária, verba por degrau
│   │   ├── normalizacao/      🔜 fato_midia / fato_eventos_crm
│   │   ├── motores/           🔜 relatório diário, alertas operacionais, pacing · ⏳ anomalias, vencedores, alocação
│   │   ├── estatistica/       ⏳ maturação, contagens, MAD, encolhimento, testes
│   │   ├── historico/         🔜 registro de alterações
│   │   ├── copy/              ⏳ verificador de copy, taxonomia de ângulos
│   │   └── saidas/            🔜 templates de alertas e relatórios
│   ├── conversao/
│   │   ├── hash.py            ✅ normalização e SHA-256 de e-mail/telefone
│   │   └── pipeline.py        ✅ webhook Kommo → eventos → envios
│   ├── integracoes/
│   │   ├── kommo.py           ✅ parser de webhook, leitura de lead, extração de IDs
│   │   └── clickup.py         🔜 fila de aprovação
│   ├── plataformas/
│   │   ├── meta/capi.py       ✅ payload e envio da API de Conversões
│   │   └── google/conversoes_offline.py  ✅ payload de conversão offline (envio pela biblioteca oficial: 🔜)
│   └── __main__.py            ✅ CLI: validar · calcular · simular-webhook
├── tests/                     ✅ unittest (sem dependência externa)
├── playbooks/imobiliario/     ✅ playbook.yaml (demais arquivos 🔜)
├── clientes/_exemplo/         ✅ perfil.yaml · marca.yaml · ofertas/
├── onboarding/                ⏳ extensão do wizard do briefing-trilha
└── .env.example               ✅
```

Clientes reais: repositório privado `trilha-clientes` (mesma estrutura de `clientes/_exemplo/`), apontado por `TRILHA_CLIENTES_DIR`.

## 13. Roadmap

Um único roadmap para núcleo e plataformas, com o corte de MVP: [`ROADMAP.md`](ROADMAP.md).

## 14. Plataformas e canais futuros

Mesmo núcleo, novo módulo em `plataformas/`, ativado pela Camada 0 quando o segmento justificar:
- **TikTok Ads** — públicos jovens, educação, varejo; mesmo módulo criativo e taxonomia do Meta.
- **LinkedIn Ads** — clientes B2B; lead gen nativo com retorno de qualidade pelo CRM.
- **Orgânico** (Instagram, Perfil da Empresa no Google, SEO local) — entra primeiro como **fonte medida** na visão consolidada, depois como módulo de conteúdo alimentado pelos mesmos ângulos vencedores.
