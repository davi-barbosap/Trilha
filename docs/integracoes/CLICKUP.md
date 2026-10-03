# Integração ClickUp

> Núcleo: §10 (governança, níveis de autonomia) · Roadmap: MVP semana 6 e Fase 2–3
> Princípio: o ClickUp é a **interface de operação e governança** — o Trilha não constrói tela própria de aprovação.

## 1. Espaço padrão

```
Espaço "Trilha"
├── Pasta por cliente
│   ├── Lista "Aprovações"        ← fila L1
│   ├── Lista "Testes"            ← protocolo de testes (núcleo §9.4)
│   ├── Lista "Criativos"         ← esteira do volante criativo
│   ├── Lista "Onboarding"        ← modelo com o checklist de auditoria Meta/Google
│   └── Lista "Entregas"          ← relatórios mensais e resumos ao cliente
└── Lista "Decisões"              ← registro sugestão → decisão → resultado (todas as contas)
```

## 2. Fila de aprovação (MVP, semana 6)

```
Motor gera sugestão L1
  → cria tarefa em "Aprovações": título curto, descrição com simulação antes → depois,
    impacto estimado em R$/dia, motivo, link para o painel
    campos: cliente, plataforma, tipo_acao, entidade_id, payload_json (oculto), prazo
  → gestor muda o status:
       "Aprovado"   → webhook taskStatusUpdated → Trilha executa → registra no histórico → comenta o resultado
       "Ajustar"    → gestor edita o campo de valor → Trilha recalcula a simulação
       "Recusado"   → registrado em "Decisões" com o motivo (calibra a liberação de L2)
  → sem decisão até o prazo: a sugestão expira (dado velho não é executado)
```

Segurança: o webhook do ClickUp é validado pela assinatura do cabeçalho `X-Signature`; o Trilha confere que o usuário que aprovou tem permissão para aquele cliente e que o estado atual da entidade ainda é o "antes" da simulação — se mudou, a tarefa volta para "Ajustar".

## 3. Registro de testes

Campos da tarefa = protocolo do núcleo §9.4: hipótese, variável, métrica de decisão, amostra mínima, duração máxima, regra de decisão, resultado. O Trilha atualiza o progresso da amostra e fecha a tarefa com o veredito.

## 4. Esteira criativa (Fase 3)

Cada briefing do volante criativo (Meta §6.5) vira tarefa para o designer/videomaker: etiquetas da taxonomia (eixo, objeção, avatar, formato, gancho) em campos, prazo, link da peça final (Canva/Drive). Ao subir, a peça passa pelo verificador de copy antes de ir para "Aprovação do cliente".

## 5. Onboarding e entregas

- Novo cliente → a lista "Onboarding" é criada a partir do modelo (auditoria do núcleo §3.3 + checklists das plataformas), com responsáveis e prazos do plano de 90 dias.
- Relatório mensal e resumo semanal geram tarefas recorrentes com revisão humana antes do envio.

## 6. Implementação

API v2 do ClickUp (token por espaço, em `.env`) para criar e atualizar tarefas e webhooks; há servidores MCP do ClickUp que podem ser usados para consultas no chat. Código previsto em `trilha/integracoes/clickup.py`.
