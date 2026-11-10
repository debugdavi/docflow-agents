# Regras de release do projeto

Copie este arquivo para `.release-rules.md` na raiz do repositório e ajuste. As skills do fluxo o leem se ele existir. Tudo é opcional: apague o que não se aplica.

As regras **refinam** o comportamento padrão. Quando uma regra contradiz o SemVer ou outro padrão, o agente avisa antes de aplicá-la e registra a regra usada na justificativa.

## Idioma
- Idioma dos textos gerados: pt-BR

## Versionamento
- Enquanto a versão for `0.y.z`, uma breaking change sobe o MINOR (e não o MAJOR).
- Qualquer migration que remova ou renomeie coluna é MAJOR.
- Mudança só em dependências de segurança (Dependabot) é PATCH.
- Mudança de comportamento atrás de feature flag desligada não conta como MINOR.
- Prefixo das branches de release: `release/`
- Pré-lançamentos usam o sufixo `-rc.N`.

## Changelog
- Escopos que merecem destaque no texto: `auth`, `payments`, `api`
- Ignorar commits de: `ci`, `chore(deps-dev)`, `style`
- Citar sempre o número do ticket quando existir (ex.: `PROJ-123` na mensagem do commit)

## README
- Seção "Decisões técnicas": registrar também alternativas descartadas
- Áreas do projeto usadas na documentação: Back-end, Front-end, Dados, IA

## Pull Request
- Revisores padrão: `@time-backend`
- Rótulos permitidos: `feature`, `bugfix`, `release`, `breaking-change`
- PRs de release sempre como rascunho (draft) até o CI passar

## Tag e release
- Sempre criar tag anotada
- Releases com sufixo `-rc` são marcadas como pré-lançamento
- Anexar artefatos de `dist/*.tar.gz` à Release
