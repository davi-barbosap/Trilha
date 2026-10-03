# Sistema de Automação Meta Ads com Claude — Rascunho Técnico v0.1

> Status: rascunho de arquitetura (2026-10-02). Ponto de partida para iterações futuras.
> Referência inicial: "Claude + Facebook Ads (FULL COURSE)" — Sam Piliero / The Moonlighters, com adaptações e melhorias próprias.

## 1. Objetivo

Construir um sistema **agnóstico de cliente**: um núcleo único de automação para Meta Ads que se adapta a qualquer cliente e branding a partir de um **perfil fornecido no onboarding**. Nenhuma regra, meta ou número de cliente é codificado no núcleo.

Princípios:
- **Núcleo fixo, personalização por dados.** O núcleo consulta o perfil; nunca o contrário.
- **Leitura livre, escrita com aprovação.** Nenhuma alteração em orçamento, anúncio ou campanha sem confirmação humana.
- **Estatística proporcional ao volume.** Limiares e janelas são derivados do volume de conversões de cada conta.
- **Filtro humano obrigatório** em toda decisão que envolva verba.

## 2. Arquitetura em três camadas

```
┌─────────────────────────────────────────────────────────┐
│ CAMADA 1 — NÚCLEO (igual para todos)                    │
│  conexão · permissões · motores · padrões de saída      │
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

### 2.1 Camada 1 — Núcleo

**Conexão**
- MCP oficial da Meta como conector personalizado (URL indicada na referência: `https://mcp.facebookads.com/ads`; disponibilidade em liberação gradual — validar por conta).
- Prompt de verificação inicial: listar contas acessíveis e quais estão habilitadas para MCP.

**Permissões**
| Tipo de ferramenta | Política |
|---|---|
| Insights / leitura de entidades | Sempre permitir |
| Edição de orçamento, campanha, conjunto, anúncio | Sempre exigir aprovação |
| Criação/publicação | Sempre exigir aprovação |

**Motores**
1. **Relatórios**
   - Pontual (perguntas ad hoc).
   - Histórico (agregação semanal, N semanas, com seção de padrões).
   - Mês corrente (MTD) com metas do perfil, publicado como artifact com dados ao vivo.
2. **Detector de anomalias** — conta e campanha; boas e más; métricas primárias (gasto, métrica principal) e secundárias (CPM, CTR, frequência, entrega).
3. **Detector de vencedores / potenciais** — nível de anúncio.
4. **Recomendação criativa** — top N anúncios por gasto, com link para o Gerenciador e prévia do criativo.
5. **Geração de briefings e roteiros** — a partir de vencedores/potenciais + skills de branding e avatares.
6. **(Futuro)** Geração de imagem/vídeo via MCPs externos.

**Padrões de saída** (comuns a todos os clientes)
- Alerta: `[severidade] conta · nível · métrica · valor atual vs. linha de base · janela · ação sugerida`.
- Relatório diário: resumo executivo → métrica principal vs. meta → anomalias → vencedores → recomendações.
- Painel MTD: mesmo layout para todos os clientes.

### 2.2 Camada 2 — Perfil do cliente

Arquivo por cliente (ex.: `clientes/<slug>/perfil.yaml`) + documentos de contexto.

```yaml
cliente:
  nome: ""
  slug: ""
  segmento: ""                # e-commerce, imobiliário, educação, serviço local...
  ciclo_de_venda: ""          # imediato | curto | longo
contas:
  - ad_account_id: ""
metrica_principal:
  tipo: ""                    # ROAS | CPA | CPL | CPL_QUALIFICADO
  alvo: null
  teto: null
conversao_real:
  fonte: ""                   # pixel | CRM | planilha | nenhuma
  referencia: ""              # link/ID da fonte
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
- `historico.md` — aprendizados da conta (o que funcionou e o que não funcionou).

### 2.3 Camada 3 — Regras derivadas

**Janelas e frequência de alerta por volume**
| Conversões/dia | Janelas de análise | Frequência de anomalias | Gasto mínimo p/ alertar |
|---|---|---|---|
| ≥ 100 | 1, 3, 7 dias | até 4×/dia | baixo |
| 20–100 | 3, 7, 14 dias | 1–2×/dia | moderado |
| < 20 | 7, 14 dias | 1×/dia | alto + mín. de conversões |

*(Faixas iniciais — calibrar com o registro de decisões.)*

**Detecção de anomalias — método robusto**
- Linha de base: **mediana** da janela, excluindo períodos sazonais marcados no perfil.
- Dispersão: **MAD** (desvio absoluto mediano) em vez de desvio-padrão.
- Escore: `z_robusto = (x − mediana) / (1,4826 × MAD)`; alertar se `|z| > 3` (ajustável).
- Alertas de entrega independentes de estatística: gasto zerado, conjunto parado, anúncio reprovado, orçamento esgotado antes do horário.

**Detector de vencedores — com encolhimento bayesiano**
- Categorias (referência):
  - **Vencedor:** > 5% do gasto da campanha **e** métrica principal dentro da meta.
  - **Potencial:** só uma das duas condições.
  - Vencedor → replicar; potencial → ajustar.
- Melhoria: estimar a eficiência de cada anúncio com **encolhimento em direção à média da conta/campanha**, para não premiar anúncios com poucas conversões.
  - Taxa de conversão: Beta-Binomial (prior a partir da conta).
  - Contagem de conversões por gasto: Gamma-Poisson.
  - Classificar por probabilidade posterior de bater a meta, ex.: `P(CPA < alvo) > 0,8`.
- Avaliar em 3, 7 e 14 dias; destacar **vencedores persistentes** (presentes em todas as janelas).

## 3. Implementação no Claude

| Peça | Forma | Observação |
|---|---|---|
| Núcleo | Skill `meta-ads-core` | Motores, padrões de saída, regras derivadas |
| Perfil do cliente | Pasta `clientes/<slug>/` (ou skill por cliente) | perfil.yaml + branding + avatares |
| Onboarding | Questionário que gera o pacote | Cliente novo entra em minutos |
| Rotinas | Tarefas agendadas por cliente | Todas apontam para o mesmo núcleo |
| Painéis | Artifacts com dados ao vivo | Layout padronizado |
| Registro de decisões | Log por cliente | Sugestão → decisão → resultado |

## 4. Estrutura proposta do repositório

```
/
├── ARQUITETURA.md            # este documento
├── core/
│   ├── SKILL.md              # skill do núcleo
│   ├── motores/
│   │   ├── relatorios.md
│   │   ├── anomalias.md
│   │   ├── vencedores.md
│   │   └── criativos.md
│   ├── estatistica/          # funções de linha de base, MAD, encolhimento
│   └── saidas/               # templates de alerta, relatório e painel
├── onboarding/
│   ├── questionario.md
│   └── template_perfil.yaml
├── clientes/
│   └── _exemplo/
│       ├── perfil.yaml
│       ├── branding.md
│       ├── avatares.md
│       └── historico.md
└── logs/
    └── decisoes/
```

## 5. Roadmap

1. **Fundação** — validar acesso ao MCP por conta; definir permissões.
2. **Modelo de perfil + questionário de onboarding.**
3. **Relatório diário + alertas de entrega.**
4. **Detector de anomalias robusto** (mediana/MAD, regras por volume).
5. **Detector de vencedores** com encolhimento bayesiano.
6. **Skills de contexto** (branding, avatares) e motor de briefings.
7. **Volante criativo** com MCPs de geração de imagem/vídeo.
8. **Registro de decisões e calibração** dos limiares.

## 6. Riscos e limitações

- Acesso ao MCP da Meta ainda em liberação gradual.
- Sem fonte de conversão real (CRM/planilha), o sistema otimiza a métrica da plataforma, não o resultado do negócio.
- Excesso de criativos gerados por IA incha a conta e dilui verba.
- Tarefas agendadas dependem do ambiente em que rodam; validar a confiabilidade antes de depender delas.
- Toda decisão de verba passa por aprovação humana.

## 7. Próximos passos

- [ ] Revisar e ajustar este rascunho.
- [ ] Fechar o `template_perfil.yaml` e o questionário de onboarding.
- [ ] Testar o conector da Meta numa conta.
