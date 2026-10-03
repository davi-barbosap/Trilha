# Ecossistema — o que é deste sistema, o que é do assessor, o que corre em paralelo

> Decisão: [ADR-007](decisoes/007-escopo-do-sistema.md)
> Este documento delimita o escopo. Quando outro documento contradisser, vale este.

## 1. Objetivo único deste sistema

**Executar o trabalho manual que sustenta os serviços de mídia paga do assessor** — coletar, conferir, calcular, devolver conversões às plataformas, montar os números e o material de apoio — para que o assessor gaste o tempo dele pensando, decidindo e se relacionando com o cliente.

O sistema **não pensa a estratégia** e **não fala com o cliente**.

## 2. As três colunas

| Assessor (humano) | Este sistema (Trilha) | Ferramentas paralelas (fora deste repositório) |
|---|---|---|
| Estratégia, decisões de verba, estrutura, criativo e oferta | **Conversão real:** Kommo → Meta (API de Conversões) e Google (Data Manager API) | **BotConversa:** atendimento e fluxos no WhatsApp |
| **Contatos proativos** com o cliente (≥ 3 por semana) | **Coleta e monitoramento:** Meta, Google e Kommo; pacing; urgências; freio de emergência | **GA4 / GTM:** rastreamento do site e eventos |
| **Respostas no grupo do cliente** (≤ 2 h) | **Dossiê da otimização semanal** e execução do que o assessor aprovar | **Landing pages** |
| Sessão de otimização semanal (decide) | **Números do relatório semanal** ao cliente (leads · criativos · ações) | **Disparos em massa** |
| Relatório semanal: escreve os insights e apresenta | **Pacote de dados do briefing** de criativo | **Fluxos de CRM** no Kommo (incl. `build_kommo_json.py` do briefing-trilha) |
| Briefing de criativo: escreve a estratégia | **Pacote da reunião mensal** | **Captura de tarefas no ClickUp no mesmo dia** (n8n) |
| Reunião mensal: conduz | **Painel da carteira** para a reunião de equipe | **Onboarding** (wizard do briefing-trilha) |
| Alinhamento com a equipe | | |

## 3. O que este sistema precisa das ferramentas paralelas (contratos de interface)

O Trilha não constrói essas ferramentas, mas depende do que elas gravam. Sem isso, a conversão real e os relatórios ficam incompletos.

| Ferramenta paralela | Precisa entregar ao Trilha | Por quê |
|---|---|---|
| **Landing pages** | campos ocultos com `gclid`, `gbraid`, `wbraid`, `fbclid` e UTMs, gravados nos campos personalizados do lead no Kommo ([Kommo](integracoes/kommo.md) §4) | sem o identificador de clique, a venda não volta para o Google/Meta |
| **BotConversa** | quando atender a conversa vinda de anúncio de clique para WhatsApp, repassar o `ctwa_clid` e as UTMs ao lead no Kommo; mover o lead nas etapas padronizadas | sem o `ctwa_clid`, a qualificação da conversa não volta para o Meta |
| **GA4 / GTM** | tag do Google e pixel do Meta funcionando nas páginas; eventos de conversão do site; `event_id` compartilhado entre pixel e servidor quando houver API de Conversões no site | o freio de emergência usa "horas sem evento de conversão"; deduplicação no Meta |
| **Fluxos de CRM (Kommo)** | etapas do funil padronizadas e estáveis (o mapa etapa → evento depende dos IDs); motivo de perda obrigatório | mapa de eventos (`crm.mapa_eventos`) e bloco "leads" do relatório |
| **Captura de tarefas (n8n)** | tarefas no ClickUp com o cliente identificado (pasta do cliente) | painel da carteira lê tarefas atrasadas por pessoa |
| **Onboarding (briefing-trilha)** | `perfil.yaml`, `marca.yaml`, `ofertas/*.yaml` que passam no `python -m trilha validar` | contrato de dados ([ADR-005](decisoes/005-dependencia-briefing-trilha.md)) |

Mudou uma etapa no Kommo, um campo oculto da página ou o fluxo do BotConversa? Avisar quem cuida do Trilha: o mapa de eventos e o W01 precisam acompanhar.

## 4. Fora do escopo, de propósito

- Construir landing pages, disparos em massa ou fluxos de CRM/atendimento.
- Medir ou cobrar tempo de resposta e contatos do assessor com o cliente.
- Escrever mensagens ao cliente, roteiros, peças criativas ou a estratégia de um briefing.
- Prospecção comercial da agência. (A calculadora de economia unitária pode ser usada nisso, mas como uso paralelo; aqui ela serve para as metas de cada cliente.)
