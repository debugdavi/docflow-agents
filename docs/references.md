# Referências

Fontes consultadas em 10/11/2026 para o desenho do projeto. Páginas de documentação mudam; confirme na fonte antes de depender de um detalhe.

## Formato de skills e portabilidade

- [Agent Skills: visão geral](https://agentskills.io/home) e [especificação](https://agentskills.io/specification.md): estrutura de pasta, campos do frontmatter (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`), limites (nome até 64 caracteres, descrição até 1024), divulgação progressiva e recomendação de manter `SKILL.md` abaixo de 500 linhas.
- [GitHub Copilot: criar skills](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills) e [no Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-skills): diretórios `.github/skills`, `.claude/skills` e `.agents/skills`.
- [Cursor: Agent Skills](https://cursor.com/docs/skills.md) e [Rules](https://cursor.com/docs/context/rules): `.agents/skills`, `.cursor/skills` e compatibilidade com `.claude/skills`; `AGENTS.md` na raiz e em subpastas.
- [Gemini CLI: Agent Skills](https://geminicli.com/docs/cli/skills/): `.gemini/skills` e o alias interoperável `.agents/skills`.
- [Claude Code: skills](https://code.claude.com/docs/en/skills.md) e [subagentes](https://code.claude.com/docs/en/sub-agents.md): `.claude/skills`, campos adicionais do frontmatter, e quando preferir subagente a skill.
- [AGENT.md / AGENTS.md](https://github.com/agentmd/agent.md): arquivo de instruções para agentes, com arquivos aninhados e precedência do mais específico.
- Codex CLI e `.agents/skills`: [artigo secundário](https://codex.danielvaughan.com/2026/05/05/agent-skills-open-standard-portable-skills-codex-cli-cross-agent/). Não foi possível consultar a documentação primária; confirme na documentação da ferramenta.

## Escrita de PRs, commits e decisões

- [Google Engineering Practices: descrições de change list](https://google.github.io/eng-practices/review/developer/cl-descriptions.html): primeira linha que se sustenta sozinha e no imperativo; corpo com o problema e o porquê; revisar a descrição antes de enviar.
- [Graphite: boas práticas para descrições de PR](https://graphite.com/guides/github-pr-description-best-practices): o que muda, tickets relacionados, capturas de tela, como testar e notas sobre áreas de risco.
- [ADR templates](https://adr.github.io/adr-templates): formatos Nygard (título, status, contexto, decisão, consequências) e MADR.

## GitHub CLI

- [`gh release create`](https://cli.github.com/manual/gh_release_create): `--notes-file`, `--notes-from-tag`, `--generate-notes`, `--verify-tag`, `--target`, `--draft`, `--prerelease`, `--latest`.
- [`gh pr create`](https://cli.github.com/manual/gh_pr_create): `--title`, `--body-file`, `--base`, `--head`, `--draft`, `--label`, `--reviewer`, `--template`.
- Os flags usados nas skills foram conferidos também com `gh <comando> --help` (gh 2.89.0).

## Padrões adotados

- [Keep a Changelog 1.1.0](https://keepachangelog.com/pt-BR/1.1.0/)
- [Semantic Versioning 2.0.0](https://semver.org/lang/pt-BR/spec/v2.0.0.html)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/pt-br/v1.0.0/)
