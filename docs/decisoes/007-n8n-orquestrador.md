# ADR-007 — n8n como orquestrador, trilha-api como núcleo

**Status:** aceita · 2026-10-03 · substitui o [ADR-002](002-orquestracao.md)

## Contexto
O ADR-002 previa tudo em código (Cloud Run), assumindo uma equipe com desenvolvedor. A operação real é de assessoria: 8+ clientes, um assessor sênior que faz os rituais com o cliente ([MODELO-OPERACIONAL.md](../../MODELO-OPERACIONAL.md)) e, no máximo, um responsável técnico em meio período. A pergunta decisiva é quem mantém o sistema numa terça-feira às 18h quando um token expira — e um sistema 100% em código vira dependência perigosa sem programador.

## Decisão
- **n8n instalado no próprio servidor** (edição gratuita, modo fila com Redis, banco Postgres) agenda, conecta e entrega: Kommo, ClickUp, Slack, Meta, Google.
- **trilha-api** (o pacote `trilha` exposto por HTTP, `python -m trilha servir`) decide tudo o que custa dinheiro ou envolve dado pessoal: validação do perfil, metas, mapa de eventos, hash, payloads de conversão, regras do freio.
- **Regra de divisão:** se um erro custa dinheiro ou expõe dado pessoal, a lógica fica na trilha-api, com teste. Se o erro só atrasa uma entrega, pode ficar no n8n. Nó de código no n8n com mais de ~30 linhas vai para a trilha-api.
- **Dados pessoais de leads não passam pelo n8n:** a trilha-api busca o lead no Kommo e devolve só payloads com hash.
- **Fluxos com parâmetros, nunca copiados por cliente:** um fluxo lê a lista de clientes e percorre cada um.
- Make/Zapier ficam fora: cobrança por operação inviável no volume da carteira e sem lugar para a lógica crítica.
- n8n Cloud fica fora no volume atual (~10–15 mil execuções/mês com o desenho em laço): os planos da nuvem limitam execuções.

## Consequências
- Cerca de 80% do sistema fica em fluxos visuais que o responsável técnico mantém; 20% em código testado.
- Infraestrutura em `infra/` (docker-compose com n8n + worker, Postgres, Redis, trilha-api, Caddy); fluxos versionados em `n8n/fluxos/` por exportação diária.
- Licença do n8n (Sustainable Use License): uso interno da agência para atender clientes é o caso comum; dar acesso ao n8n para clientes ou revendê-lo exige revisão da licença.
- Os dez requisitos de operação profissional estão em [N8N.md](../integracoes/N8N.md) §4.
