# ADR-008 — Funil padrão único e perda classificada por etapa e motivo

**Status:** aceita

## Contexto
O diferencial da Trilha é enxergar o meio do funil: velocidade do primeiro contato, cadência, passagem do atendimento para a qualificação, comparecimento e critério de qualificação. Com só quatro etapas (lead, qualificado, agendamento, venda) e toda perda tratada como "lead ruim", o sistema não conseguia mostrar onde está o gargalo nem separar o que é do marketing e o que é do comercial.

## Decisão
- **Um funil padrão para todos os segmentos:** `lead → em_atendimento → lead_qualificado → agendamento → comparecimento → proposta → venda`, mais `perdido`. O playbook do segmento muda só os nomes exibidos e as referências de conversão; sem playbook próprio, vale `playbooks/padrao/`.
- **Perda classificada** por categoria do motivo (lead, atendimento, comercial, externo) e pelo momento (antes ou depois da qualificação). Motivos de perda são obrigatórios no Kommo, com a lista padrão do playbook.
- **Resultado é venda e valor vendido** (VGV no imobiliário); CPL é diagnóstico.
- **Atribuição de vendas pelo Kommo** (UTMs do lead), independente da janela das plataformas.
- **Raio-x do funil** (`trilha/core/funil.py`) entra no dossiê, no relatório semanal, no pacote da reunião e no painel da carteira, com marketing entregou × comercial converteu separados.

## Consequências
- Todo cliente precisa do funil padrão e dos motivos de perda configurados no Kommo ([raio-x do funil](../raio-x-do-funil.md), contrato).
- A etapa 143 do Kommo é sempre `perdido`; a leitura (lead ruim, atendimento, comercial, externo) vem da categoria do motivo e do momento da perda.
- O sistema mede o time comercial do cliente; o contato do assessor com o cliente continua fora.
