---
name: readme-agent
description: Cria ou atualiza o README.md refletindo a stack real do projeto, a área (back-end, front-end, dados, ML, IA), versões das bibliotecas, SDKs e requisitos, instalação, configuração, execução e as decisões técnicas por trás das escolhas, sempre ancoradas em evidência do repositório. Use ao iniciar um projeto, quando dependências, runtime, SDKs, variáveis de ambiente ou comandos mudarem, quando o usuário pedir README, documentação de stack ou "como rodar o projeto", e na etapa de README de cada release.
compatibility: Requer git. O gh (GitHub CLI) é opcional e ajuda a achar o PR em que uma decisão foi registrada.
metadata:
  version: "0.1.0"
---
# README Agent

Mantém o `README.md` fiel ao que o projeto é e usa, e explica **por que** as escolhas centrais foram feitas, quando isso estiver registrado. Um README desatualizado é pior que nenhum: quem segue instruções erradas perde tempo e passa a desconfiar do resto da documentação. Por isso este agente só afirma o que comprova nos arquivos do projeto. Etapa 3 do fluxo `release-flow`; funciona também sozinho.

Modelo de estrutura: [assets/readme-template.md](assets/readme-template.md). Como reconhecer stack e área pelos arquivos: [references/detect-stack.md](references/detect-stack.md).

Se existir `.release-rules.md`, leia a seção "README".

## Passos

1. **Ler o projeto.** Estrutura de pastas, manifestos (`package.json`, `*.csproj`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`...), lockfiles, `Dockerfile`, `docker-compose.yml`, CI (`.github/workflows/`), `.env.example`, ADRs (`docs/adr/`, `docs/decisions/`) e o README atual. No fluxo, leia também a seção `versao` do `.release/context.yml` e as mudanças da versão no changelog.
   - **Versão das libs:** use a resolvida no lockfile; sem lockfile, use o intervalo declarado e diga que é "declarado".
   - **Runtime e SDKs:** `.nvmrc`, `.python-version`, `engines` do `package.json`, `global.json`, `TargetFramework`, `FROM` do Dockerfile, imagens e versões no CI.

2. **Decidir o que fazer.** Compare stack, bibliotecas principais, runtime, SDKs, variáveis de ambiente e comandos com o README atual.
   - Não existe README: crie a partir do modelo.
   - Nada mudou além da versão: atualize só badge e menções à versão, se houver.
   - Nada mudou e não há menção à versão: não edite o arquivo e registre `alterado: false`.
   - Houve mudança: atualize apenas as seções afetadas.

3. **Montar ou atualizar as seções.** Use tabelas para facilitar a leitura rápida.
   - **Visão geral:** nome, badge da versão nova (`versao.nova` do contexto, nunca a antiga) e um parágrafo com o objetivo.
   - **Área do projeto:** uma ou mais entre Back-end, Front-end, Dados, ML, IA (ex.: "Back-end + IA"), inferida das dependências e da estrutura. Ambíguo? Pergunte.
   - **Stack e SDKs:** tabela Categoria × Tecnologia × Versão × Papel.
   - **Principais bibliotecas:** só as dependências diretas que definem o projeto, com o papel de cada uma. Não liste transitivas.
   - **Pré-requisitos e instalação:** runtime, SDKs, ferramentas (Docker, `gh`) e passo a passo.
   - **Configuração:** tabela de variáveis de ambiente (nome, obrigatória, descrição, exemplo com placeholder).
   - **Executar e testar:** comandos copiados dos scripts reais (`scripts` do `package.json`, `Makefile`, CI). Não achou o comando? Pergunte em vez de inventar.
   - **Decisões técnicas:** ver o passo 4.

4. **Registrar decisões técnicas, com evidência.** Inclua as escolhas que moldam o projeto (linguagem, framework, banco, autenticação, mensageria, infraestrutura, bibliotecas centrais) e ignore as triviais (linter, formatador). Para cada uma, procure o motivo, nesta ordem:
   1. ADRs e documentos de decisão do repositório.
   2. O commit que introduziu a dependência: `git log -S'"nome-da-lib"' --format='%h %s%n%b---' -- package.json` (ajuste o manifesto). Depois, o PR dele: `gh pr list --state merged --search "<sha>" --json number,title,body,url --limit 1`.
   3. Descrições de PR e corpo de commits que falem da escolha.
   4. O que o usuário disser na conversa.

   Achou o motivo: escreva-o em uma frase curta e cite a fonte (`ADR-0003`, `#57`, ``a1b2c3d``). Não achou: escreva **"a confirmar"** na coluna do motivo, nunca uma justificativa plausível inventada, e pergunte ao usuário no fim, em lista curta. Se ele responder, grave a resposta no README. Se as regras pedirem alternativas descartadas, inclua só as que aparecerem na fonte.

5. **Preservar o que é do projeto.** Ao atualizar um README existente, edite só as seções acima. Diagramas de arquitetura, licença, guia de contribuição, badges de CI e qualquer seção customizada ficam intactos, na mesma ordem.

6. **Registrar e passar adiante.** Preencha a seção `readme` de `.release/context.yml`: `alterado`, `resumo`, `novas_variaveis_env`, `novos_sdks_libs` (comparando com o README anterior) e `decisoes_a_confirmar`. O `github-pr-agent` usa esses campos para avisar os revisores; deixá-los vazios por esquecimento esconde mudanças que quebram o ambiente.

## Cuidados

- Nunca liste biblioteca, SDK ou comando que não apareça nos arquivos do projeto.
- Exemplos de `.env` usam apenas placeholders (`YOUR_API_KEY_HERE`); jamais copie valores reais.
- Escreva para quem chega ao projeto pela primeira vez: o que é, como rodar, o que precisa ter instalado.
