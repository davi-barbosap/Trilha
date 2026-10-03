# Sistema de Automação Google Ads com Claude — Arquitetura v0.3

> Status: rascunho de arquitetura · 2026-10-02
> **Leia primeiro:** [`ARQUITETURA-NUCLEO.md`](ARQUITETURA-NUCLEO.md) — estratégia, onboarding, perfil, brand kit, playbooks, conversão real, estatística e governança são compartilhados e não se repetem aqui.
> Documento irmão: [`ARQUITETURA-META-ADS.md`](ARQUITETURA-META-ADS.md)
> Referência inicial: masterclass "Claude Code + Google Ads" (Jono), com adaptações e correções próprias.

### Changelog
- **v0.3** — Conteúdo comum movido para o núcleo. Novos: landing pages em três níveis, Perfil da Empresa no Google, anúncios de chamada e formulário de lead, integração com brand kit (verificador de copy, ofertas, regras comerciais), destino WhatsApp com rastreamento, negativas vindas do playbook do segmento, auditoria de onboarding.
- **v0.2** — (sem versão própria; numeração alinhada ao núcleo e ao Meta)
- **v0.1** — Acesso via API, seis módulos, conversões offline, correções à referência.

---

## 1. Papel do Google no sistema

O Google **captura demanda**: atende quem já está procurando. O fator decisivo é a **coerência de intenção** — busca → anúncio → página → atendimento falando a mesma coisa — e a disciplina de não pagar por buscas que nunca viram cliente. Volume é limitado pela demanda existente; por isso a Camada 0 (núcleo §3) precisa estimar o teto de volume antes de prometer resultado.

## 2. Implementação

| Função | Ferramenta |
|---|---|
| Acesso à conta | Google Ads API (biblioteca oficial Python + GAQL) via Claude Code |
| Pesquisa de palavras-chave | Planejador de Palavras-chave (API ou exportação) |
| Cálculos | núcleo |
| Geração em massa | skills (`/campanha`, `/anuncios`, `/negativas`, `/landing`) |
| Landing pages | três níveis (§4.5) |

Se surgir um conector MCP confiável para Google Ads, ele substitui só a camada de acesso.

### 2.1 Configuração de acesso (uma vez por agência)

1. **Conta de administrador (MCC)** com as contas dos clientes vinculadas — o cliente continua dono da conta.
2. **Developer token** na Central de API (nível inicial limitado; pedir ampliação quando crescer).
3. **Projeto no Google Cloud** com a Google Ads API ativada.
4. **OAuth** (cliente "aplicativo para computador"), autenticação única, refresh token guardado.
5. **Segredos** em `.env` (`developer_token`, `login_customer_id`, `client_id`, `client_secret`, `refresh_token`); `.env.example` só com nomes.

## 3. Auditoria de onboarding (Google)

- [ ] Conta vinculada à MCC; histórico e acessos
- [ ] Ações de conversão: quais existem, qual é primária, se contam formulários/ligações/WhatsApp/offline
- [ ] Tag do Google e conversões otimizadas ativas
- [ ] Configurações de risco: parceiros de pesquisa, rede de display em campanha de pesquisa, localização por "interesse", recomendações automáticas aplicadas
- [ ] Termos de pesquisa dos últimos 90 dias: % do gasto em termos irrelevantes (estimativa de desperdício)
- [ ] Índice de qualidade por palavra-chave e seus três componentes
- [ ] Estrutura: fragmentação, grupos sem anúncio ou com 1 título, extensões faltando
- [ ] Perfil da Empresa no Google vinculado (negócios locais)
- [ ] Coerência anúncio → página (amostra)

## 4. Módulos

### M1 — Pesquisa e triagem de palavras-chave

- Entrada: ofertas (`ofertas/`), área de atendimento e serviços (`perfil.yaml`), negativas do playbook.
- Ideias do Planejador **restritas à região do cliente**; volume, concorrência e lance estimado reais — o modelo não inventa volume.
- Classificação por intenção:
  - **Comercial / urgente** (serviço + cidade/bairro, "perto de mim", "emergência", "24h", nome da oferta) → manter.
  - **Informacional, emprego, curso, DIY, peça/fornecedor, concorrente** → descartar ou negativar.
- **Matriz oferta/serviço × local**, cortando combinações abaixo do volume mínimo do perfil.
- Termos ambíguos verificados pela intenção real da busca antes de entrar.
- **Estimativa de teto de demanda**: soma de volume × CTR esperado × taxa de conversão → alimenta a Camada 0 (o Google sozinho comporta a meta?).

### M2 — Estrutura de campanhas

- Campanha = oferta ou linha de serviço, com orçamento, horário (do `marca.yaml`) e localização próprios.
- **Grupos temáticos fechados (STAG)** como padrão; SKAG apenas para termos de alto volume e alto valor.
- Correspondência: **frase** + **exata** nos termos-núcleo; ampla só com lances inteligentes maduros alimentados por conversão real.
- **Padrões de proteção** (salvo exceção no perfil):
  - somente rede de pesquisa; sem parceiros de pesquisa;
  - localização por **presença**;
  - exclusão de países/regiões fora da área de atendimento;
  - recomendações automáticas **desligadas**;
  - públicos apenas em observação na pesquisa fria.
- **Lances** seguindo a escada de evento do núcleo: maximizar conversões (lead) → CPA-alvo (lead qualificado) → ROAS-alvo (venda com valor), cada degrau liberado por volume mínimo.
- Formatos opcionais, decididos pela Camada 0: PMax e display tratados como **hipóteses a testar**, nunca padrão; remarketing na pesquisa (RLSA) como primeiro teste de público quente.

### M3 — Anúncios responsivos (RSA) e extensões

- Até 15 títulos e 4 descrições por anúncio, gerados de: termo do grupo + oferta (diferenciais concretos, condições, objeções) + voz da marca + avatares.
- **Título 1 fixado com a intenção do grupo**; os demais (ofertas, prova, diferenciais, resposta a objeções) rodam livres.
- Máximo de **3 RSAs ativos por grupo** — o teste real é de títulos, ofertas e páginas ao longo do tempo.
- **Verificador de copy do núcleo (§5.3)** antes da revisão humana: concretude, termos e promessas proibidas, regra de preço do canal "anúncio", registro profissional, limites de caracteres e políticas.
- Extensões completas: sitelinks, frases de destaque, snippets estruturados, imagem (somente com assets reais e de qualidade), nome e logo da marca, local.
- **Recursos adicionais por maturidade:**
  - **Chamada** (anúncio/extensão de ligação) — serviços urgentes; com horário de atendimento.
  - **Formulário de lead** — baixo atrito; qualificação obrigatória via perguntas e retorno de status.
  - **WhatsApp como destino** — via landing com botão rastreado (código na mensagem, núcleo §7.3).

### M4 — Negativas

- **Lista universal do segmento** vinda de `playbooks/<segmento>/negativas.md` + específicas do cliente, compartilhada entre campanhas.
- **Varredura recorrente de termos de pesquisa**: classificação (geografia errada, intenção errada, emprego, concorrente…), justificativa, impacto em R$, aplicação só após aprovação.
- Termos ambíguos checados pela intenção real (ex.: "contratação de X" pode ser vaga de emprego).

### M5 — Landing pages em três níveis

| Nível | Quando | Como |
|---|---|---|
| **1. Site atual + inserção dinâmica** | maturidade baixa, verba pequena, site razoável | parâmetros na URL ajustam título/subtítulo à busca; nenhum site novo |
| **2. Template parametrizado** | padrão para a maioria | uma página por oferta com blocos trocados por intenção; identidade do `marca.yaml`, conteúdo do `ofertas/` |
| **3. Página dedicada** | termos de maior valor/volume | Next.js → GitHub → Vercel, título repetindo a busca |

Em todos os níveis:
- Formulário ou botão de WhatsApp visível sem rolar.
- Prova social do `marca.yaml` (preferência por depoimentos em vídeo), vídeo do responsável quando a assinatura inclui pessoa.
- Diferenciais e respostas a objeções vindos da oferta — **a mesma fonte dos anúncios e dos fluxos de WhatsApp**.
- Aviso de privacidade e base legal (LGPD).
- Captura de gclid + UTMs em campos ocultos.
- Teste A/B de páginas seguindo o protocolo de testes do núcleo.

### M6 — Rastreamento e públicos

- Tag do Google em todas as páginas; conversões: formulário, ligação, clique no WhatsApp, e **eventos de qualidade do Kommo** como conversões offline (núcleo §7.2).
- Conversões otimizadas para leads (dados com hash) como complemento quando o gclid se perde.
- Verificação automática da tag após cada publicação de página.
- Público de visitantes para RLSA; display de remarketing apenas como teste.

### M7 — Negócio local

- **Perfil da Empresa no Google**: vinculado, com horário, categorias, fotos reais e avaliações monitoradas — afeta extensões de local e confiança.
- Para serviços elegíveis, avaliar formatos de anúncio de serviços locais conforme disponibilidade na região.

## 5. Monitoramento específico do Google

Somam-se aos motores do núcleo:

| Alerta | Gatilho |
|---|---|
| Orçamento limitado com CPA abaixo da meta | oportunidade de escala |
| Queda de parcela de impressões (classificação ou orçamento) | estatística do núcleo |
| Índice de qualidade caiu | por palavra-chave relevante |
| Termo novo com gasto relevante sem conversão | candidato a negativa |
| Reprovação de anúncio ou de recurso | sempre |
| Conversão / tag sem disparar após publicação | sempre |
| Divergência Google × CRM | conversões na plataforma muito diferentes dos leads no Kommo |

## 6. Campos do Google no perfil do cliente

```yaml
plataformas:
  google:
    customer_ids: []
    area_atendimento:
      tipo: ""                # cliente vai até você | você vai até o cliente
      centro: ""
      raio_km: null
      cidades: []
      excluir: []
    volume_minimo_termo: null # busca mensal mínima para entrar na matriz
    concorrentes: []          # decisão consciente: negativar ou disputar
    landing:
      nivel_padrao: 2         # 1 | 2 | 3
      dominio: ""
    recursos: { chamada: false, formulario_lead: false, whatsapp: true }
    perfil_empresa_id: ""
```

Serviços, ofertas, horário e regras comerciais vêm de `ofertas/` e `marca.yaml` — sem duplicar.

## 7. Estrutura no repositório

```
plataformas/google/
├── conector/          # API, GAQL, autenticação, normalização
├── auditoria/         # checklist de onboarding, estimativa de desperdício
├── palavras_chave/    # M1
├── estrutura/         # M2
├── anuncios/          # M3 (usa core/copy)
├── negativas/         # M4 (usa playbooks/<segmento>/negativas.md)
├── landing/           # M5: inserção dinâmica, template, Next.js
├── rastreamento/      # M6
└── local/             # M7
skills/
├── campanha/  ├── anuncios/  ├── negativas/  └── landing/
```

## 8. Roadmap Google

1. Acesso à API + auditoria de onboarding (com estimativa de desperdício).
2. Relatório diário e alertas operacionais (usando o núcleo).
3. M4 Negativas — maior economia imediata.
4. M6 + eventos de qualidade do Kommo como conversões offline.
5. M1 + M2 com padrões de proteção.
6. M3 com verificador de copy.
7. M5 começando pelo nível 2 (template parametrizado).
8. M7 e auditoria semanal.

## 9. Riscos específicos

- Developer token com acesso inicial limitado; aprovação superior leva tempo.
- Demanda baixa (cidades pequenas, nichos) limita volume e testes — a Camada 0 precisa dizer isso ao cliente antes.
- Publicação direta na conta é o maior risco: simulação, aprovação e registro sempre.
- Páginas geradas em massa exigem revisão de promessas e compliance do segmento.
- Sem conversão real, lances inteligentes otimizam para formulário, inclusive spam.
- Opiniões fortes da referência (PMax, display) são hipóteses por cliente, não regra.
