# Integração Kommo

> Código: `trilha/integracoes/kommo.py` · `trilha/conversao/pipeline.py` · Testes: `tests/test_kommo.py`, `tests/test_pipeline.py`
> Núcleo: §7 (conversão real e qualidade de lead)

## 1. Antes de construir: o que já é nativo

Verificar na conta do cliente, porque o que for nativo não precisa de código:
- Integração do WhatsApp (API do WhatsApp Business) e gravação da origem da conversa.
- Integração com formulários instantâneos do Meta (leads entram direto no funil).
- Formulários de site do Kommo (capturam UTMs).
- Integrações de eventos com o Meta disponíveis no marketplace do Kommo.

O Trilha cobre o que costuma faltar: **mapa etapa → evento padronizado por cliente, retorno para Meta e Google com deduplicação, registro no banco e alertas**.

## 2. Fluxo

```
Kommo: lead muda de etapa
  → webhook (POST form-urlencoded) para https://<servico>/webhooks/kommo?token=<segredo>
  → trilha.integracoes.kommo.parse_webhook()      → mudanças de etapa (lead_id, pipeline_id, status_id)
  → trilha.conversao.pipeline.eventos_do_webhook()→ mapa do perfil.yaml → evento padrão
  → KommoClient.buscar_lead(lead_id)               → campos personalizados + contato (API v4)
  → extrair_dados_lead()                           → gclid, fbclid, ctwa_clid, lead_id do Meta, e-mail, telefone, valor
  → montar envios: Meta API de Conversões · Google conversão offline
  → enviar (modo simulação por padrão) e registrar em JSONL / fila_envios
```

O Kommo não assina os webhooks: a URL leva um token secreto (`KOMMO_WEBHOOK_TOKEN`) e o endpoint rejeita chamadas sem ele.

## 3. Configuração por cliente (`perfil.yaml`)

```yaml
crm:
  tipo: kommo
  subdominio: "imobiliaria-exemplo"     # https://<subdominio>.kommo.com
  mapa_eventos:                         # IDs mudam em cada conta — copiar do Kommo
    - { pipeline_id: 1111, status_id: 2222, evento: lead }
    - { pipeline_id: 1111, status_id: 3333, evento: lead_qualificado }
    - { pipeline_id: 1111, status_id: 4444, evento: agendamento }
    # 142 (venda ganha) → venda e 143 (perdida) → desqualificado já são padrão
  campos:                               # nome do campo personalizado no Kommo
    gclid: "gclid"
    gbraid: "gbraid"
    wbraid: "wbraid"
    fbclid: "fbclid"
    ctwa_clid: "ctwa_clid"
    meta_lead_id: "meta_lead_id"
    utm_source: "utm_source"
    utm_campaign: "utm_campaign"
    utm_content: "utm_content"          # recebe o nome do anúncio na taxonomia
    codigo_criativo: "codigo_criativo"  # código curto da mensagem do WhatsApp
    corretor: "corretor"
    motivo_perda: "motivo_perda"
```

## 4. Campos personalizados padrão (criar em todo cliente)

| Campo | Tipo | Preenchido por |
|---|---|---|
| `gclid`, `gbraid`, `wbraid` | texto | campo oculto da landing / GTM |
| `fbclid` | texto | campo oculto da landing / GTM |
| `ctwa_clid` | texto | integração do WhatsApp (anúncio de clique para WhatsApp) |
| `meta_lead_id` | texto | integração de formulário instantâneo |
| `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` | texto | landing |
| `codigo_criativo` | texto | Salesbot lendo o código da mensagem pré-preenchida |
| `origem` | lista | padronizada: meta, google, portal_zap, portal_vivareal, portal_olx, indicacao, organico, lista |
| `corretor` | usuário/lista | distribuição de leads |
| `motivo_perda` | lista | obrigatório ao mover para "perdido" — alimenta as objeções da oferta |

## 5. Regras de envio

- **Deduplicação:** `event_id = kommo-<lead_id>-<evento>`; o mesmo lead voltando à mesma etapa não gera evento novo na plataforma.
- **Sem identificador, sem envio para aquela plataforma:** sem `gclid`/`gbraid`/`wbraid` e sem e-mail/telefone, não há envio ao Google; para o Meta, é preciso ao menos um entre `ctwa_clid`, `meta_lead_id`, `fbc` ou dado de contato em hash.
- **Eventos de uso interno** (`desqualificado`, `reativado`) são registrados mas não enviados, salvo configuração explícita em `conversao.destinos`.
- **Atraso:** o Google aceita conversões offline dentro da janela da ação de conversão (normalmente até 90 dias após o clique); eventos mais antigos são registrados e não enviados.
- **Limite de requisições da API do Kommo:** as leituras de lead passam por uma fila com backoff; a documentação oficial do Kommo define o limite vigente.
- **Falha nunca é silenciosa:** envio com erro vai para `fila_envios` com nova tentativa; três falhas seguidas viram alerta operacional.

## 6. Funcionalidades extras sobre os dados do Kommo

| Funcionalidade | Para quê |
|---|---|
| Tempo até o primeiro contato por corretor | SLA real (marca.yaml) e alerta |
| Taxa de qualificação por corretor × por campanha | separa problema de atendimento de problema de mídia |
| Motivos de perda por oferta | alimentam `objecoes` da oferta e novos ângulos de criativo |
| Reativação de leads frios | listas para público personalizado (em hash) + fluxo de nutrição |
| Divergência plataforma × CRM | alerta quando leads na plataforma e no Kommo se descolam |

## 7. Testar localmente

```bash
python -m trilha simular-webhook tests/fixtures/kommo_webhook.txt \
  --perfil clientes/_exemplo/perfil.yaml \
  --lead tests/fixtures/kommo_lead.json
```

Mostra os eventos identificados e os payloads exatos que iriam para o Meta e o Google, sem enviar nada.
