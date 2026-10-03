# ADR-005 — Dependência do briefing-trilha

**Status:** proposta — precisa do acordo da responsável pelo repositório `beatriz-moraes082/briefing-trilha`

## Contexto
O wizard de onboarding (Streamlit), o `build_kommo_json.py`, os textos de objeções/apelos e o playbook imobiliário vêm do `briefing-trilha`, um repositório de outra pessoa. Sem regra, uma mudança lá quebra o onboarding aqui sem aviso.

## Decisão proposta
1. **Contrato de dados, não de código:** o wizard produz `perfil.yaml`, `marca.yaml` e `ofertas/*.yaml`; o Trilha valida com `python -m trilha validar`. Qualquer mudança de formato passa pelo esquema em `trilha/core/perfil.py`.
2. **Versão fixada:** o Trilha consome o `briefing-trilha` por tag de versão (submódulo Git ou pacote), nunca pela branch principal.
3. **Conteúdo de playbook** (objeções, apelos, fluxos) é copiado para `playbooks/imobiliario/` com referência à versão de origem; atualizações são deliberadas.
4. **Responsáveis:** definir quem mantém o wizard e como as etapas de mídia (núcleo §4.2) entram lá — preferência por contribuição no próprio `briefing-trilha`.

## Consequências
Enquanto não houver acordo, o onboarding de mídia roda pelo `clientes/_exemplo/` preenchido à mão e validado pelo CLI.
