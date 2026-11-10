---
name: release-flow
description: Orquestra o fluxo de documentação de release de ponta a ponta (changelog Keep a Changelog, versão SemVer, README, Pull Request e tag/Release no GitHub via gh), passando o estado entre as etapas e parando nas confirmações humanas. Use quando o usuário pedir para preparar ou fazer uma release, soltar uma versão, versionar o projeto, documentar uma entrega ou rodar o fluxo completo (changelog + versão + README + PR + tag), em vez de uma etapa isolada.
compatibility: Requer git e GitHub CLI (gh) autenticado com gh auth login. Os scripts opcionais usam Python 3.8+.
metadata:
  version: "0.1.0"
---
# Release Flow (orquestrador)

Coordena as skills do fluxo e cuida da sequência, do estado compartilhado e das confirmações. Não escreve changelog, versão, README nem PR: cada etapa pertence a uma skill especializada. O orquestrador existe porque as etapas dependem umas das outras (a versão sai do changelog, o PR junta tudo, a tag só vale depois do merge) e alguém precisa garantir a ordem e parar nos pontos em que um erro sairia caro.

Convenções comuns a todas as etapas: [references/conventions.md](references/conventions.md). Formato do estado compartilhado: [references/context-contract.md](references/context-contract.md).

## Etapas

| # | Skill | Entrega | Quem edita |
|---|---|---|---|
| 1 | `changelog-agent` | itens rastreáveis em `## [Unreleased]` | `CHANGELOG.md` (itens) |
| 2 | `version-agent` | versão nova decidida, changelog datado, manifestos | `CHANGELOG.md` (cabeçalho, links), manifestos |
| 3 | `readme-agent` | README fiel ao projeto, ou "sem mudanças" | `README.md` |
| 4 | `github-pr-agent` | Pull Request descrito para o revisor | nenhum arquivo do projeto |
| 5 | `github-release-agent` | tag anotada e GitHub Release (**só depois do merge**) | nenhum arquivo do projeto |

Cada arquivo do projeto tem um único dono. Se uma etapa achar que algo de outra está errado, registra em `pendencias` no contexto e devolve a decisão, sem corrigir por conta própria.

## Antes de começar

1. Confirme que está num repositório git e rode `git status --porcelain`. Se houver alterações não commitadas, pergunte se deve seguir mesmo assim.
2. Rode `gh auth status`. Sem `gh` instalado ou autenticado, o fluxo continua só até produzir os textos e comandos para o usuário executar, e você avisa isso logo no início.
3. Descubra repositório e branch padrão: `gh repo view --json nameWithOwner,url,defaultBranchRef`.
4. Leia `.release-rules.md` na raiz, se existir (regras do usuário). Modelo: [assets/release-rules.example.md](assets/release-rules.example.md). Ele refina as etapas, e cada etapa o lê por conta própria.
5. Crie `.release/context.yml` com a seção de topo (projeto, repositório, branches, data). Garanta que `.release/` está no `.gitignore`: é estado de trabalho e não deve ir para o repositório.

## Como chamar cada skill

Cada ferramenta ativa skills de um jeito (comando de barra, menção, ativação automática pela descrição). Use o mecanismo da sua ferramenta. Se ela não tiver um, abra `.agents/skills/<nome>/SKILL.md` e siga as instruções como se fossem suas. O resultado é o mesmo, porque o conteúdo da skill é o que importa.

## Fluxo

1. **changelog-agent.** Se `[Unreleased]` ficar vazio, pare: não há o que lançar. Commits ambíguos vão para o usuário decidir antes de seguir.
2. **version-agent.** **Pare e peça confirmação da versão.** Todas as etapas seguintes herdam esse número. Com a confirmação, ofereça criar a branch `release/vX.Y.Z` a partir da branch padrão (ou o prefixo definido nas regras do usuário), caso o trabalho ainda não esteja numa branch própria.
3. **readme-agent.** Roda em toda release, inclusive PATCH, porque é ele quem decide se algo precisa mudar.
4. **Commit e PR.** Mostre os arquivos alterados, proponha a mensagem `chore(release): vX.Y.Z` e, com a confirmação do usuário, faça o commit. Depois chame **github-pr-agent** em modo release, que pede nova confirmação antes de `git push` e `gh pr create`.
5. **Merge.** É do humano (ou do processo de revisão do time). O orquestrador espera. Quando o usuário avisar que o merge foi feito, confira com `gh pr view <número> --json state,mergedAt,mergeCommit`.
6. **github-release-agent.** Só com o PR em estado `MERGED`. Cria a tag anotada e o GitHub Release com confirmação.

## Modos

- **Completo** (padrão): etapas 1 a 4, pausa no merge, depois a 5.
- **A partir de uma etapa**: "refaça a partir do README". Releia o contexto e reexecute daí em diante.
- **Rascunho**: nada é gravado nem enviado; cada etapa mostra o que faria. Útil para conhecer o fluxo ou ensaiar uma release.
- **Etapa isolada**: se o usuário pediu só uma coisa ("qual a próxima versão?"), chame só a skill dela, sem acionar o resto.

## Falhas e correções

- Cada etapa termina com `status: ok` ou `status: blocked` (com a dúvida em `pendencias`). Em `blocked`, mostre a dúvida, resolva e reexecute **só aquela etapa**.
- Se a versão mudar depois da etapa 2, reexecute 3, 4 e 5. Se o changelog mudar, reexecute 2 em diante.
- Nunca pule etapas nem reordene: cada uma consome o resultado da anterior.
- Erro do `gh` (permissão, rede, repositório sem remoto): mostre a mensagem como veio, não repita às cegas e ofereça os comandos para o usuário rodar manualmente.

## Fechamento

Termine com um resumo curto: versão decidida, arquivos alterados, link do PR (e da Release, se já criada) e o que falta, na ordem. Não recapitule os passos internos.
