# ADR-004 — Dados de clientes fora do repositório de código

**Status:** aceita · 2026-10-03

## Contexto
A v0.3 previa `clientes/<cliente>/` dentro deste repositório, com margem, ticket, regras comerciais e histórico. Isso mistura código (que pode ser compartilhado com freelancers e ferramentas) com dado sensível de negócio e, eventualmente, dado pessoal (LGPD).

## Decisão
- Este repositório guarda apenas `clientes/_exemplo/`. O `.gitignore` bloqueia qualquer outra pasta em `clientes/`.
- Clientes reais vivem em um repositório **privado** separado (`trilha-clientes`), com acesso só da equipe de operação, apontado pela variável `TRILHA_CLIENTES_DIR`.
- Dados pessoais de leads nunca vão para nenhum repositório: ficam no Kommo e no banco (ADR-001), e saem para as plataformas apenas em hash.

## Consequências
- O código pode ser revisado e testado sem expor clientes.
- Saída de cliente (núcleo §10) = arquivar a pasta dele no repositório privado e apagar os dados no banco conforme a política de retenção.
