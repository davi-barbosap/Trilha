# n8n — orquestração da operação

> Decisão: [ADR-007](../decisoes/007-n8n-orquestrador.md) · Quem faz o quê: [MODELO-OPERACIONAL.md](../../MODELO-OPERACIONAL.md)
> Infra: [`infra/`](../../infra/) · Fluxos exportados: [`n8n/fluxos/`](../../n8n/fluxos/) · Núcleo chamado pelos fluxos: `trilha/api.py`

## 1. Arquitetura

```
                 ┌──────────────────────────── n8n (modo fila: principal + worker) ───────────────────────────┐
Kommo webhook ──►│ W01 Conversão real ───────────► POST /conversao ──┐                                          │
Agendador ──────►│ W02 Coleta  W03 Urgências+freio ─► /freio/avaliar ├──► trilha-api (rede interna, sem porta    │
                 │ W04 Pacing  W05 Leitura diária                     │     pública): perfil, metas, hash,        │
ClickUp gatilho ►│ W06 Execução do aprovado ──────► /calcular ───────┘     payloads, regras do freio             │
                 │ W07 Pauta de contato   W08 SLA Kommo   W09 Onboarding                                            │
                 │ W10 Vigia de falhas    W11 Pacote da reunião   W12 Dossiê de otimização                         │
                 │ W13 Pós-reunião        W14 Painel da carteira                                                    │
                 └───────────────┬─────────────────────────────────────────────────────────────────────────────────┘
                                 ▼
          ClickUp (dossiês, pautas, pacotes, tarefas) · Slack (urgências, falhas) · Postgres · BigQuery → Looker Studio
```

Regra de divisão (ADR-007): erro que custa dinheiro ou expõe dado pessoal → trilha-api, com teste. Erro que só atrasa uma entrega → pode ficar no n8n.

## 2. Mapa de fluxos

Cada fluxo é **um só para toda a carteira**: lê a lista de clientes (diretório `trilha-clientes` via trilha-api ou tabela no Postgres) e percorre cada um. Nunca copiar fluxo por cliente.

| Fluxo | Serve a | Disparo | Faz | Status |
|---|---|---|---|---|
| **W01** Conversão real | base de tudo | webhook do Kommo `…/webhook/kommo/<cliente_id>?token=…` | confere token, responde 200 na hora, chama `/conversao`, avisa no Slack se algo foi pulado | ✅ exportado (`n8n/fluxos/W01-conversao-real.json`) |
| **W02** Coleta | dossiê, pacote, painel | diário 05:00 | Meta Insights + Google (GAQL) por cliente → BigQuery `fato_midia` | ⬜ |
| **W03** Urgências + freio | freio de emergência | a cada 2h, 07–23h, todos os dias | métricas do dia → `/freio/avaliar` → pausa (modo A) ou só avisa (modo B) → Slack com botão de desfazer; também: gasto zerado, entrega parada, reprovação | ⬜ (regra pronta na API) |
| **W04** Pacing | dossiê | diário 06:00 | projeção do gasto do mês × verba contratada por cliente e plataforma | ⬜ |
| **W05** Leitura diária | assessor | dias úteis 07:30 | uma mensagem no Slack com a carteira em 5 linhas por cliente; resumo escrito com Claude a partir dos números já calculados | ⬜ |
| **W06** Execução do aprovado | sessão de otimização | gatilho do ClickUp (status → "Aprovado") | confere se a conta ainda está no estado "antes", executa, registra, comenta o resultado na tarefa | ⬜ |
| **W07** Pauta de contato | contato proativo | véspera de `operacao.dia_contato`, 16:00 | boa notícia, ponto de atenção, pergunta, rascunho de mensagem → tarefa no ClickUp. **Não envia nada ao cliente.** | ⬜ |
| **W08** SLA de atendimento | ponto de atenção da pauta, gatilho de contato extra | a cada 15 min no horário comercial | leads sem primeiro contato além do SLA do `marca.yaml` → aviso ao assessor/analista | ⬜ |
| **W09** Onboarding | entrada de cliente | formulário | `/validar` o perfil → lista "Onboarding" no ClickUp a partir do modelo → checklist de campos do Kommo | ⬜ |
| **W10** Vigia de falhas | todos | fluxo de erro global | toda falha de qualquer fluxo vira aviso no Slack com etapa, erro e link da execução | ✅ exportado (`n8n/fluxos/W10-vigia-de-falhas.json`) |
| **W11** Pacote da reunião | reunião mensal | 2 dias úteis antes da reunião (`operacao.semana_reuniao` / `dia_reuniao`) | resultado × meta vigente, testes, decisões e efeito, proposta de 30 dias, perguntas → documento no ClickUp/Drive | ⬜ |
| **W12** Dossiê de otimização | sessão semanal | véspera de `operacao.dia_otimizacao`, 16:00 | placar, mudanças, decisões anteriores e efeito, 3–5 sugestões com simulação, testes, freio, atendimento → tarefa no ClickUp | ⬜ |
| **W13** Pós-reunião | reunião mensal | áudio/texto anexado à tarefa da reunião | transcrição → ata → tarefas com responsável e prazo → rascunho de nova versão do perfil quando meta/verba/oferta mudaram | ⬜ |
| **W14** Painel da carteira | alinhamento com a equipe | véspera da reunião de equipe | semáforo por cliente, tarefas atrasadas por pessoa, criativos pendentes, tokens e contratos perto de vencer, clientes sem contato na semana | ⬜ |

**Prioridade de construção:** W10 → W01 → W02 → W03 → W12 → W06 → W07 → W04/W05 → W11/W13 → W14 → W08 → W09 (ver [ROADMAP](../../ROADMAP.md)).

## 3. Volume e custo (8 clientes, ~300 leads/mês cada)

| Fluxo | Execuções/mês |
|---|---|
| W01 (uma por evento do Kommo) | 7.000–10.000 |
| W06 (o gatilho do ClickUp dispara em toda atualização de tarefa) | 1.000–3.000 |
| W08 (laço por cliente, a cada 15 min) | ~1.300 |
| W10 | ~750 |
| W03 | ~270 |
| Demais (W02, W04, W05, W07, W11–W14) | < 300 |
| **Total** | **~10–15 mil** |

Com fluxos copiados por cliente, o total passaria de 22 mil — mais um motivo para o desenho em laço.

| Item | Mensal estimado |
|---|---|
| Servidor (4 vCPU / 8 GB) com n8n, worker, Redis, Postgres, Caddy | R$ 100–300 |
| BigQuery + Looker Studio | R$ 0–50 |
| API do Claude (W05, W07, W11, W12, W13: ~300 chamadas de ~6 mil tokens) | dezenas de dólares — conferir tabela vigente |
| Backups externos e monitoramento | R$ 0–50 |
| **Total** | **~R$ 300–800** |

## 4. Os dez requisitos de operação profissional

1. **Fluxos com parâmetros, nunca copiados por cliente.**
2. **Credenciais organizadas:** Meta — um usuário do sistema por Business Manager, token sem expiração; Google — uma credencial na MCC, **app OAuth publicado em produção** (em modo "teste" o token de atualização expira em 7 dias); Kommo — um token por conta em `infra/kommo-tokens.env`, validade registrada no ClickUp com aviso 30 dias antes (W14).
3. **Fluxo de erro global:** todo fluxo aponta para o W10 em *Settings → Error workflow*.
4. **Vigia externo:** um serviço fora do servidor (ex.: monitor de "batimento") recebe um ping ao fim do W02 e do W03; sem ping no horário, avisa. O n8n não consegue avisar que ele mesmo caiu.
5. **LGPD no histórico de execuções:** `EXECUTIONS_DATA_SAVE_ON_SUCCESS=none`, limpeza após 7 dias, e dados pessoais tratados só na trilha-api (o W01 nunca vê telefone ou e-mail).
6. **Versionamento:** `infra/backup.sh` exporta todos os fluxos para `n8n/fluxos/` e faz commit todo dia (o Git nativo do n8n é recurso pago).
7. **Ambiente de teste:** segunda instância (ou outra porta) ligada a uma conta de teste do Kommo e ao `META_TEST_EVENT_CODE`; `TRILHA_SIMULAR=1` até o primeiro evento aparecer certo no Gerenciador de Eventos.
8. **Modo fila com Redis** para absorver rajadas de webhooks (importações de leads no Kommo).
9. **Webhooks protegidos:** token na URL do Kommo (conferido no W01), assinatura do ClickUp conferida no W06, HTTPS pelo Caddy, trilha-api sem porta pública.
10. **Runbook:** a §6 deste documento, mantida junto com cada fluxo novo.

## 5. Segurança: leitura de variáveis de ambiente

Os fluxos leem configuração por `$env` (`TRILHA_API_URL`, `TRILHA_API_TOKEN`, `KOMMO_WEBHOOK_TOKEN`, `SLACK_WEBHOOK_URL`), o que exige `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`. Consequência: qualquer fluxo pode ler qualquer variável do contêiner do n8n. Aceitável numa instância de uso exclusivo da equipe, com acesso de edição restrito. Alternativas: guardar esses valores como credenciais do n8n (tipo "Header Auth") ou usar as Variáveis do n8n (recurso pago).

## 6. Runbook

| Sintoma | Onde olhar | Ação |
|---|---|---|
| Aviso do W10 no Slack | link da execução no aviso | ler a etapa e o erro; 401/403 = credencial; 429 = limite da API (o fluxo tenta de novo); 5xx = indisponibilidade da plataforma |
| W01 avisa "lead sem identificador" com frequência | campos `gclid`/`fbclid`/`ctwa_clid` no Kommo do cliente | conferir campos ocultos da landing, GTM e integração do WhatsApp (KOMMO.md §4) |
| W01 avisa "perfil sem …" | `perfil.yaml` do cliente em `trilha-clientes` | completar o bloco e rodar `python -m trilha validar` |
| Evento desconhecido do Kommo (etapa nova) | `crm.mapa_eventos` | o cliente criou/renomeou etapa: atualizar o mapa |
| Sem leitura diária (W05) às 08h | vigia externo / `docker compose ps` | reiniciar o serviço; se o banco caiu, restaurar do backup |
| Freio pausou campanha | aviso no Slack | decidir na hora (desfazer) ou na sessão semanal; nunca deixar sem decisão até a sessão |
| Token do Kommo expirando (W14) | ClickUp | gerar novo token na conta do cliente e atualizar `infra/kommo-tokens.env`; reiniciar a trilha-api |
| Restaurar do zero | `infra/backup/` + `N8N_ENCRYPTION_KEY` guardada fora do servidor | subir o compose, restaurar o `pg_dump`, conferir credenciais |

## 7. Importar os fluxos exportados

1. Importar `W10-vigia-de-falhas.json` primeiro; anotar o ID gerado.
2. Importar `W01-conversao-real.json`; em *Settings → Error workflow*, apontar para o W10 (o arquivo traz o marcador `DEFINIR_ID_DO_W10_APOS_IMPORTAR`).
3. Ativar o W01 e cadastrar no Kommo de cada cliente o webhook `https://<dominio>/webhook/kommo/<cliente_id>?token=<KOMMO_WEBHOOK_TOKEN>` para os eventos de lead criado e mudança de etapa.
4. Testar com `TRILHA_SIMULAR=1`: mover um lead de teste e conferir a execução e a resposta da trilha-api.

Os arquivos foram escritos para o formato de exportação atual do n8n, mas **ainda não foram importados numa instância real**: conferir tipo e versão de cada nó ao importar.
