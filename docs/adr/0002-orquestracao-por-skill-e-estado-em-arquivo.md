# ADR 0002: Orquestração por skill e estado em arquivo

- **Status:** aceita
- **Data:** 2026-11-10

## Contexto

As etapas dependem umas das outras (a versão sai do changelog; o PR junta tudo; a tag só vale depois do merge) e é preciso parar em pontos de confirmação. Não há um mecanismo de orquestração comum a todas as ferramentas: algumas têm subagentes, outras não. Um orquestrador escrito para uma delas não serviria nas demais.

## Decisão

O orquestrador é também uma skill (`release-flow`) que instrui o agente a chamar as outras pelo mecanismo da ferramenta ou, na falta dele, a ler o `SKILL.md` correspondente. O estado entre as etapas fica em `.release/context.yml`, fora do git, com um contrato descrito em `references/context-contract.md`. Cada skill escreve só a própria seção.

## Consequências

- Funciona em qualquer ferramenta que leia skills, sem depender de subagentes.
- O estado sobrevive a troca de sessão ou de ferramenta, e qualquer pessoa vê onde o fluxo parou.
- A orquestração depende do modelo seguir as instruções; não há garantia mecânica da ordem. Os pontos de confirmação e o campo `etapa_atual` reduzem o risco, mas não o eliminam.
- Subagentes específicos (por exemplo um revisor final isolado no Claude Code) podem ser acrescentados depois como camada opcional, sem alterar o núcleo.
