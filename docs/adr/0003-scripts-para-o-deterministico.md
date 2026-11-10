# ADR 0003: Parte determinística em scripts, julgamento no modelo

- **Status:** aceita
- **Data:** 2026-11-10

## Contexto

Pedir ao modelo para ler `git log`, achar rodapés de `BREAKING CHANGE:`, comparar dependências entre dois commits e recortar uma seção do changelog funciona na maior parte das vezes, mas falha de formas silenciosas (um rodapé escondido por `--oneline`, uma dependência que mudou de major sem ninguém notar). Essas tarefas têm resposta certa e dá para testá-las.

## Decisão

Três scripts Python, só com biblioteca padrão, ficam em `release-flow/scripts/`: `collect_commits.py` (commits em JSON), `branch_facts.py` (arquivos por categoria, diffs de dependências, versões nos manifestos, dicas) e `extract_release_notes.py` (seção de uma versão). Eles emitem fatos; a decisão continua com o agente. Cada skill traz também o equivalente em comandos git, então os scripts são opcionais. Os scripts são testados com repositórios git reais temporários.

## Consequências

- A parte que tem resposta certa é testável e repetível, e o agente começa a análise com evidências estruturadas.
- Exige Python 3.8+ para usar os scripts; sem ele, o agente usa os comandos git de cada skill.
- As heurísticas (categorias de arquivo, dicas) podem errar em estruturas incomuns de projeto. Por isso são tratadas como pistas e o agente deve abrir os arquivos antes de concluir.
- Os scripts vivem em `release-flow`, mas são usados por outras skills; quem instala uma skill isolada perde os scripts e cai no equivalente em git.
