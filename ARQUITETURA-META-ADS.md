# Sistema de Automação Meta Ads com Claude — Arquitetura v0.2

> Status: rascunho de arquitetura · atualizado em 2026-10-02
> Referência inicial: "Claude + Facebook Ads (FULL COURSE)" — Sam Piliero / The Moonlighters, com adaptações e melhorias próprias.
> Documento irmão: [`ARQUITETURA-GOOGLE-ADS.md`](ARQUITETURA-GOOGLE-ADS.md) — as duas plataformas compartilham núcleo, perfil do cliente e motores estatísticos.

### Changelog
- **v0.2** — Decisão de implementação híbrida (MCP para acesso + código para lógica); camada de conectores separada; módulo de conversão real (CRM → API de Conversões); núcleo compartilhado com o Google Ads; estrutura de repositório com código.
- **v0.1** — Arquitetura em três camadas, perfil do cliente, regras derivadas, roadmap.

---

## 1. Objetivo

Construir um sistema **agnóstico de cliente**: um núcleo único de automação para Meta Ads que se adapta a qualquer cliente e branding a partir de um **perfil fornecido no onboarding**. Nenhuma regra, meta ou número de cliente é codificado no núcleo.

Princípios:
- **Núcleo fixo, personalização por dados.** O núcleo consulta o perfil; nunca o contrário.
- **Leitura livre, escrita com aprovação.** Nenhuma alteração em orçamento, anúncio ou campanha sem confirmação humana.
- **Cálculo em código, nunca "de cabeça".** Toda métrica, linha de base e teste estatístico roda em Python/R; o modelo interpreta e recomenda.
- **Estatística proporcional ao volume.** Limiares e janelas derivados do volume de conversões de cada conta.
- **Conversão real acima da métrica da plataforma.** Sempre que houver fonte (CRM, planilha), ela manda.
- **Filtro humano obrigatório** em toda decisão que envolva verba.

## 2. Decisão de implementação: híbrida

| Função | Ferramenta | Por quê |
|---|---|---|
| Acesso aos dados da Meta | MCP oficial da Meta (via Claude Code ou chat) | Login simples, mantido pela Meta |
| Acesso a dados fora do MCP | Marketing API (Graph API) via scripts | Cobertura completa quando o MCP for limitado |
| Cálculos e estatística | Código no repositório (Python/R) | Determinístico, testável, versionado, econômico em tokens |
| Contexto do cliente e fluxos | Skills + arquivos de perfil | Reaproveitável para qualquer cliente |
| Consultas pontuais do dia a dia | Chat com o conector | Rápido para "por que o CPL subiu ontem?" |
| Rotinas recorrentes | Tarefas agendadas apontando para os scripts | Mesmo núcleo para todos os clientes |

Regra prática: **o MCP traz o dado, o código calcula, o Claude interpreta, você aprova.** Dados volumosos são processados no script e só o resumo chega ao modelo.

## 3. Arquitetura em camadas

```
┌─────────────────────────────────────────────────────────┐
│ CONECTORES          Meta MCP · Marketing API · CRM      │
└──────────────────────────┬──────────────────────────────┘
                           │ dados brutos
┌──────────────────────────▼──────────────────────────────┐
│ CAMADA 1 — NÚCLEO (compartilhado entre plataformas)     │
│  normalização · motores · estatística · saídas · logs   │
└──────────────────────────┬──────────────────────────────┘
                           │ consulta
┌──────────────────────────▼──────────────────────────────┐
│ CAMADA 2 — PERFIL DO CLIENTE (pacote por cliente)       │
│  negócio · métrica · metas · branding · avatares · ...  │
└──────────────────────────┬──────────────────────────────┘
                           │ deriva
┌──────────────────────────▼──────────────────────────────┐
│ CAMADA 3 — REGRAS DERIVADAS (calibração automática)     │
│  janelas · limiares · definição de vencedor · alertas   │
└─────────────────────────────────────────────────────────┘
```

### 3.0 Conectores

**Meta MCP**
- Conector personalizado (URL indicada na referência: `https://mcp.facebookads.com/ads`; liberação gradual — validar por conta).
- Verificação inicial: listar contas acessíveis e quais estão habilitadas para MCP.

**Permissões**
| Tipo de ferramenta | Política |
|---|---|
| Insights / leitura de entidades | Sempre permitir |
| Edição de orçamento, campanha, conjunto, anúncio | Sempre exigir aprovação |
| Criação/publicação | Sempre exigir aprovação |

**Normalização.** Todo dado (Meta ou Google) é convertido para um esquema comum antes de chegar aos motores:
`data · plataforma · conta · campanha · conjunto/grupo · anúncio · gasto · impressões · cliques · conversões · valor · campos de nomenclatura`.
Isso permite usar os mesmos motores nas duas plataformas.

### 3.1 Camada 1 — Núcleo

**Motores**
1. **Relatórios** — pontual; histórico semanal com seção de padrões; mês corrente (MTD) com metas do perfil, publicado como artifact.
2. **Detector de anomalias** — conta e campanha; boas e más; métricas primárias (gasto, métrica principal) e secundárias (CPM, CTR, frequência, entrega).
3. **Detector de vencedores / potenciais** — nível de anúncio.
4. **Recomendação criativa** — top N anúncios por gasto, com link para o Gerenciador e prévia do criativo.
5. **Briefings e roteiros** — a partir de vencedores/potenciais + skills de branding e avatares.
6. **Conversão real** — ver §3.4.
7. **(Futuro)** Geração de imagem/vídeo via MCPs externos.

**Padrões de saída** (comuns a todos os clientes e às duas plataformas)
- Alerta: `[severidade] plataforma · conta · nível · métrica · valor atual vs. linha de base · janela · ação sugerida`.
- Relatório diário: resumo executivo → métrica principal vs. meta → anomalias → vencedores → recomendações.
- Painel MTD: mesmo layout para todos os clientes.

**Registro de decisões** — toda recomendação gera uma linha: `data · cliente · recomendação · evidência · decisão (aprovada/recusada) · resultado após N dias`. Base para calibrar limiares.

### 3.2 Camada 2 — Perfil do cliente

Arquivo por cliente em `clientes/<slug>/perfil.yaml` (compartilhado com o Google Ads) + documentos de contexto.

```yaml
cliente:
  nome: ""
  slug: ""
  segmento: ""                # e-commerce, imobiliário, educação, serviço local...
  ciclo_de_venda: ""          # imediato | curto | longo
plataformas:
  meta:
    ad_account_ids: []
    pixel_id: ""
  google:                     # ver ARQUITETURA-GOOGLE-ADS.md
    customer_ids: []
metrica_principal:
  tipo: ""                    # ROAS | CPA | CPL | CPL_QUALIFICADO
  alvo: null
  teto: null
conversao_real:
  fonte: ""                   # pixel | CRM | planilha | nenhuma
  referencia: ""
  retorno_para_plataforma: false   # enviar vendas/leads qualificados via API de Conversões
volume:
  conversoes_dia_tipicas: null
  gasto_diario_tipico: null
sazonalidade:
  periodos:
    - nome: ""
      inicio: ""
      fim: ""
      tratamento: ""          # excluir_da_base | meta_propria
nomenclatura:
  padrao_campanha: ""         # ex.: {produto}_{funil}_{publico}
  campos: []
restricoes:
  categoria_especial: null
  compliance: []
  promessas_proibidas: []
entrega:
  canal: ""                   # chat | e-mail | Slack | WhatsApp
  horarios: []
  fuso: "America/Maceio"
```

Documentos de contexto:
- `branding.md` — tom de voz, paleta, tipografia, termos obrigatórios e proibidos, exemplos aprovados.
- `avatares.md` — clusters de público: dores, objeções, gatilhos, linguagem real, ângulos de solução.
- `historico.md` — aprendizados da conta.

### 3.3 Camada 3 — Regras derivadas

**Janelas e frequência de alerta por volume**
| Conversões/dia | Janelas de análise | Frequência de anomalias | Gasto mínimo p/ alertar |
|---|---|---|---|
| ≥ 100 | 1, 3, 7 dias | até 4×/dia | baixo |
| 20–100 | 3, 7, 14 dias | 1–2×/dia | moderado |
| < 20 | 7, 14 dias | 1×/dia | alto + mín. de conversões |

*(Faixas iniciais — calibrar com o registro de decisões.)*

**Detecção de anomalias — método robusto**
- Linha de base: **mediana** da janela, excluindo períodos sazonais do perfil.
- Dispersão: **MAD** em vez de desvio-padrão.
- Escore: `z_robusto = (x − mediana) / (1,4826 × MAD)`; alertar se `|z| > 3` (ajustável).
- Alertas de entrega independentes de estatística: gasto zerado, conjunto parado, anúncio reprovado, orçamento esgotado antes do horário.

**Detector de vencedores — com encolhimento bayesiano**
- Categorias (referência):
  - **Vencedor:** > 5% do gasto da campanha **e** métrica principal dentro da meta → replicar.
  - **Potencial:** só uma das duas condições → ajustar.
- Eficiência estimada com **encolhimento em direção à média da conta/campanha**:
  - taxa de conversão: Beta-Binomial (prior a partir da conta);
  - conversões por gasto: Gamma-Poisson.
- Classificação por probabilidade posterior, ex.: `P(CPA < alvo) > 0,8`.
- Janelas de 3, 7 e 14 dias; destaque para **vencedores persistentes**.

### 3.4 Módulo de conversão real

Sem ele, o sistema otimiza o que a Meta vê (cliques, leads de formulário), não o resultado do negócio.

```
Anúncio → landing/formulário → captura de fbclid + UTMs (campos ocultos)
       → CRM (lead + origem) → status: qualificado / vendido / valor
       → (a) painel interno de ROAS/CPL real
       → (b) retorno à Meta via API de Conversões (eventos de lead qualificado / compra)
```

- O motor de vencedores passa a usar a conversão real quando disponível.
- O retorno à plataforma ensina o algoritmo a buscar leads parecidos com os que viram venda.
- Para leads de formulário instantâneo, a qualificação também pode ser reportada de volta.

## 4. Estrutura do repositório

```
/
├── ARQUITETURA-META-ADS.md
├── ARQUITETURA-GOOGLE-ADS.md
├── core/                       # compartilhado entre plataformas
│   ├── SKILL.md
│   ├── normalizacao/           # esquema comum de dados
│   ├── estatistica/            # mediana/MAD, encolhimento bayesiano
│   ├── motores/                # relatórios, anomalias, vencedores
│   └── saidas/                 # templates de alerta, relatório, painel
├── plataformas/
│   ├── meta/
│   │   ├── conector/           # chamadas MCP / Marketing API
│   │   ├── criativos/          # recomendação, briefings, roteiros
│   │   └── capi/               # retorno de conversões
│   └── google/                 # ver ARQUITETURA-GOOGLE-ADS.md
├── onboarding/
│   ├── questionario.md
│   └── template_perfil.yaml
├── clientes/
│   └── _exemplo/
│       ├── perfil.yaml
│       ├── branding.md
│       ├── avatares.md
│       └── historico.md
├── logs/decisoes/
└── .env.example                # nomes das variáveis; segredos nunca no Git
```

## 5. Roadmap

1. **Fundação** — validar acesso ao MCP por conta; definir permissões; esquema de normalização.
2. **Perfil do cliente + questionário de onboarding** (compartilhado com Google).
3. **Relatório diário + alertas de entrega.**
4. **Detector de anomalias robusto** (mediana/MAD, regras por volume).
5. **Detector de vencedores** com encolhimento bayesiano.
6. **Módulo de conversão real** (captura → CRM → API de Conversões).
7. **Skills de contexto** (branding, avatares) e motor de briefings.
8. **Volante criativo** com MCPs de geração de imagem/vídeo.
9. **Registro de decisões e calibração** dos limiares.

## 6. Riscos e limitações

- Acesso ao MCP da Meta em liberação gradual.
- Sem fonte de conversão real, o sistema otimiza a métrica da plataforma, não o resultado do negócio.
- Excesso de criativos gerados por IA incha a conta e dilui verba.
- Segredos (tokens, IDs) ficam fora do repositório (`.env`).
- Tarefas agendadas dependem do ambiente em que rodam; validar confiabilidade antes de depender delas.
- Toda decisão de verba passa por aprovação humana.

## 7. Próximos passos

- [ ] Revisar este documento.
- [ ] Fechar `template_perfil.yaml` e o questionário de onboarding.
- [ ] Definir o esquema de normalização comum (Meta + Google).
- [ ] Testar o conector da Meta numa conta.
