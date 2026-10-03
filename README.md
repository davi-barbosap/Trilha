# Trilha

Sistema de automação de mídia paga (Meta Ads e Google Ads) com Claude, agnóstico de cliente: um núcleo único que se adapta a cada onboarding, marca e oferta.

**Objetivo único: executar o trabalho manual que sustenta os serviços de mídia paga.** O assessor pensa, decide e fala com o cliente; o sistema coleta, confere, calcula, devolve as conversões reais ao Meta e ao Google e deixa pronto, na véspera, o material de cada compromisso: dossiê da otimização semanal, números do relatório semanal, pacote de dados do briefing, pacote da reunião mensal e painel da carteira. Nada sai do sistema direto para o cliente.

Landing pages, disparos em massa, fluxos de CRM, BotConversa, GA4 e captura de tarefas no ClickUp são **ferramentas paralelas**, fora deste repositório ([ECOSSISTEMA.md](ECOSSISTEMA.md)).

**Status:** v0.6. Escopo, modelo operacional e arquitetura fechados; o MVP de 8 semanas aguarda o servidor autohospedado do n8n ([ROADMAP](ROADMAP.md)).

## Documentos

| Documento | Conteúdo |
|---|---|
| [ECOSSISTEMA.md](ECOSSISTEMA.md) | **Comece por aqui.** O que é deste sistema, o que é do assessor, o que corre em paralelo — e o que as ferramentas paralelas precisam entregar |
| [MODELO-OPERACIONAL.md](MODELO-OPERACIONAL.md) | O cargo de assessor e o sistema, item por item; o material de cada compromisso; capacidade realista; freio de emergência |
| [ROADMAP.md](ROADMAP.md) | Roadmap único: MVP de 8 semanas organizado pelos rituais, e indicadores |
| [ARQUITETURA-NUCLEO.md](ARQUITETURA-NUCLEO.md) | Comum a todas as plataformas: estratégia (Camada 0), onboarding, perfil, brand kit, playbooks, conversão real, estatística, governança |
| [ARQUITETURA-META-ADS.md](ARQUITETURA-META-ADS.md) | Módulos específicos do Meta: estrutura de conta, Advantage+, destinos, módulo criativo |
| [ARQUITETURA-GOOGLE-ADS.md](ARQUITETURA-GOOGLE-ADS.md) | Módulos específicos do Google: palavras-chave, campanhas, RSA, negativas, landing pages, rastreamento |
| [docs/decisoes/](docs/decisoes/) | Registro de decisões de arquitetura (ADRs 001–009): n8n como orquestrador, freio de emergência, escopo do sistema |
| [docs/integracoes/](docs/integracoes/) | Especificações: [n8n](docs/integracoes/N8N.md) · [Kommo](docs/integracoes/KOMMO.md) · [ClickUp](docs/integracoes/CLICKUP.md) · [outras](docs/integracoes/OUTRAS.md) |

## O que já roda

```bash
pip install -e .

# valida o perfil de um cliente (esquema rígido: campo errado ou incoerente é rejeitado)
python -m trilha validar clientes/_exemplo/perfil.yaml

# calculadora de economia unitária: CAC/CPL máximos e verba por degrau da escada de otimização
python -m trilha calcular clientes/_exemplo/perfil.yaml --verba 8000

# o que um webhook do Kommo enviaria ao Meta (API de Conversões) e ao Google (conversão offline), sem enviar nada
python -m trilha simular-webhook tests/fixtures/kommo_webhook.txt \
  --perfil clientes/_exemplo/perfil.yaml \
  --lead tests/fixtures/kommo_lead.json --contato tests/fixtures/kommo_contato.json

# trilha-api: o núcleo por HTTP, chamado pelos fluxos do n8n
TRILHA_API_TOKEN=um-segredo TRILHA_CLIENTES_DIR=clientes python -m trilha servir --porta 8080

# testes (só biblioteca padrão + pydantic + pyyaml)
python -m unittest discover -s tests -v
```

## Estrutura

```
trilha/            pacote Python = trilha-api (core, conversao, integracoes, plataformas, api.py)
n8n/modelos/       fluxos-modelo do n8n (W01, W10) · n8n/fluxos/: exportação diária da produção
infra/             servidor da operação: docker-compose (n8n, Postgres, Redis, trilha-api, Caddy), backup
tests/             testes e fixtures
playbooks/         padrões por segmento (imobiliário)
clientes/_exemplo/ modelo de cliente — clientes reais ficam no repositório privado (ADR-004)
docs/              decisões e integrações
```

Segredos: copie `.env.example` para `.env`. O `.env` nunca é versionado.
