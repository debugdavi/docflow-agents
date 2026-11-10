# Contrato de contexto: `.release/context.yml`

Estado compartilhado entre as etapas. Fica em arquivo (e não só na conversa) para sobreviver a troca de ferramenta, de sessão ou de janela de contexto: quem retomar o fluxo lê o arquivo e sabe onde parou.

Regras:

- O orquestrador cria o arquivo e a seção de topo. Cada skill preenche **apenas a própria seção**.
- Se faltar um campo de que uma etapa depende, ela pergunta ao usuário. Sem usuário disponível, grava `status: blocked` e a dúvida em `pendencias`.
- O arquivo é estado de trabalho. Fica fora do git (`.release/` no `.gitignore`).
- Não guarde segredos nem o texto completo do changelog aqui: o texto fica em `CHANGELOG.md`.

```yaml
release-context:
  status: ok                    # ok | blocked
  etapa_atual: version-agent
  projeto: nome-do-projeto
  repositorio: dono/projeto     # nameWithOwner
  repo_url: https://github.com/dono/projeto
  branch_origem: release/v1.3.0
  branch_destino: main
  data: 2026-11-10
  regras_usuario: .release-rules.md   # ou null

  changelog:                    # changelog-agent
    arquivo: CHANGELOG.md
    base: v1.2.0                # tag de partida do intervalo
    secoes: [Added, Fixed]
    breaking: false
    ambiguos: []                # commits que o usuário precisa classificar

  versao:                       # version-agent
    anterior: 1.2.0
    nova: 1.3.0
    tag: v1.3.0
    bump: MINOR                 # MAJOR | MINOR | PATCH
    justificativa: "Added: login com SSO (#42)"
    regras_aplicadas: []        # regras do usuário que pesaram na decisão
    manifestos: [package.json, package-lock.json]
    confirmada: true            # o usuário confirmou o número

  readme:                       # readme-agent
    alterado: true
    resumo: "Nova lib X; variável API_URL"
    novas_variaveis_env: [API_URL]
    novos_sdks_libs: ["lib-x 2.1.0"]
    decisoes_a_confirmar: []

  pr:                           # github-pr-agent
    modo: release               # feature | release
    numero: 57
    url: https://github.com/dono/projeto/pull/57
    estado: OPEN                # OPEN | MERGED | CLOSED

  release:                      # github-release-agent
    tag: v1.3.0
    url: null
    prerelease: false

  pendencias: []                # perguntas em aberto de qualquer etapa
```
