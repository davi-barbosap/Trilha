# Trilha

Sistema de automação de mídia paga (Meta Ads e Google Ads) com Claude, agnóstico de cliente: um núcleo único que se adapta a cada onboarding, marca e oferta.

**O sistema faz o trabalho manual e prepara; o assessor decide, se relaciona com o cliente e alinha a equipe.** Cada semana, para cada cliente, o assessor recebe pronto o dossiê da sessão de otimização e a pauta do contato proativo; cada mês, o pacote da reunião. Nada sai do sistema direto para o cliente.

**Status:** v0.5. O modelo operacional e a arquitetura estão fechados; o MVP de 8 semanas está em construção ([ROADMAP](ROADMAP.md)).

## Documentos

| Documento | Conteúdo |
|---|---|
| [MODELO-OPERACIONAL.md](MODELO-OPERACIONAL.md) | **Comece por aqui.** Quem faz o quê, os rituais do assessor e o que o sistema entrega para cada um, capacidade, agenda, freio de emergência |
| [ROADMAP.md](ROADMAP.md) | Roadmap único: MVP de 8 semanas organizado pelos rituais, e indicadores |
| [ARQUITETURA-NUCLEO.md](ARQUITETURA-NUCLEO.md) | Comum a todas as plataformas: estratégia (Camada 0), onboarding, perfil, brand kit, playbooks, conversão real, estatística, governança |
| [ARQUITETURA-META-ADS.md](ARQUITETURA-META-ADS.md) | Módulos específicos do Meta: estrutura de conta, Advantage+, destinos, módulo criativo |
| [ARQUITETURA-GOOGLE-ADS.md](ARQUITETURA-GOOGLE-ADS.md) | Módulos específicos do Google: palavras-chave, campanhas, RSA, negativas, landing pages, rastreamento |
| [docs/decisoes/](docs/decisoes/) | Registro de decisões de arquitetura (ADRs 001–008), incluindo n8n como orquestrador e freio de emergência |
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
n8n/fluxos/        fluxos do n8n exportados (W01, W10)
infra/             servidor da operação: docker-compose (n8n, Postgres, Redis, trilha-api, Caddy), backup
tests/             testes e fixtures
playbooks/         padrões por segmento (imobiliário)
clientes/_exemplo/ modelo de cliente — clientes reais ficam no repositório privado (ADR-004)
docs/              decisões e integrações
```

Segredos: copie `.env.example` para `.env`. O `.env` nunca é versionado.
