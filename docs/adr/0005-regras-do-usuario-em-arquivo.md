# ADR 0005: Regras do time em `.release-rules.md`

- **Status:** aceita
- **Data:** 2026-11-10

## Contexto

Times têm convenções próprias: "em `0.y.z`, breaking sobe o MINOR", "migration que remove coluna é MAJOR", rótulos permitidos em PRs, quais tipos de commit ignorar no changelog. Embutir essas regras nas skills as tornaria rígidas; pedir a cada execução cansa e gera inconsistência.

## Decisão

Um arquivo Markdown opcional na raiz do projeto, `.release-rules.md`, com seções por assunto (Idioma, Versionamento, Changelog, README, Pull Request, Tag e release). Cada skill lê a sua seção. Um modelo vem em `release-flow/assets/release-rules.example.md`. As regras **refinam** o comportamento padrão; quando uma contradiz o SemVer ou outro padrão, o agente avisa antes de aplicar e registra a regra na justificativa.

## Consequências

- O time versiona suas regras junto do código e todo mundo, e toda ferramenta, as segue.
- Texto livre dá flexibilidade, mas depende de o modelo interpretar bem. Regras ambíguas levam a perguntas ou a interpretações diferentes.
- Não há validação automática do conteúdo do arquivo. Um esquema estruturado seria mais rígido; fica como possível evolução se o texto livre se mostrar insuficiente.
