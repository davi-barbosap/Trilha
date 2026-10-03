# Trilha

Sistema que executa o trabalho manual por trás dos serviços de mídia paga (Meta Ads e Google Ads) da Trilha, para que o assessor de marketing gaste o tempo dele pensando, decidindo e cuidando do cliente.

## O que é

Um assessor que atende vários clientes passa boa parte da semana em tarefas braçais: abrir o Gerenciador de Anúncios e o Google Ads, copiar números, conferir no Kommo quantos leads realmente viraram oportunidade, montar planilhas, comparar com a meta, levantar dados para o briefing e preparar a reunião do mês.

O Trilha faz esse trabalho. Ele **não pensa a estratégia, não decide verba e não fala com o cliente** — isso é do assessor.

## O que faz na prática

**Todos os dias, sozinho**
- **Devolve a venda real para o Meta e o Google.** Quando o lead muda de etapa no Kommo (qualificado, visita, venda), o sistema avisa as plataformas. Assim elas aprendem a buscar gente parecida com quem compra, não só com quem clica.
- **Coleta e confere os números** de Meta, Google e Kommo, e acompanha se a verba do mês vai sobrar ou faltar.
- **Avisa só o que é urgente:** anúncio reprovado, campanha parada, rastreamento quebrado.
- **Freio de emergência:** se uma campanha está gastando sem trazer nenhum lead, ou com o rastreamento quebrado, pausa e avisa na hora, com um botão para desfazer. É a única coisa que o sistema faz sem pedir. Reativar é sempre decisão do assessor.

**Na véspera de cada compromisso do assessor, deixa o material pronto no ClickUp**

| Compromisso do assessor | O que o sistema deixa pronto |
|---|---|
| Otimização semanal de cada cliente | **Dossiê:** resultado da semana pelo Kommo, o que mudou na conta, o efeito das decisões da semana anterior e os pontos de atenção com os números de cada um |
| Relatório semanal ao cliente | **Números em três blocos** — leads, criativos e ações — para o assessor escrever a leitura dele e entregar |
| Briefing para a equipe de criação | **Pacote de dados:** o que está convertendo, o que cansou, objeções e motivos de perda registrados no Kommo |
| Reunião mensal com o cliente | **Pacote da reunião:** resultado do mês contra a meta, testes, decisões e efeitos |
| Reunião de equipe | **Painel da carteira:** situação de cada cliente, freios acionados, pendências |

**O que continua sendo do assessor:** estratégia, decisões de verba e criativo, criação de campanhas, contatos proativos com o cliente, respostas no grupo, a leitura dos relatórios e a condução das reuniões.

**O que fica fora deste sistema** (ferramentas paralelas): landing pages, disparos em massa, fluxos de CRM, BotConversa, GA4/GTM e a captura de tarefas no ClickUp. Ver [ecossistema](docs/ecossistema.md).

## Resultado esperado

Cerca de **3,75 h de trabalho do assessor por cliente por semana**, contra ~7,6 h sem o sistema. Isso permite atender **~10 clientes por assessor** sem perder a qualidade do relacionamento ([modelo operacional](docs/modelo-operacional.md) §5).

## Situação atual

A base de código está pronta e testada: ficha validada de cada cliente, cálculo de metas, conversão real para Meta e Google, regras do freio e a API que o n8n chama. Para entrar em operação falta subir o servidor autohospedado do n8n e montar os fluxos de cada material, na ordem descrita no [roadmap](docs/roadmap.md).

## Documentação

| Documento | Conteúdo |
|---|---|
| [docs/ecossistema.md](docs/ecossistema.md) | O que é do sistema, do assessor e das ferramentas paralelas — e o que as paralelas precisam entregar |
| [docs/modelo-operacional.md](docs/modelo-operacional.md) | O cargo de assessor item por item, o material de cada compromisso, capacidade, freio |
| [docs/roadmap.md](docs/roadmap.md) | O que está pronto e o que falta para entrar em operação |
| [docs/arquitetura/](docs/arquitetura/) | Núcleo, Meta Ads e Google Ads |
| [docs/integracoes/](docs/integracoes/) | n8n, Kommo, ClickUp e demais ferramentas |
| [docs/decisoes/](docs/decisoes/) | Decisões de arquitetura |

## Uso técnico

```bash
pip install -e .

python -m trilha validar clientes/_exemplo/perfil.yaml      # confere a ficha de um cliente
python -m trilha calcular clientes/_exemplo/perfil.yaml     # CAC, CPL máximos e verba por etapa
python -m trilha simular-webhook tests/fixtures/kommo_webhook.txt \
  --perfil clientes/_exemplo/perfil.yaml \
  --lead tests/fixtures/kommo_lead.json --contato tests/fixtures/kommo_contato.json   # o que seria enviado, sem enviar
python -m trilha servir --porta 8080                        # API chamada pelo n8n (exige TRILHA_API_TOKEN)

python -m unittest discover -s tests -v
```

## Estrutura

```
trilha/            código (API, CLI, regras, integrações)
tests/             testes
docs/              documentação
n8n/modelos/       fluxos-modelo do n8n
infra/             servidor: Docker, n8n, Postgres, Redis, HTTPS, backup
playbooks/         padrões por segmento (imobiliário)
clientes/_exemplo/ ficha de cliente de exemplo — clientes reais ficam em repositório privado
```

Segredos: copiar `.env.example` para `.env` (uso local) ou `infra/.env.example` e `infra/kommo.env.example` (servidor). Nenhum `.env` é versionado.
