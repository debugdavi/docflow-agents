# Convenções compartilhadas

Valem para todas as skills do fluxo. Cada skill repete o essencial no próprio texto, para continuar útil se for instalada sozinha.

## Padrões adotados

- [Keep a Changelog 1.1.0](https://keepachangelog.com/pt-BR/1.1.0/) para o `CHANGELOG.md`.
- [Semantic Versioning 2.0.0](https://semver.org/lang/pt-BR/spec/v2.0.0.html) para versões. A tag usa o prefixo `v` (`v1.3.0`); os manifestos usam a versão sem o `v`.
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/pt-br/v1.0.0/) como fonte de classificação dos commits.

## Idioma e estilo

- Textos gerados em **português do Brasil** com acentuação correta, salvo se `.release-rules.md` definir outro idioma. Termos universais ficam em inglês (build, deploy, endpoint, SDK). Chaves do contexto e nomes de arquivo não levam acento.
- Itens de changelog: frase curta, no presente, começando pelo verbo ("Adiciona…", "Corrige…", "Remove…"). Descreva o impacto para quem usa, não o nome do arquivo alterado.
- Datas no formato `AAAA-MM-DD`.

## Verdade e rastreabilidade

- A fonte da verdade é o repositório: commits, tags, manifestos, lockfiles, CI, ADRs. Nunca invente versão, biblioteca, comando, variável de ambiente, URL ou motivo de uma decisão. Sem evidência, pergunte ou marque como "a confirmar".
- Toda afirmação sobre o que mudou deve poder ser seguida até um commit ou PR. O changelog liga cada item a esse commit ou PR.

## Segurança

- Nenhum segredo em arquivo, PR ou release. Exemplos de configuração usam placeholders (`YOUR_API_KEY_HERE`).
- Não ponha tokens em URLs nem em argumentos de linha de comando.

## Uso do `gh` e do git

- **Leitura é livre:** `git log`, `git diff`, `gh repo view`, `gh pr view`, `gh pr list`, `gh release list`, `gh label list`.
- **Escrita no remoto exige confirmação explícita, uma por ação:** `git push`, `gh pr create`, `gh release create`, criação de tag. Mostre o comando exato e o conteúdo antes.
- A **tag é criada depois do merge**, a partir da branch de destino atualizada. Uma tag criada antes pode apontar para um commit que nunca chega à branch principal.
- Nunca use `--force`, nem apague tag, release ou branch sem pedido explícito.
- Para texto longo, grave em arquivo (`.release/pr-body.md`, `.release/release-notes.md`) e passe com `--body-file` / `--notes-file`, em vez de escapar aspas na linha de comando.

## Donos de arquivo

| Arquivo | Dono |
|---|---|
| `CHANGELOG.md` (itens em `[Unreleased]`) | `changelog-agent` |
| `CHANGELOG.md` (cabeçalho de versão e links), manifestos | `version-agent` |
| `README.md` | `readme-agent` |
| `.release/context.yml` | cada skill escreve só a própria seção |
| `.release/pr-body.md` | `github-pr-agent` |
| `.release/release-notes.md` | `github-release-agent` |
