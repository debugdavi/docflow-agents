# ADR 0001: Skills no formato aberto Agent Skills, em `.agents/skills/`

- **Status:** aceita
- **Data:** 2026-11-10

## Contexto

O fluxo precisa funcionar em várias ferramentas de IA. Cada uma tem arquivos próprios (regras do Cursor, instruções do Copilot, `GEMINI.md`, `CLAUDE.md`), e escrever o mesmo conteúdo em todos geraria divergência. Ao mesmo tempo, várias ferramentas passaram a ler skills no formato `SKILL.md`, e a pasta `.agents/skills/` aparece como caminho comum em Copilot, Cursor e Gemini CLI. O Claude Code lê `.claude/skills/`.

## Decisão

Escrever todo o conteúdo como skills no formato Agent Skills (`SKILL.md` com frontmatter `name` e `description`), guardadas em `.agents/skills/`. Usar apenas os campos do frontmatter definidos pela especificação. Um instalador cria o link (ou cópia) em `.claude/skills/` para o Claude Code. Um `AGENTS.md` na raiz descreve o projeto, e `CLAUDE.md`, `GEMINI.md` e `.github/copilot-instructions.md` apontam para ele.

## Consequências

- Uma fonte única para todas as ferramentas; adicionar uma ferramenta nova costuma ser copiar a pasta.
- Campos específicos de uma ferramenta (por exemplo `disable-model-invocation` do Claude Code e do Cursor) ficam de fora, para o validador poder checar a especificação estritamente. A proteção contra ações indevidas está no texto das skills (confirmações), não em configuração da ferramenta.
- O Claude Code depende do link em `.claude/skills/`. Em sistemas sem suporte a links o instalador faz cópia, que pode ficar desatualizada; rodar o instalador de novo com `--force` resolve.
- A compatibilidade foi verificada na documentação de cada ferramenta e pode mudar com o tempo.
