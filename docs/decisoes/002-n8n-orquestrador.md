# ADR-002 — n8n como orquestrador, trilha-api como núcleo

**Status:** aceita

## Contexto
A operação é de assessoria: vários clientes, um assessor que faz o relacionamento ([modelo operacional](../modelo-operacional.md)) e, no máximo, um responsável técnico em meio período. Quem mantém o sistema quando um token expira numa terça às 18h precisa conseguir fazer isso sem ser programador.

## Decisão
- **n8n 2.x autohospedado** (edição gratuita, modo fila com Redis, banco Postgres) agenda, conecta e entrega: Kommo, ClickUp, Slack, Meta, Google.
- **trilha-api** (o pacote `trilha` exposto por HTTP, `python -m trilha servir`) decide tudo o que custa dinheiro ou envolve dado pessoal: validação do perfil, metas, mapa de eventos, hash, payloads de conversão, regras do freio.
- **Regra de divisão:** se um erro custa dinheiro ou expõe dado pessoal, a lógica fica na trilha-api, com teste. Se o erro só atrasa uma entrega, pode ficar no n8n. Nó de código no n8n com mais de ~30 linhas vai para a trilha-api.
- **Dados pessoais de leads não passam pelo n8n:** a trilha-api busca o lead no Kommo e devolve só payloads com hash.
- **Fluxos com parâmetros, nunca copiados por cliente:** um fluxo lê a lista de clientes e percorre cada um.
- Fora: Make/Zapier (cobrança por operação inviável no volume da carteira, sem lugar para a lógica crítica) e n8n Cloud (planos limitados por número de execuções).

## Consequências
- A maior parte do sistema fica em fluxos visuais; a parte crítica fica em código testado.
- Infraestrutura em `infra/`; fluxos de produção versionados em `n8n/fluxos/` pela exportação diária.
- Licença do n8n (Sustainable Use License): uso interno da agência para atender clientes é o caso comum; dar acesso ao n8n para clientes ou revendê-lo exige revisão da licença.
- n8n 2.x bloqueia por padrão o acesso a variáveis de ambiente nos nós. Segredos dos fluxos ficam em credenciais do n8n; `$env` é liberado só para configuração de baixo risco ([n8n](../integracoes/n8n.md) §5).
