# Integração ClickUp

> Quem faz o quê: [MODELO-OPERACIONAL.md](../../MODELO-OPERACIONAL.md) · Fluxos: [N8N.md](N8N.md) (W06, W07, W09, W11–W14)
> Princípio: o ClickUp é **a mesa de trabalho do assessor**. Tudo o que o sistema prepara chega como tarefa; toda decisão do assessor é tomada na tarefa. O Trilha não tem tela própria.

## 1. Espaço padrão

```
Espaço "Trilha"
├── Pasta por cliente
│   ├── Lista "Otimização semanal"   ← um dossiê por semana (W12); sugestões como subtarefas
│   ├── Lista "Contato proativo"     ← uma pauta por semana (W07)
│   ├── Lista "Reuniões"             ← pacote antes (W11), ata e encaminhamentos depois (W13)
│   ├── Lista "Testes"               ← protocolo de testes (núcleo §9.4)
│   ├── Lista "Criativos"            ← esteira de produção
│   └── Lista "Onboarding"           ← modelo com o checklist de auditoria (W09)
├── Lista "Carteira"                 ← painel e pauta da reunião de equipe (W14)
└── Lista "Decisões"                 ← sugestão → decisão → resultado, todas as contas
```

## 2. Sessão semanal de otimização (W12 → W06)

```
Véspera do dia_otimizacao, 16:00 — W12 cria a tarefa "Otimização · <cliente> · semana NN"
  descrição: placar, mudanças, decisões anteriores e efeito, testes, freio, atendimento
  subtarefas: uma por sugestão (3 a 5), com motivo, simulação antes → depois, R$ em jogo e risco
       campos ocultos: plataforma, entidade_id, tipo_acao, payload_json, estado_antes_hash

Na sessão, o assessor decide cada subtarefa:
  "Aprovado"  → W06 confere a assinatura do webhook, confere se a entidade ainda está no estado "antes",
                executa, registra no histórico de alterações e comenta o resultado
  "Ajustar"   → o assessor edita o valor; W06 recalcula a simulação e devolve para decisão
  "Recusado"  → vai para "Decisões" com o motivo (mede a qualidade do dossiê)
  sem decisão até o fim do dia da sessão → expira (dado velho não é executado)
```

Se o estado da entidade mudou entre o dossiê e a aprovação (alguém mexeu na conta), o W06 não executa e devolve a subtarefa para "Ajustar" com a diferença.

## 3. Contato proativo (W07)

Tarefa "Contato · <cliente> · semana NN", criada na véspera do `dia_contato`:
- boa notícia com número · ponto de atenção · pergunta para o cliente;
- **rascunho de mensagem** no tom do `marca.yaml`, no campo "Rascunho" — o assessor reescreve e envia pelo próprio canal;
- o assessor marca "Feito" e, se quiser, cola a resposta do cliente: ela entra no contexto do próximo dossiê.

Gatilhos de contato extra (recorde, queda, verba acabando, problema de atendimento, freio acionado) chegam como comentário na tarefa da semana e aviso no Slack.

## 4. Reunião mensal (W11 → W13)

- **Antes:** tarefa "Reunião mensal · <cliente> · <mês>" com o pacote (documento ou slides para revisão) dois dias úteis antes.
- **Depois:** o assessor anexa o áudio ou escreve os pontos; o W13 gera a ata no corpo da tarefa, cria as tarefas de encaminhamento (responsável, prazo) e, se meta/verba/oferta mudaram, anexa o rascunho da nova versão do `perfil.yaml` para validação.

## 5. Carteira e reunião de equipe (W14)

Tarefa semanal em "Carteira": semáforo por cliente, tarefas atrasadas por pessoa, criativos pendentes, tokens e contratos perto de vencer, clientes sem contato proativo registrado na semana, e proposta de pauta.

## 6. Testes, criativos e onboarding

- **Testes:** campos da tarefa = protocolo do núcleo §9.4 (hipótese, variável, métrica, amostra mínima, duração máxima, regra de decisão, resultado). O sistema atualiza o progresso da amostra; o assessor dá o veredito.
- **Criativos:** briefings decididos na sessão semanal viram tarefas para quem produz, com as etiquetas da taxonomia em campos e o link da peça.
- **Onboarding:** o W09 cria a lista a partir do modelo (auditoria do núcleo §3.3 + checklists do Meta e do Google + campos do Kommo).

## 7. Implementação

API v2 do ClickUp com token em `.env` (`CLICKUP_TOKEN`); webhooks do ClickUp com assinatura conferida (`CLICKUP_WEBHOOK_SECRET`). Os gatilhos e ações rodam nos fluxos do n8n ([N8N.md](N8N.md)); a decisão de executar (estado "antes" igual, valor dentro do teto contratado) passa pela trilha-api.
