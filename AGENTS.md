# AGENTS.md

Instruções para agentes de IA que trabalham **neste repositório** (DocFlow Agents). Para usar o fluxo em outro projeto, veja o [README](README.md).

## O que é este projeto

Um conjunto de skills no formato Agent Skills (`SKILL.md`) que automatiza a documentação de release: changelog, versão, README, PR e tag/Release no GitHub. As skills ficam em `.agents/skills/` e são a **fonte única**; outras pastas (`.claude/skills/`) são apenas links ou cópias geradas por `scripts/install.py`.

## Estrutura

- `.agents/skills/<nome>/SKILL.md`: uma skill por pasta. O nome da pasta é igual ao campo `name`.
- `.agents/skills/release-flow/scripts/`: scripts Python (só biblioteca padrão) que fazem a parte determinística.
- `docs/`: design, ADRs e referências. `examples/`: repositório de exemplo. `tests/`: testes.

## Como trabalhar

- Depois de mexer em qualquer skill ou script, rode:
  ```bash
  python scripts/validate_skills.py
  python -m unittest discover -s tests -v
  ```
- `SKILL.md` com no máximo 500 linhas; detalhes longos vão para `references/` (um nível de profundidade).
- A `description` de cada skill diz **o que faz e quando usar**, com as palavras que o usuário diria. É o que a ferramenta lê para decidir ativar a skill.
- Só os campos `name`, `description`, `license`, `compatibility`, `metadata` e `allowed-tools` no frontmatter, para manter a compatibilidade entre ferramentas.
- Scripts: só biblioteca padrão, Python 3.8+, e cada um com teste em `tests/` usando git real em repositório temporário.
- Mudou o comportamento de uma skill de forma relevante? Registre a decisão em `docs/adr/` e a mudança em `CHANGELOG.md`.

## Convenções

- Textos em português do Brasil com acentuação correta; nomes de arquivo e chaves de configuração sem acento.
- Commits no padrão Conventional Commits. Versões seguem SemVer; changelog segue Keep a Changelog.
- Nada de segredos em exemplos: use placeholders como `YOUR_API_KEY_HERE`.
- O fluxo nunca executa ações no remoto (push, PR, tag, release) sem confirmação explícita do usuário. Não enfraqueça essa regra nas skills.
