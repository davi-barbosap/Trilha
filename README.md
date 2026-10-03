# Trilha

Sistema de automação de mídia paga (Meta Ads e Google Ads) com Claude, agnóstico de cliente: um núcleo único que se adapta a cada onboarding, marca e oferta.

**Status:** v0.4. A arquitetura está fechada e o MVP está em construção ([ROADMAP](ROADMAP.md)).

## Documentos

| Documento | Conteúdo |
|---|---|
| [ROADMAP.md](ROADMAP.md) | Roadmap único com corte de MVP (6 semanas) e indicadores do próprio sistema |
| [ARQUITETURA-NUCLEO.md](ARQUITETURA-NUCLEO.md) | Comum a todas as plataformas: estratégia (Camada 0), onboarding, perfil, brand kit, playbooks, conversão real, estatística, governança |
| [ARQUITETURA-META-ADS.md](ARQUITETURA-META-ADS.md) | Módulos específicos do Meta: estrutura de conta, Advantage+, destinos, módulo criativo |
| [ARQUITETURA-GOOGLE-ADS.md](ARQUITETURA-GOOGLE-ADS.md) | Módulos específicos do Google: palavras-chave, campanhas, RSA, negativas, landing pages, rastreamento |
| [docs/decisoes/](docs/decisoes/) | Registro de decisões de arquitetura (armazenamento, orquestração, painel, dados de clientes, briefing-trilha, autonomia) |
| [docs/integracoes/](docs/integracoes/) | Especificações: [Kommo](docs/integracoes/KOMMO.md) · [ClickUp](docs/integracoes/CLICKUP.md) · [outras](docs/integracoes/OUTRAS.md) |

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

# testes (só biblioteca padrão + pydantic + pyyaml)
python -m unittest discover -s tests -v
```

## Estrutura

```
trilha/            pacote Python (core, conversao, integracoes, plataformas)
tests/             testes e fixtures
playbooks/         padrões por segmento (imobiliário)
clientes/_exemplo/ modelo de cliente — clientes reais ficam no repositório privado (ADR-004)
docs/              decisões e integrações
```

Segredos: copie `.env.example` para `.env`. O `.env` nunca é versionado.
