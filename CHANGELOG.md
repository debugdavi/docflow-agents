# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-10

### Added
- Skill `release-flow`, que orquestra o fluxo de release e guarda o estado em `.release/context.yml`.
- Skill `changelog-agent`: changelog Keep a Changelog com itens ligados ao PR ou commit de origem e modo retroativo a partir das tags.
- Skill `version-agent`: decisão de MAJOR, MINOR ou PATCH a partir da análise da branch e de regras do usuário, com confirmação antes de editar.
- Skill `readme-agent`: README com stack, área do projeto, versões, requisitos e decisões técnicas com fonte.
- Skill `github-pr-agent`: descrição de PR para o revisor (modos funcionalidade e release), aberta com `gh` após confirmação.
- Skill `github-release-agent`: tag anotada e GitHub Release com `gh` depois do merge, além de apoio para começar a taguear.
- Scripts `collect_commits.py`, `branch_facts.py` e `extract_release_notes.py`, com testes.
- Instalador `scripts/install.py` (links ou cópia) e validador `scripts/validate_skills.py` contra a especificação Agent Skills.
- Exemplo executável em `examples/` e documentação de design em `docs/`.
- Arquivos de entrada para `AGENTS.md`, Claude Code, Gemini CLI e GitHub Copilot.

[Unreleased]: https://github.com/debugdavi/docflow-agents/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/debugdavi/docflow-agents/releases/tag/v0.1.0
