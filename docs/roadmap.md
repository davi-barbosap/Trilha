# Roadmap — implantação

> Escopo: [ecossistema](ecossistema.md) · Quem faz o quê: [modelo operacional](modelo-operacional.md)
> Legenda: ✅ pronto · 🟡 parcialmente pronto · ⬜ a fazer

O sistema entra em operação num cliente piloto, é testado na prática e depois é estendido ao resto da carteira (só configuração: um `perfil.yaml` por cliente, nenhum fluxo novo). A lista abaixo está na ordem em que um item depende do anterior.

## Pronto

- ✅ Esquema validado do `perfil.yaml` (agenda do material, freio, mapa de eventos do Kommo)
- ✅ Calculadora de economia unitária (CAC, CPL e CPL qualificado máximos, verba por degrau)
- ✅ Leitura do Kommo com confirmação da etapa real do lead
- ✅ Conversões para o Meta (API de Conversões v26.0) e para o Google (Data Manager API), com hash e deduplicação
- ✅ Regras do freio de emergência
- ✅ trilha-api: `/saude`, `/clientes`, `/validar`, `/calcular`, `/conversao`, `/freio/avaliar`, com segredo de webhook por cliente
- ✅ Fluxos-modelo do n8n: W01 (conversão real) e W10 (vigia de falhas)
- ✅ Infraestrutura descrita em `infra/` (n8n 2.x, Postgres, Redis, trilha-api, HTTPS, backup)
- ✅ 42 testes e verificação automática no GitHub

## Para entrar em operação

| # | Item | Material que passa a ficar pronto | Pronto quando | Status |
|---|---|---|---|---|
| 1 | **Servidor autohospedado** do n8n + **W10** vigia de falhas | — (base) | `/saude` responde; uma falha forçada chega no Slack; um backup é restaurado | 🟡 tudo escrito; falta o servidor |
| 2 | **W01** conversão real no piloto (Meta) | todos | `lead_qualificado` aparece no Gerenciador de Eventos, primeiro com `META_TEST_EVENT_CODE`, depois em produção | 🟡 falta importar e ligar no Kommo do piloto |
| 3 | Envio ao Google (Data Manager API) + **W02** coleta diária | dossiê, relatório | `validateOnly` aceito, depois envio real; dados do dia anterior disponíveis às 05:30 | 🟡 payload pronto |
| 4 | **W03** urgências + freio, **W04** pacing, **W05** leitura diária | monitoramento | uma pausa de teste com aviso e desfazer; leitura diária no Slack às 07:30 | 🟡 regra do freio pronta |
| 5 | **W12** dossiê de otimização + histórico de alterações | otimização semanal | o assessor faz a sessão do piloto só com o dossiê | ⬜ |
| 6 | **W06** execução do aprovado (ClickUp) | otimização semanal | uma mudança aprovada é executada e desfeita em teste | ⬜ |
| 7 | **W07** números do relatório semanal | relatório semanal | relatório do piloto com os três blocos (leads · criativos · ações) na véspera | ⬜ |
| 8 | **W08** pacote de dados do briefing | briefing de criativo | um briefing do piloto escrito sobre o pacote | ⬜ |
| 9 | **W11** pacote da reunião + **W14** painel da carteira | reunião mensal, alinhamento com a equipe | uma reunião preparada em ≤ 15 min; painel na véspera da reunião de equipe | ⬜ |
| 10 | Entrada dos demais clientes | tudo | perfis válidos em `/clientes`; material de todos chegando na véspera | ⬜ |

## Depois de operar

Sem prazo. Cada item entra quando a operação mostrar que vale a pena.

- Taxonomia de ângulos e renomeação dos anúncios existentes (o material passa a dizer "qual argumento converte").
- Subida de campanhas e anúncios aprovados pelo assessor.
- Auditoria de onboarding automatizada (Meta, Google, desperdício em termos de pesquisa).
- Varredura de termos de pesquisa do Google como ponto de atenção no dossiê.
- Painel MTD no Looker Studio e calendário sazonal.
- Verificador de copy dos anúncios.
- Estatística avançada (quando algum cliente tiver 20+ conversões por dia) e vencedores por argumento.
- Novos segmentos e plataformas (TikTok, LinkedIn).

## Em paralelo (fora deste repositório)

BotConversa · GA4/GTM · landing pages · disparos em massa · fluxos de CRM no Kommo · captura de tarefas no ClickUp · onboarding (briefing-trilha). Ver [ecossistema](ecossistema.md).
