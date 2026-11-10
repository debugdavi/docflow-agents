# Passo a passo: uma release do `tasks-api`

Este exemplo percorre o fluxo inteiro num projeto fictício. Para reproduzir:

```bash
python examples/make_sample_repo.py /tmp/tasks-api
cd /tmp/tasks-api
```

O script cria um repositório com autor e datas fixos, então os hashes abaixo são os mesmos na sua máquina. O remote `origin` aponta para `git@github.com:acme/tasks-api.git` (fictício; nada é enviado).

> **O que é real e o que é ilustrativo.** Os comandos e as saídas dos scripts (aqui resumidas ou formatadas para caber) foram executados de verdade sobre esse repositório. Os textos de changelog, veredito de versão, README e PR são o que um agente produz seguindo as skills; servem de referência de formato e de nível de detalhe, e o texto exato varia de uma execução para outra.

## Ponto de partida

O projeto está na tag `v1.2.0` e nunca teve changelog. Desde então há 8 commits:

```text
8cdfd20 ci: cacheia dependências
6fa8ac6 docs: corrige link do README
1c2d86a chore(deps): atualiza express para 5.0 (#16)
a493d4e feat(api)!: remove endpoint GET /v1/tasks (#15)
467cad3 feat(auth): aceita autenticação opcional por JWT (#14)
1e31da7 refactor: extrai validação para módulo próprio
f557e21 fix(tasks): corrige paginação que repetia itens (#13)
c2c05df feat(tasks): adiciona filtro por status (#12)
```

Pedido ao agente: *"prepare a release"* (skill `release-flow`).

## Etapa 1: changelog-agent

O script lê os commits desde a última tag, inclusive o corpo, onde fica o `BREAKING CHANGE:`:

```bash
python3 .agents/skills/release-flow/scripts/collect_commits.py --no-files
```

Resumo do JSON devolvido:

```text
range:   base=v1.2.0  head=HEAD  first_release=false
repo:    https://github.com/acme/tasks-api
summary: total=8  breaking=1  non_conventional=0
         by_type: chore 1, ci 1, docs 1, feat 3, fix 1, refactor 1
```

Decisões do agente: `docs`, `ci` e `refactor` ficam de fora (não mudam nada para quem usa). `chore(deps)` entra, porque trocar o Express de major afeta o runtime. O `feat(api)!` vai para **Removed**, e não para Added, porque o que o usuário percebe é a remoção. Como o projeto não tinha `CHANGELOG.md`, o agente cria o arquivo com o cabeçalho padrão e escreve em `[Unreleased]`:

```markdown
## [Unreleased]

### Added
- **tasks:** Adiciona filtro de tarefas por status. ([#12](https://github.com/acme/tasks-api/pull/12))
- **auth:** Aceita autenticação opcional por JWT. Exige a variável `JWT_SECRET` e aplica a migration `002_add_user_id`. ([#14](https://github.com/acme/tasks-api/pull/14))

### Changed
- Atualiza o Express para a versão 5. ([#16](https://github.com/acme/tasks-api/pull/16))

### Removed
- **BREAKING:** **api:** Remove o endpoint `GET /v1/tasks`. Use `GET /v2/tasks`, que agora devolve a resposta paginada. ([#15](https://github.com/acme/tasks-api/pull/15))

### Fixed
- **tasks:** Corrige a paginação, que repetia itens entre páginas. ([#13](https://github.com/acme/tasks-api/pull/13))
```

Cada item termina com o PR de origem: é a rastreabilidade que permite ir do changelog ao diff.

## Etapa 2: version-agent

O agente não se limita ao texto do changelog. Ele levanta fatos da branch:

```bash
python3 .agents/skills/release-flow/scripts/branch_facts.py
```

Trechos relevantes do JSON:

```json
"breaking_commits": [
  { "short": "a493d4e", "subject": "feat(api)!: remove endpoint GET /v1/tasks (#15)",
    "note": "use GET /v2/tasks, que agora devolve a resposta paginada." }
],
"removed_files": ["src/routes/v1/tasks.js"],
"dependency_changes": { "package.json": { "dependencies": {
  "added":   { "jsonwebtoken": "^9.0.2" },
  "changed": { "express": { "from": "^4.18.0", "to": "^5.0.0" } } } } },
"hints": [
  "1 commit(s) marcados como breaking change.",
  "Migrations/SQL alterados: verifique compatibilidade de dados e plano de rollback.",
  "1 arquivo(s) de código removidos: possível remoção de API pública.",
  "Arquivos de configuração/ambiente alterados: procure variáveis novas ou renomeadas.",
  "package.json: express mudou de major (4 -> 5)."
]
```

Veredito apresentado ao usuário:

> **Proposta: `1.2.0` → `2.0.0` (MAJOR), tag `v2.0.0`.**
> - Changelog: item `**BREAKING:**` removendo `GET /v1/tasks` (#15).
> - Branch: `src/routes/v1/tasks.js` foi removido, o que confirma a remoção de uma rota pública.
> - Também mudaram: Express 4 → 5 (major) e uma migration que só adiciona coluna (não é, por si, incompatível).
>
> Confirma a versão 2.0.0?

Depois do "sim", o agente renomeia `[Unreleased]` para `## [2.0.0] - 2026-11-10`, cria um `[Unreleased]` vazio acima, acrescenta os links de comparação no rodapé e roda `npm version 2.0.0 --no-git-tag-version` para atualizar `package.json`.

## Etapa 3: readme-agent

O agente lê o `package.json` (Node `>=20`, Express 5, jsonwebtoken), o `.env.example` (nova variável `JWT_SECRET`) e procura o porquê de cada escolha. Para o JWT, o `git log -S'"jsonwebtoken"' -- package.json` aponta o commit `467cad3`, cujo corpo traz a justificativa. Para o Express 5, o corpo do commit do PR #16 também. Já o Express como framework original não tem registro em lugar nenhum, então o README diz "a confirmar" e o agente pergunta ao usuário no fim.

Trecho do README produzido:

```markdown
**Área:** Back-end

## Stack e SDKs

| Categoria | Tecnologia | Versão | Papel |
|---|---|---|---|
| Runtime | Node.js | >= 20 | execução da API |
| Framework | Express | ^5.0.0 (declarada) | servidor HTTP |
| Autenticação | jsonwebtoken | ^9.0.2 (declarada) | validação de tokens JWT |

## Decisões técnicas

| Escolha | Por quê | Fonte |
|---|---|---|
| Autenticação por JWT | Mantém a API sem estado e permite escalar horizontalmente | `467cad3` (#14) |
| Express 5 | Trata erros de rotas assíncronas nativamente | #16 |
| Express como framework HTTP | a confirmar | — |

## Configuração

| Variável | Obrigatória | Descrição | Exemplo |
|---|---|---|---|
| `PORT` | não | porta do servidor | `3000` |
| `JWT_SECRET` | para validar tokens | segredo de assinatura dos JWT | `YOUR_JWT_SECRET_HERE` |
```

O contexto da etapa registra `novas_variaveis_env: [JWT_SECRET]` e `novos_sdks_libs: ["jsonwebtoken ^9.0.2"]`, que o PR vai usar.

## Etapa 4: github-pr-agent (modo release)

Depois de commitar com `chore(release): v2.0.0` na branch `release/v2.0.0`, o agente monta o corpo (resumido aqui) em `.release/pr-body.md`:

```markdown
## Resumo
Libera a v2.0.0: filtro de tarefas por status, autenticação opcional por JWT e Express 5.
Remove o endpoint `GET /v1/tasks`, o que exige migração dos clientes.

## Versão
| | |
|---|---|
| Anterior → nova | `1.2.0` → `2.0.0` |
| Tipo do bump | `MAJOR` |
| Por quê | `**BREAKING:**` no changelog (#15) e remoção de `src/routes/v1/tasks.js` na branch |

## Atenção antes de aprovar
- **Breaking changes:** `GET /v1/tasks` removido. Clientes devem usar `GET /v2/tasks` (resposta paginada).
- **Variáveis de ambiente novas:** `JWT_SECRET`, para validar tokens JWT.
- **Bibliotecas novas:** `jsonwebtoken ^9.0.2`; `express` de `^4.18.0` para `^5.0.0`.
- **Migrations:** `db/migrations/002_add_user_id.sql` adiciona a coluna `user_id` em `tasks`.

## Por onde começar a revisão
1. `src/routes/v1/tasks.js` (removido): confirme que nenhum cliente interno ainda o usa.
2. `db/migrations/002_add_user_id.sql`: confirme o plano de rollback antes do deploy.
3. `package.json`: versão `2.0.0` e salto de major do Express.
4. `CHANGELOG.md`: cada item corresponde a uma mudança real e o breaking traz a migração.
```

Título: `chore(release): v2.0.0`. O agente mostra tudo e pergunta *"Posso fazer o push e abrir o PR?"*. Com o "sim":

```bash
git push -u origin HEAD
gh pr create --base main --head release/v2.0.0 --title "chore(release): v2.0.0" --body-file .release/pr-body.md
```

## Merge e etapa 5: github-release-agent

O merge é do time. Quando o usuário avisa, o agente confere o estado do PR (`gh pr view 57 --json state,mergedAt,mergeCommit`), muda para a `main` atualizada e extrai as notas da versão:

```bash
python3 .agents/skills/release-flow/scripts/extract_release_notes.py CHANGELOG.md 2.0.0 > .release/release-notes.md
```

Mostra a especificação (tag `v2.0.0` no commit atual da `main`, título `v2.0.0 - API v2 e autenticação por JWT`, notas, sem pré-lançamento) e pergunta *"Posso criar a tag e publicar a Release?"*. Com o "sim":

```bash
git tag -a v2.0.0 -m "v2.0.0: API v2 e autenticação por JWT"
git push origin v2.0.0
gh release create v2.0.0 --verify-tag --title "v2.0.0 - API v2 e autenticação por JWT" --notes-file .release/release-notes.md
```

O resultado final é um repositório com changelog rastreável, versão justificada, README atualizado, PR com contexto para o revisor e uma tag que aponta para o commit exato da versão.
