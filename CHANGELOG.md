# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-10

### Added

- Seis skills de documentação de release no formato Agent Skills: `release-flow` (orquestrador), `changelog-agent`, `version-agent`, `readme-agent`, `github-pr-agent` e `github-release-agent`. ([`5326c7f`](https://github.com/debugdavi/docflow-agents/commit/5326c7fa964304a51758187c7aac7e60f470a7bb), [`c34781c`](https://github.com/debugdavi/docflow-agents/commit/c34781c6c9f0cdd0333e64a4fa27fee7a056b28b))
- Scripts determinísticos de apoio ao `release-flow`: `collect_commits.py`, `branch_facts.py` e `extract_release_notes.py`. ([`eab0eca`](https://github.com/debugdavi/docflow-agents/commit/eab0ecad3f802978b7e675040694cb59969f4842))
- Instalador `scripts/install.py` (cria links relativos ou cópias, conforme o sistema) e validador `scripts/validate_skills.py` contra a especificação Agent Skills. ([`938b1c2`](https://github.com/debugdavi/docflow-agents/commit/938b1c216b0795b9b0a1c66135e85960420db2a9))
- Repositório de exemplo e walkthrough executável em `examples/`. ([`61f0b95`](https://github.com/debugdavi/docflow-agents/commit/61f0b9587c93bc90ac207b33f0099945568baca7))
- Documentação de design, referências e ADRs 0001–0005 em `docs/`. ([`3a55192`](https://github.com/debugdavi/docflow-agents/commit/3a551923bdf9288555a61f14efb22ecb3424c3f2), [`97a3d1a`](https://github.com/debugdavi/docflow-agents/commit/97a3d1a28f5c96bb51b2eab9678885d0938bfcba))
- Arquivos de entrada para agentes de IA (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) e instruções para o GitHub Copilot. ([`cbb9bf5`](https://github.com/debugdavi/docflow-agents/commit/cbb9bf5a4845f664ae574f02b62cc4578c26aed6))

[Unreleased]: https://github.com/debugdavi/docflow-agents/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/debugdavi/docflow-agents/releases/tag/v0.1.0
