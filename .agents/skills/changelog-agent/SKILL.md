---
name: changelog-agent
description: Escreve e atualiza o CHANGELOG.md no padrão Keep a Changelog a partir dos commits desde a última tag, com cada item ligado ao commit ou PR que o originou para facilitar a rastreabilidade. Use sempre que o usuário falar em changelog, notas de versão, histórico de mudanças, "o que mudou desde a última versão", rastrear alterações por versão, ou quiser montar um changelog retroativo a partir das tags, mesmo sem pedir o changelog explicitamente.
compatibility: Requer git. O gh (GitHub CLI) é opcional e ajuda a achar o PR de cada commit. O script de apoio usa Python 3.8+.
metadata:
  version: "0.1.0"
---
# Changelog Agent

Transforma o histórico de commits em um changelog que responde a duas perguntas: **o que mudou em cada versão** e **onde está a mudança no código**. Por isso cada item termina com um link para o PR ou commit de origem: quem lê o changelog chega ao diff em um clique. Etapa 1 do fluxo `release-flow`; funciona também sozinho.

Este agente escreve sempre em `## [Unreleased]`. Número de versão e data são decisão do `version-agent`.

Regras que valem aqui (resumo de `release-flow/references/conventions.md`): Keep a Changelog 1.1.0, texto em pt-BR com acentuação, itens no presente começando pelo verbo, nunca inventar informação que não esteja nos commits ou PRs.

Se existir `.release-rules.md` na raiz, leia a seção "Changelog" e aplique (escopos em destaque, tipos a ignorar, padrão de ticket).

## Passos

1. **Coletar os commits.** Prefira o script, que lê o corpo completo dos commits e devolve JSON:
   ```bash
   python3 .agents/skills/release-flow/scripts/collect_commits.py
   ```
   Ajuste o caminho à sua instalação (`.claude/skills/...` ou `~/.agents/skills/...`). Sem o script, use o equivalente em git:
   ```bash
   ULTIMA_TAG=$(git describe --tags --abbrev=0 2>/dev/null || true)
   git log ${ULTIMA_TAG:+$ULTIMA_TAG..}HEAD --no-merges --format='%h %s%n%b---'
   ```
   O corpo (`%b`) é indispensável: `BREAKING CHANGE:` fica no rodapé do commit e `--oneline` o esconde. Sem tag, o intervalo é todo o histórico (primeira release).

2. **Classificar.** Os tipos do Conventional Commits cobrem só parte das seções; o resto se infere pelo conteúdo.

   | Commit | Seção | Observação |
   |---|---|---|
   | `feat` | Added | |
   | `fix` | Fixed | |
   | `perf` | Changed | |
   | `refactor` | Changed | só se mudar comportamento ou API visível; senão ignore |
   | `revert` | Removed ou Fixed | só se o revertido já saiu numa versão; senão ignore |
   | `docs` | Changed | só se alterar documentação pública relevante; senão ignore |
   | `build`, `ci`, `test`, `style`, `chore` | ignorar | exceto se afetar quem usa (dependência de runtime, correção de CVE → Security) |
   | texto fala em "deprecated" ou "descontinuado" | Deprecated | não é tipo oficial; infira pelo texto |
   | recurso removido | Removed | idem |
   | CVE, vulnerabilidade | Security | idem |

   Commit fora do padrão (`conventional: false`): classifique pelo texto se for evidente; se não, não chute, vá para a lista de ambíguos do passo 6.

3. **Marcar breaking changes.** Commit com `!` ou rodapé `BREAKING CHANGE:` vira item que começa com `**BREAKING:**` e termina com a migração ("Use `X` no lugar de `Y`"). Se o commit não diz como migrar, pergunte. O `version-agent` procura exatamente `**BREAKING:**`, então não varie a grafia.

4. **Redigir com rastreabilidade.** Agrupe commits da mesma entrega em um item e descreva o impacto para quem usa. Termine cada item com a referência:
   - PR conhecido: `([#42](https://github.com/dono/repo/pull/42))`. O número vem do `pr_hint` do script, do sufixo `(#42)` do commit de squash, ou de `gh pr list --state merged --search "<sha>" --json number,url --limit 1`.
   - Sem PR: ``([`a1b2c3d`](https://github.com/dono/repo/commit/SHA-COMPLETO))``.
   - Issues citadas no commit (`Closes #40`) entram junto: `([#42](URL-do-PR), fecha [#40](URL-da-issue))`.
   - Se o item agrupa vários commits, liste todas as referências.

   Se o escopo do commit for relevante (`auth`, `api`), use-o como prefixo em negrito: `- **auth:** Adiciona login com SSO.`

5. **Escrever em `[Unreleased]`.** Se `CHANGELOG.md` já tem itens em `[Unreleased]`, mescle e remova duplicatas. Nunca apague versões anteriores. Inclua só as seções que tiverem itens. Se o arquivo não existe, crie com o cabeçalho abaixo:
   ```markdown
   # Changelog

   Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

   O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
   e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

   ## [Unreleased]
   ```

6. **Sinalizar ambiguidades.** Commits que você não conseguiu classificar vão numa lista curta no fim da resposta, fora do arquivo, e também em `changelog.ambiguos` do contexto. O usuário decide.

7. **Registrar e passar adiante.** Se estiver no fluxo, preencha a seção `changelog` de `.release/context.yml` (arquivo, base, seções, `breaking`, ambíguos). O próximo passo é o `version-agent`.

## Modo retroativo (projeto sem changelog)

Para equipes que ainda não têm o hábito, gere o histórico a partir das tags existentes, da mais antiga para a mais nova:

```bash
git tag --sort=creatordate
python3 .agents/skills/release-flow/scripts/collect_commits.py --head v1.1.0   # base = tag anterior, automaticamente
```

Para cada tag, escreva `## [x.y.z] - AAAA-MM-DD` (data do commit da tag: `git log -1 --format=%ad --date=short <tag>^{commit}`) e termine com os links de comparação do rodapé. Sem tags, avise o usuário e sugira começar em `[Unreleased]`; o `github-release-agent` pode propor a primeira tag.

## Exemplo

Entrada (resumida):
```
a1b2c3d feat(auth): login com SSO (#42)
d4e5f6a fix(cpf): aceita CPF com pontuação
0f9e8d7 refactor: extrai função de validação
b7c8d9e feat(api)!: remove endpoint /v1/orders (#44)
        BREAKING CHANGE: use /v2/orders
```

Saída:
```markdown
## [Unreleased]

### Added
- **auth:** Adiciona login com SSO. ([#42](https://github.com/dono/repo/pull/42))

### Removed
- **BREAKING:** **api:** Remove o endpoint `/v1/orders`. Use `/v2/orders` no lugar. ([#44](https://github.com/dono/repo/pull/44))

### Fixed
- **cpf:** Corrige a validação para aceitar CPF com pontuação. ([`d4e5f6a`](https://github.com/dono/repo/commit/d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5))
```

O `refactor` foi ignorado: não muda comportamento visível. O `feat(api)!` entrou em Removed, não em Added, porque o que o usuário percebe é a remoção.

## Antes de entregar

Nenhuma seção vazia, nenhum item sem referência, breaking com `**BREAKING:**` e migração, nenhuma versão ou data inventada, estilo uniforme e acentuação correta.
