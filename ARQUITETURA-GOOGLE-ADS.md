# Sistema de Automação Google Ads com Claude — Arquitetura v0.1

> Status: rascunho de arquitetura · 2026-10-02
> Referência inicial: masterclass "Claude Code + Google Ads" (Jono), com adaptações e correções próprias.
> Documento irmão: [`ARQUITETURA-META-ADS.md`](ARQUITETURA-META-ADS.md) — as duas plataformas compartilham núcleo, perfil do cliente, normalização e motores estatísticos.

---

## 1. Objetivo

Construir um sistema **agnóstico de cliente** para Google Ads (rede de pesquisa) que cubra o ciclo completo — pesquisa de palavras-chave, estrutura de campanhas, geração de anúncios, landing pages, rastreamento, otimização e retorno de conversões — adaptando-se a cada cliente a partir do **perfil fornecido no onboarding**.

Princípios (os mesmos do Meta, mais dois específicos):
- **Núcleo fixo, personalização por dados.**
- **Leitura livre, escrita com aprovação.** O Claude prepara as mudanças; nada é publicado sem confirmação.
- **Cálculo em código, nunca "de cabeça".**
- **Conversão real acima da métrica da plataforma.**
- **Volume real, nunca inventado.** Palavras-chave sempre validadas com dados do Planejador de Palavras-chave; o modelo não sabe volume de busca.
- **Coerência de intenção.** Busca → anúncio → landing page → atendimento falam a mesma coisa.
- **Filtro humano obrigatório** em toda decisão que envolva verba.

## 2. Decisão de implementação

Diferente do Meta, a referência não usa um conector pronto: o acesso é pela **API do Google Ads via Claude Code**.

| Função | Ferramenta | Por quê |
|---|---|---|
| Acesso à conta | Google Ads API (biblioteca oficial Python + GAQL) | Cobertura completa: leitura, criação, relatórios, termos de pesquisa |
| Pesquisa de palavras-chave | Planejador de Palavras-chave (via API ou exportação manual) | Volume, concorrência e lance estimado reais |
| Cálculos e estatística | Código no repositório (núcleo compartilhado) | Determinístico e versionado |
| Geração em massa | Skills (`/campanha`, `/anuncios`, `/negativas`, `/landing`) | Repetível sem reexplicar contexto |
| Landing pages | Next.js → GitHub → Vercel | Uma página por intenção, deploy simples |
| Consultas pontuais | Claude Code em conversa | Auditorias e diagnósticos rápidos |

Se surgir um conector MCP confiável para Google Ads, ele pode substituir a camada de acesso sem mudar o resto.

## 3. Configuração de acesso (uma vez por agência)

1. **Conta de administrador (MCC)** — vincular as contas dos clientes como subcontas. Uma MCC atende todos os clientes.
2. **Developer token** — na Central de API da MCC. O nível inicial tem limite de requisições; solicitar acesso ampliado quando a operação crescer.
3. **Projeto no Google Cloud** — ativar a Google Ads API.
4. **OAuth** — tela de consentimento + cliente do tipo "aplicativo para computador"; baixar `credentials.json`; autenticar uma vez e guardar o refresh token.
5. **Segredos** — `developer_token`, `login_customer_id` (MCC), `client_id`, `client_secret`, `refresh_token` em `.env`, **nunca no Git**. Repositório com `.env.example` apenas com os nomes.

## 4. Arquitetura em camadas

```
┌─────────────────────────────────────────────────────────┐
│ CONECTORES     Google Ads API · Keyword Planner · CRM   │
└──────────────────────────┬──────────────────────────────┘
                           │ dados brutos → normalização comum
┌──────────────────────────▼──────────────────────────────┐
│ CAMADA 1 — NÚCLEO (compartilhado com Meta)              │
│  + módulos Google: palavras-chave · estrutura · RSA ·   │
│    negativas · landing pages · rastreamento             │
└──────────────────────────┬──────────────────────────────┘
┌──────────────────────────▼──────────────────────────────┐
│ CAMADA 2 — PERFIL DO CLIENTE (mesmo perfil.yaml)        │
└──────────────────────────┬──────────────────────────────┘
┌──────────────────────────▼──────────────────────────────┐
│ CAMADA 3 — REGRAS DERIVADAS                             │
└─────────────────────────────────────────────────────────┘
```

### 4.1 Módulos específicos do Google

**M1 — Pesquisa e triagem de palavras-chave**
- Entrada: serviços e área geográfica do perfil.
- Puxa ideias do Planejador **restrito à região do cliente** (nunca o país inteiro por padrão).
- Classifica cada termo por intenção:
  - **Comercial/urgente** (ex.: "serviço + perto de mim", "serviço + cidade", "emergência", "24h") → manter.
  - **Informacional, vaga de emprego, curso, DIY, fornecedor/peça, concorrente** → descartar ou negativar.
- Saída: lista aprovada com volume, concorrência e lance estimado + lista de descartes.
- **Matriz serviço × local**: gera combinações e corta as que não têm volume mínimo (definido no perfil).

**M2 — Estrutura de campanhas**
- Campanha = serviço (ou linha de negócio), com orçamento, horários e localização próprios.
- **Grupos temáticos fechados (STAG)** como padrão: poucos termos muito próximos por grupo.
  - *Correção à referência:* SKAG puro (um termo por grupo) perdeu força porque as correspondências de frase/exata hoje incluem variações próximas, e os lances inteligentes precisam de volume por grupo. SKAG fica reservado a termos de alto volume e alto valor.
- Correspondência padrão: **frase** (+ exata nos termos-núcleo). Ampla apenas com lances inteligentes maduros e conversão real alimentando o algoritmo.
- **Configurações-padrão de proteção** (aplicadas a todo cliente, salvo exceção no perfil):
  - somente **rede de pesquisa** (sem parceiros de pesquisa, sem display na campanha de pesquisa);
  - segmentação geográfica por **presença**, não "presença ou interesse";
  - exclusão de países fora da área de atendimento;
  - **aplicação automática de recomendações desligada**;
  - sem segmentos de público restringindo a pesquisa fria (apenas observação).
- Lances: começar em **maximizar conversões**; migrar para **CPA-alvo / ROAS-alvo** quando houver volume e conversão real suficientes (limiar no perfil).

**M3 — Gerador de anúncios responsivos (RSA)**
- Até 15 títulos e 4 descrições por anúncio, gerados a partir de: termo do grupo + perfil + branding + avatares + oferta.
- **Título 1 fixado com o termo/intenção do grupo**; demais títulos (ofertas, diferenciais, prova) rodam livres.
- Extensões sempre completas: sitelinks, frases de destaque, snippets estruturados, chamada, local, nome e logo — ocupam mais espaço na página.
- *Correção à referência:* cada grupo aceita **no máximo 3 RSAs ativos**. "Testar centenas de anúncios" na prática significa testar variações de títulos, ofertas e landing pages ao longo do tempo, com volume suficiente.
- Validação automática antes de publicar: limites de caracteres, políticas, termos proibidos do perfil, coerência com a landing page.

**M4 — Negativas**
- **Lista universal por segmento** (empregos, cursos, DIY, grátis, definição, peças, suporte a clientes existentes…), compartilhada entre campanhas do cliente.
- **Varredura recorrente de termos de pesquisa**: o Claude classifica cada termo (geografia errada, intenção errada, concorrente, emprego…), propõe negativas com justificativa e só aplica após aprovação.
- Termos ambíguos são verificados pela intenção real (ex.: "contratação de X" pode ser vaga de emprego, não cliente).

**M5 — Landing pages**
- Uma página por intenção (grupo ou família de grupos), com título que repete a busca.
- Gerador em Next.js com template por cliente (cores e tipografia do `branding.md`); referência visual opcional.
- Checklist de conversão: formulário na primeira dobra, prova social (idealmente depoimentos em vídeo), vídeo do responsável, oferta clara, carregamento rápido.
- Deploy: GitHub → Vercel; depois do deploy, atualizar a URL final dos anúncios.
- Teste A/B de páginas como alavanca principal de conversão.

**M6 — Rastreamento e públicos**
- Tag do Google em todas as páginas; evento de conversão no envio do formulário e na ligação.
- Verificação automática da tag (Tag Assistant / teste de navegador).
- Público de visitantes do site para **RLSA** (remarketing na pesquisa) — lance maior para quem já conhece a marca. Display de remarketing apenas como teste.

### 4.2 Módulo de conversão real (compartilhado com Meta)

```
Busca → anúncio → landing → captura de gclid + UTMs (campos ocultos do formulário)
     → CRM (lead + campanha + termo + gclid) → status: qualificado / vendido / valor
     → (a) painel interno de ROAS/CPA real por campanha e termo
     → (b) importação de conversões offline no Google Ads (gclid + valor)
```

- Permite migrar para ROAS-alvo com valores reais, não um valor fixo por lead.
- Conversões otimizadas para leads podem complementar quando o gclid se perder.
- **Rotina de higiene**: ligação ao lead em até poucos minutos (velocidade de resposta) e registro de qualidade no CRM — sem isso, o retorno ao Google ensina o algoritmo errado.

### 4.3 Motores do núcleo aplicados ao Google

| Motor | Adaptação |
|---|---|
| Relatórios | Métricas adicionais: parcela de impressões, posição/topo, índice de qualidade e seus 3 componentes, CPC |
| Anomalias | Mesmo método (mediana/MAD, regras por volume) + alertas específicos: orçamento limitado, queda de parcela de impressões, reprovação de anúncio, tag sem disparar |
| Vencedores | Nível: termo de pesquisa e combinação título/página; encolhimento bayesiano igual ao Meta |
| Auditoria | Painel semanal: campanhas a pausar, a escalar, termos a negativar, índices de qualidade baixos e por quê |

## 5. Campos adicionais no perfil do cliente

```yaml
plataformas:
  google:
    customer_ids: []
    servicos:                 # base para a matriz serviço × local
      - nome: ""
        ticket_medio: null
    area_atendimento:
      tipo: ""                # cliente vai até você | você vai até o cliente
      centro: ""
      raio_km: null
      cidades: []
    horario_atendimento: ""   # define programação dos anúncios
    volume_minimo_termo: null # busca mensal mínima para entrar na matriz
    negativas_segmento: ""    # lista universal a usar
    concorrentes: []          # para negativar (ou não) conscientemente
    landing:
      dominio: ""
      template: ""
```

## 6. Estrutura no repositório

```
plataformas/google/
├── conector/          # cliente da API, consultas GAQL, autenticação
├── palavras_chave/    # M1: pesquisa, triagem, matriz serviço × local
├── estrutura/         # M2: criação de campanhas e grupos com padrões de proteção
├── anuncios/          # M3: geração e validação de RSA + extensões
├── negativas/         # M4: listas universais por segmento + varredura de termos
├── landing/           # M5: template Next.js por cliente
├── rastreamento/      # M6: tag, eventos, públicos
└── offline/           # importação de conversões offline
skills/
├── campanha/          # /campanha
├── anuncios/          # /anuncios
├── negativas/         # /negativas
└── landing/           # /landing
```

## 7. Roadmap

1. **Acesso** — MCC, developer token, projeto no Cloud, OAuth, `.env`.
2. **Leitura e relatórios** — normalização comum + relatório diário reaproveitando o núcleo.
3. **M4 Negativas** — lista universal + varredura de termos (maior economia imediata).
4. **M1 + M2** — pesquisa de palavras-chave e criação de campanhas com padrões de proteção.
5. **M3** — gerador de RSA com validação.
6. **M6 + conversão real** — tag, eventos, gclid no CRM, importação offline.
7. **M5** — gerador de landing pages e testes A/B.
8. **Auditoria e anomalias** específicas do Google.
9. **Skills** para cada fluxo repetível.

## 8. Riscos e limitações

- Developer token com acesso inicial limitado; aprovação de nível superior leva tempo.
- Volume de busca baixo (cidades pequenas, nichos) inviabiliza SKAG e testes rápidos — o perfil precisa refletir isso.
- Publicação direta na conta é o maior risco: toda escrita passa por aprovação e fica registrada.
- Landing pages geradas em massa precisam de revisão de conteúdo, promessas e compliance do segmento.
- Sem conversão real, lances inteligentes otimizam para formulários, inclusive spam e leads ruins.
- Opiniões fortes da referência (ex.: "PMax e display são sempre lixo") são tratadas como **hipóteses a testar por cliente**, não como regra.

## 9. Próximos passos

- [ ] Revisar este documento.
- [ ] Configurar o acesso à API numa conta de teste.
- [ ] Montar as listas universais de negativas por segmento.
- [ ] Definir o esquema de normalização comum com o Meta.
