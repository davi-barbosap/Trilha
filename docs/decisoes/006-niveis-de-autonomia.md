# ADR-006 — Níveis de autonomia

**Status:** aceita · 2026-10-03

## Contexto
A v0.3 exigia aprovação humana para toda escrita. Com 10+ clientes isso vira gargalo, e ações óbvias (negativar "vagas de emprego", pausar anúncio sem lead após gastar 2× o CPL máximo) esperam dias.

## Decisão
Níveis L0 (lê) · L1 (sugere, humano aprova — padrão) · L2 (aplica dentro de limites e avisa) · L3 (nunca automático), definidos por cliente e por tipo de ação no `perfil.yaml` (`autonomia`). Detalhes no núcleo §10. L2 só é liberado para um tipo de ação depois de 30 dias de sugestões daquele tipo aprovadas sem alteração.

## Consequências
Toda ação L2 é registrada, reversível e aparece no relatório do dia. O esquema do perfil rejeita L2 para ações da lista L3 (aumento de verba acima do teto, promessa ao consumidor).
