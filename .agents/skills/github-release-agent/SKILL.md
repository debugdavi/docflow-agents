---
name: github-release-agent
description: Cria a tag anotada de versão e o GitHub Release com as notas extraídas do changelog, usando git e gh, depois que o PR de release foi mergeado; também ajuda equipes sem o hábito a começar a taguear (primeira tag, tags retroativas das versões antigas). Use quando o usuário pedir para taguear, criar tag, criar release, publicar versão, release notes no GitHub, ou "soltar a versão" depois do merge.
compatibility: Requer git e GitHub CLI (gh) autenticado com gh auth login e permissão de escrita no repositório. O script de apoio usa Python 3.8+.
metadata:
  version: "0.1.0"
---
# GitHub Release Agent

Transforma uma versão decidida e mergeada em **tag anotada + GitHub Release**, e ajuda a criar o hábito de taguear quando o time ainda não tem. Uma tag é o marco que liga um número de versão a um commit exato: sem ela, "a versão 1.3.0" não aponta para nada no código. Etapa 5 do fluxo `release-flow`; funciona também sozinho.

**A tag nasce depois do merge**, a partir da branch de destino atualizada. Uma tag criada antes pode apontar para um commit que nunca chega à branch principal, e uma Release publicada com changelog ainda não revisado é difícil de desfazer.

Resumo das regras que valem aqui: tag `vX.Y.Z` anotada; notas só da versão atual (nunca o `CHANGELOG.md` inteiro); nenhuma ação no remoto sem confirmação explícita; nunca `--force`.

Se existir `.release-rules.md`, leia a seção "Tag e release".

## Passos

1. **Verificações antes de qualquer coisa.** Se alguma falhar, pare e diga qual; não tente contornar.
   ```bash
   gh auth status
   git fetch --tags origin
   git branch --show-current                      # deve ser a branch de destino (ex.: main)
   git status -sb                                 # sem alterações e sem atraso em relação ao remoto
   gh pr view <número> --json state,mergedAt,mergeCommit   # estado MERGED (no fluxo de release)
   git ls-remote --tags origin vX.Y.Z             # vazio: a tag ainda não existe
   gh release view vX.Y.Z                         # erro "release not found": ainda não existe
   ```
   Também confira que a versão dos manifestos é a da tag (sem o `v`) e que `CHANGELOG.md` tem a seção `## [X.Y.Z]` datada. Se a branch atual não é a de destino ou está desatualizada, ofereça `git switch <destino> && git pull`.

2. **Montar as notas.** Extraia a seção da versão:
   ```bash
   python3 .agents/skills/release-flow/scripts/extract_release_notes.py CHANGELOG.md X.Y.Z > .release/release-notes.md
   ```
   (ajuste o caminho; sem o script, copie a seção `## [X.Y.Z]` até a próxima `## [`, sem as linhas de link de rodapé). Se houver breaking changes, comece o arquivo com um aviso curto para quem vai fazer o deploy e acrescente no fim o link de comparação: `**Comparação completa:** https://github.com/dono/repo/compare/vANTERIOR...vX.Y.Z`.

3. **Montar a especificação** e mostrar ao usuário:
   - **Tag:** `vX.Y.Z`, anotada, no commit atual de `<destino>` (mostre o hash curto).
   - **Mensagem da tag:** uma linha (ex.: `v1.3.0: login com SSO e correções de CPF`).
   - **Título da Release:** `vX.Y.Z - <foco da versão em poucas palavras>`.
   - **Pré-lançamento:** sim, se a versão tem sufixo (`-rc.1`, `-beta.1`).
   - **Notas:** o conteúdo de `.release/release-notes.md`.
   - **Anexos:** só se o usuário ou as regras pedirem.

4. **Confirmar e executar.** Pergunte: "Posso criar a tag vX.Y.Z em `<hash>` e publicar a Release?". Com o "sim":
   ```bash
   git tag -a vX.Y.Z -m "<mensagem da tag>"
   git push origin vX.Y.Z
   gh release create vX.Y.Z --verify-tag --title "<título>" --notes-file .release/release-notes.md [--prerelease] [--draft]
   ```
   - Empurre **só** a tag criada (`git push origin vX.Y.Z`), nunca `git push --tags`, que envia todas as tags locais.
   - `--verify-tag` aborta se a tag não estiver no remoto, o que evita o `gh` criar uma tag sozinho em outro commit.
   - `--draft` cria um rascunho para o usuário conferir na interface do GitHub antes de publicar. Ofereça quando ele quiser revisar o resultado.
   - Sem permissão para empurrar tags, mas com permissão de release, uma alternativa é `gh release create vX.Y.Z --target <hash completo> ...`, que cria a tag no servidor. Diga ao usuário que ela será leve (sem anotação) e peça confirmação.

5. **Conferir.** `gh release view vX.Y.Z --json url,tagName,isPrerelease,isDraft`. Informe a URL. Preencha a seção `release` de `.release/context.yml`.

## Começando a taguear (equipes sem o hábito)

- **Nenhuma tag existe** (`git tag` vazio): explique em duas linhas o que a tag faz e proponha a primeira. Se há versão nos manifestos, sugira tagueá-la no commit que a introduziu; senão, no commit atual, com a versão que o `version-agent` decidir (`v0.1.0` ou `v1.0.0`).
- **Tags retroativas.** Para versões que já saíram sem tag, procure o commit em que a versão foi alterada:
  ```bash
  git log --format='%h %ad %s' --date=short -S'"version": "1.2.0"' -- package.json
  ```
  (ajuste o manifesto e a versão). Monte uma tabela versão → commit → data e **mostre ao usuário**: ele confirma cada linha, porque a associação é uma inferência. Só depois crie as tags anotadas, na ordem cronológica, e empurre uma a uma.
- **Release sem tag anterior:** a primeira Release não tem link de comparação; use o link da própria tag.

## Cuidados

- Nunca recrie nem mova uma tag já publicada: quem a usou perde a referência. Se a tag está errada, explique as opções ao usuário e deixe a decisão com ele.
- Não apague tags, releases ou branches sem pedido explícito.
- Sem `gh` autenticado, entregue os arquivos (`.release/release-notes.md`) e a lista de comandos para o usuário rodar.
