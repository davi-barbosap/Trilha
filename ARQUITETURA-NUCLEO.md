# Núcleo Compartilhado — Sistema de Automação de Mídia Paga com Claude · v0.3

> Status: rascunho de arquitetura · 2026-10-02
> Este documento reúne tudo o que é **comum a todas as plataformas**: estratégia, onboarding, perfil do cliente, brand kit, playbooks de segmento, conversão real, motores estatísticos, governança.
> Módulos específicos: [`ARQUITETURA-META-ADS.md`](ARQUITETURA-META-ADS.md) · [`ARQUITETURA-GOOGLE-ADS.md`](ARQUITETURA-GOOGLE-ADS.md)
> Fonte do modelo de briefing de oferta e do playbook imobiliário: [`briefing-trilha`](https://github.com/beatriz-moraes082/briefing-trilha).

### Changelog
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
│ CONECTORES   Meta (MCP/API) · Google Ads API · CRM (Kommo) · │
│              WhatsApp · planilhas                            │
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

## 3. Camada 0 — Diagnóstico e estratégia

Roda no onboarding de todo cliente e é revisada a cada trimestre. Produz quatro saídas antes de qualquer campanha.

### 3.1 Calculadora de economia unitária (matemática reversa)

| Entrada | Exemplo |
|---|---|
| Ticket médio (ou LTV) | R$ 3.000 |
| Margem de contribuição | 40% |
| Taxa de fechamento (lead → venda) | 5% |
| Taxa de qualificação (lead → lead qualificado) | 30% |
| % da margem que aceita investir em aquisição | 50% |

Saídas derivadas:
- **CAC máximo** = ticket × margem × % investível
- **CPL máximo** = CAC máximo × taxa de fechamento
- **CPL qualificado máximo** = CAC máximo × (taxa de fechamento ÷ taxa de qualificação)
- **Verba mínima viável** = verba necessária para gerar volume estatisticamente útil (ver §9) dentro do CPL máximo
- **Ponto de equilíbrio** e metas por fase (aprendizado, otimização, escala)

Quando o cliente não sabe uma taxa, usa-se o padrão do playbook do segmento, marcado como **estimado** até haver dado próprio.

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

Reaproveitar o wizard do `briefing-trilha` (Streamlit, validação por etapa, avisos contextuais, publicação no ClickUp), acrescentando etapas de mídia. Uma reunião com o cliente gera de uma vez:

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

**Imobiliário (primeiro playbook)** — derivado do `briefing-trilha`:
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
   → captura de fbclid · gclid · UTMs (campos ocultos ou código na mensagem)
   → CRM (Kommo): lead + origem + campanha + criativo
   → mudança de status no funil
   → (a) painel interno: CPL, CPL qualificado, CAC e ROAS reais por campanha, ângulo e termo
   → (b) retorno às plataformas: Meta (API de Conversões) · Google (conversões offline / otimizadas)
```

### 7.2 Mapa de eventos de qualidade

Os status do funil Kommo (já previstos no briefing-trilha) viram eventos padronizados:

| Status Kommo | Evento padrão | Retorno à plataforma |
|---|---|---|
| Lead entrou | `lead` | sim (otimização inicial) |
| Interesse confirmado (pós pré-atendimento) | `lead_qualificado` | sim — **evento de otimização preferido** quando houver volume |
| Visita/reunião agendada | `agendamento` | sim |
| Venda | `venda` (+ valor) | sim — base para ROAS-alvo |
| Descartado / não cadastrou | `desqualificado` | uso interno (e sinal negativo onde suportado) |
| Reativado (respondeu nutrição) | `reativado` | uso interno |

### 7.3 Módulo WhatsApp

No Brasil, a conversão principal costuma ser a conversa, não o formulário.
- **Rastreamento:** anúncios de clique para WhatsApp; para tráfego de site, botão com mensagem pré-preenchida contendo um código curto da campanha/criativo, lido pelo Kommo e gravado no lead.
- **Atendimento:** fluxos do playbook (pré-atendimento, follow-up, nutrição) gerados a partir da mesma oferta usada nos anúncios — coerência garantida pela fonte única.
- **Velocidade de resposta:** o SLA do `marca.yaml` é monitorado; SLA estourado vira alerta, porque destrói a taxa de qualificação e contamina a leitura de desempenho dos anúncios.

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

## 9. Estatística e alertas

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

- **Simulação antes de escrever:** toda alteração mostra o "antes → depois" e o impacto estimado; aplicação só após aprovação.
- **Reversão:** toda escrita guarda o estado anterior para desfazer.
- **Proteção do algoritmo:** recomendações agrupadas em janelas (ex.: 1–2×/semana por campanha); bloqueio de alterações estruturais durante fase de aprendizado, salvo emergência.
- **Monitoramento das rotinas:** se uma tarefa agendada não rodar ou falhar, aviso imediato (falha silenciosa é o pior cenário).
- **Acessos:** o cliente é dono das contas; a agência entra como parceira. Checklist de entrada e de saída do cliente (remover acessos, entregar dados e relatórios).
- **Segredos:** `.env` fora do Git; `.env.example` só com os nomes.
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
| Registro de decisões | operação | contínuo | sugestão → decisão → resultado; base de calibração |

**Hierarquia de métricas por cliente** (definida no perfil): métrica de negócio (vendas, CAC) → métrica principal da plataforma (CPL qualificado, ROAS) → métricas de diagnóstico (CPM, CTR, retenção de vídeo). Relatórios nunca apresentam métrica de diagnóstico como resultado.

## 12. Estrutura do repositório

```
/
├── ARQUITETURA-NUCLEO.md
├── ARQUITETURA-META-ADS.md
├── ARQUITETURA-GOOGLE-ADS.md
├── core/
│   ├── estrategia/          # calculadora de economia unitária, nota de maturidade, plano 90 dias
│   ├── normalizacao/
│   ├── estatistica/         # maturação de conversões, contagens, MAD, encolhimento, testes
│   ├── motores/             # relatórios, anomalias, vencedores, consolidação, alocação
│   ├── historico/           # registro de alterações
│   ├── conversao/           # captura de IDs, mapa de eventos, retorno às plataformas
│   ├── copy/                # verificador de copy, taxonomia de ângulos
│   └── saidas/              # templates: alertas, relatórios, painel, relatório ao cliente
├── plataformas/
│   ├── meta/
│   └── google/
├── integracoes/
│   ├── kommo/               # leitura de status, eventos de qualidade
│   ├── whatsapp/
│   └── clickup/
├── onboarding/              # wizard (extensão do briefing-trilha) + templates
├── playbooks/
│   └── imobiliario/
├── clientes/
│   └── _exemplo/
│       ├── perfil.yaml
│       ├── marca.yaml
│       ├── ofertas/
│       ├── avatares.md
│       └── historico.md
├── logs/decisoes/
└── .env.example
```

## 13. Roadmap do núcleo

1. **Camada 0 + perfil em níveis + playbook imobiliário + `marca.yaml`/`ofertas/`** — é o que dá a flexibilidade.
2. **Extensão do wizard do briefing-trilha** com as etapas de mídia.
3. **Histórico de alterações + correção de atraso de atribuição** — antes de ligar qualquer alerta.
4. **Conversão real + mapa de eventos Kommo + módulo WhatsApp.**
5. **Verificador de copy + taxonomia de ângulos.**
6. **Motores estatísticos** (anomalias, vencedores, testes).
7. **Visão consolidada, alocação de verba e relatório ao cliente.**
8. **Novos playbooks de segmento.**
