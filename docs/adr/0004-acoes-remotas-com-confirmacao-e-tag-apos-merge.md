# ADR 0004: Ações no remoto só com confirmação, e tag depois do merge

- **Status:** aceita
- **Data:** 2026-11-10

## Contexto

Push, criação de PR, tag e Release são visíveis para o time e difíceis de desfazer: mover uma tag publicada quebra quem já a usou. Uma tag criada antes do merge pode apontar para um commit que nunca chega à branch principal. Uma versão anterior do fluxo apenas gerava texto e deixava tudo ao usuário, o que era seguro mas pouco útil, já que o `gh` permite automatizar essas ações.

## Decisão

As skills usam `git` e `gh` e **leem** livremente (`gh repo view`, `gh pr view`, `git log`), mas **escrevem** no remoto (`git push`, `gh pr create`, tag, `gh release create`) apenas depois de mostrar o comando e o conteúdo e receber confirmação explícita, uma para cada ação. A tag é criada a partir da branch de destino atualizada, só com o PR em estado `MERGED`, e a Release usa `--verify-tag` para o `gh` nunca criar uma tag sozinho em outro commit. Nunca se usa `--force`, `git push --tags` ou remoção de tag, release ou branch sem pedido explícito.

## Consequências

- O fluxo automatiza o trabalho repetitivo sem tirar da pessoa as decisões irreversíveis.
- Há mais pausas do que numa automação completa; é o preço pretendido.
- A confirmação é uma instrução às skills, não uma trava técnica: uma ferramenta configurada para aprovar comandos automaticamente a contornaria. A proteção real continua sendo a política de permissões da ferramenta e do repositório (branch protegida, permissões de tag).
- Sem `gh` autenticado, o fluxo entrega os textos e os comandos para a pessoa executar.
