---
name: version-agent
description: Decide a próxima versão do projeto pelo Semantic Versioning (MAJOR, MINOR ou PATCH) analisando a branch (commits, arquivos alterados, migrations, contratos de API, dependências) e o changelog, aplicando regras definidas pelo usuário, e depois datar o changelog, atualizar links e manifestos. Use quando o usuário perguntar qual a próxima versão, falar em bump, versionar a branch, major/minor/patch, ou depois do changelog-agent no fluxo de release.
compatibility: Requer git. O script de apoio usa Python 3.8+. Para npm, o comando npm version é usado nos manifestos.
metadata:
  version: "0.1.0"
---
# Version Agent

Decide o incremento de versão olhando **o que foi implementado na branch**, e não só o texto do changelog. O changelog diz o que os commits alegam; a análise da branch confirma (ou contradiz) com evidências: arquivos removidos, migrations, contratos de API, dependências que mudaram de major. Etapa 2 do fluxo `release-flow`; funciona também sozinho.

O número decidido aqui é herdado por README, PR e tag. Por isso o agente **propõe, justifica e espera a confirmação do usuário** antes de editar qualquer arquivo.

## Passos

1. **Levantar os fatos da branch.**
   ```bash
   python3 .agents/skills/release-flow/scripts/branch_facts.py
   ```
   (ajuste o caminho à sua instalação; `--base <ref>` compara com outra referência). O JSON traz: intervalo analisado, commits por tipo e os marcados como breaking, arquivos por categoria (manifestos, migrations, contratos de API, configuração, infra/CI, testes, docs, código), arquivos removidos, diffs de dependências, versões declaradas nos manifestos e **dicas** geradas por heurística. Sem o script: `git log <última-tag>..HEAD --format='%h %s%n%b---'`, `git diff --stat <última-tag>..HEAD` e `git diff <última-tag>..HEAD -- <manifestos>`.

   As dicas são pistas para você investigar, nunca conclusões. Abra os arquivos suspeitos antes de decidir.

2. **Ler o changelog e as regras do usuário.**
   - `## [Unreleased]` do `CHANGELOG.md`. Vazio → não há o que lançar: avise e pare.
   - `.release-rules.md`, seção "Versionamento", se existir. Cada regra relevante entra na justificativa ("regra do usuário: ...").

3. **Versão atual**, nesta ordem: última tag, depois o manifesto. Se divergirem, mostre as duas e pergunte. Sem nenhuma (primeira release), pergunte se começa em `0.1.0` ou `1.0.0`.

4. **Decidir o bump.** Vale o maior nível encontrado, depois de aplicar as regras do usuário.

   | Nível | Evidências típicas |
   |---|---|
   | MAJOR | item `**BREAKING:**`; remoção ou renomeação de API pública, endpoint, comando ou opção de configuração; migration destrutiva sem compatibilidade; contrato de API alterado de forma incompatível |
   | MINOR | funcionalidade nova compatível (`Added`); `Deprecated`; mudança de comportamento visível porém compatível; dependência nova que muda requisitos de runtime |
   | PATCH | correções (`Fixed`), segurança (`Security`), ajustes internos sem efeito visível, só docs/testes/CI (às vezes nem exige versão) |

   Casos de borda:
   - **Evidência contradiz o changelog.** Um arquivo público removido sem marca de breaking, por exemplo: não corrija sozinho. Mostre ao usuário e devolva ao `changelog-agent` via `pendencias`.
   - **Remoção de algo que nunca foi público** não força MAJOR. Na dúvida, pergunte.
   - **Versão `0.y.z`:** o SemVer permite mudanças incompatíveis a qualquer momento, e a convenção comum é subir o MINOR. Ir para `1.0.0` é declarar a API estável. Mencione e deixe o usuário escolher, salvo regra dele.
   - **Regra do usuário que contradiz o SemVer** (por exemplo "breaking sobe só o MINOR" com a versão em `1.x`): aplique só depois de dizer isso explicitamente e registre em `regras_aplicadas`.
   - **Pré-lançamento** (`-rc.1`) só quando o usuário pedir ou a regra mandar. Novo candidato incrementa o sufixo; a versão final sai sem ele.

5. **Emitir o veredito e pedir confirmação.**
   - Versão anterior → nova (e a tag `vA.B.C`)
   - Tipo do bump
   - Evidências, em lista curta: o item do changelog e o fato da branch que sustentam o nível, mais as regras do usuário aplicadas.
   - Pergunte: "Confirma a versão A.B.C?". Sem confirmação, nada é editado.

6. **Aplicar, depois do "sim".**
   - Renomeie `## [Unreleased]` para `## [A.B.C] - AAAA-MM-DD` (data de hoje) e crie um novo `## [Unreleased]` vazio acima.
   - Atualize os links de comparação no rodapé, com a URL do repositório (`gh repo view --json url -q .url`):
     ```markdown
     [Unreleased]: https://github.com/dono/repo/compare/vA.B.C...HEAD
     [A.B.C]: https://github.com/dono/repo/compare/vANTERIOR...vA.B.C
     ```
     Na primeira versão: `[A.B.C]: https://github.com/dono/repo/releases/tag/vA.B.C`.
   - Atualize a versão nos manifestos que a declaram, sem o `v`. Para npm, `npm version A.B.C --no-git-tag-version` atualiza `package.json` e o lockfile. Nos demais (`pyproject.toml`, `Cargo.toml`, `*.csproj`...) edite só o campo de versão. Nunca edite lockfiles à mão.
   - Se o trabalho ainda não está numa branch de release, sugira `release/vA.B.C` (ou o prefixo das regras do usuário). Criar a branch é com o orquestrador ou com o usuário.

7. **Registrar e passar adiante.** Preencha a seção `versao` de `.release/context.yml` (anterior, nova, tag, bump, justificativa, regras aplicadas, manifestos, `confirmada`). O próximo passo é sempre o `readme-agent`, mesmo num PATCH: é ele quem decide se o README muda.

## Cuidados

- Refatoração interna que não muda a interface pública não gera MAJOR.
- Ao subir MINOR zere o PATCH; ao subir MAJOR zere MINOR e PATCH.
- Tag leva `v`; manifestos não.
- Em monorepo com versões independentes por pacote, pergunte qual pacote está sendo versionado antes de analisar.
