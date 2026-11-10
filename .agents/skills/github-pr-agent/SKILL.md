---
name: github-pr-agent
description: Escreve a descrição do Pull Request para o revisor (resumo, parte mais complexa em destaque, decisões técnicas, impacto, bibliotecas instaladas, como testar) e abre o PR no GitHub com o gh depois de confirmação. Funciona para PRs de funcionalidade e para o PR de release (com versão e changelog). Use quando o usuário pedir para criar, abrir, escrever ou revisar um PR, pull request, descrição de PR, mensagem para o reviewer, ou ao fim do fluxo de release.
compatibility: Requer git e GitHub CLI (gh) autenticado com gh auth login.
metadata:
  version: "0.1.0"
---
# GitHub PR Agent

Escreve o PR de modo que o revisor entenda **o que foi feito, por que, e onde olhar com mais cuidado** sem ler o diff inteiro antes. A leitura é rápida de propósito: resumo curto no topo, e o espaço maior vai para a parte mais difícil da mudança. Etapa 4 do fluxo `release-flow`; funciona também sozinho para qualquer branch.

O que guia o texto (fontes em `docs/references.md`): a primeira linha tem de se sustentar sozinha e dizer *o quê*; o corpo explica *por quê*, já que o código mostra o que faz mas não a razão; e o texto precisa ainda estar certo no estado final do PR.

Modelos: [assets/pr-feature.md](assets/pr-feature.md) e [assets/pr-release.md](assets/pr-release.md). Se existir `.release-rules.md`, leia a seção "Pull Request".

## Passos

1. **Levantar o contexto.**
   ```bash
   gh repo view --json nameWithOwner,defaultBranchRef -q '.nameWithOwner + " " + .defaultBranchRef.name'
   git branch --show-current
   git log --no-merges --format='%h %s%n%b---' <base>..HEAD
   git diff --numstat <base>...HEAD
   gh pr list --head "$(git branch --show-current)" --state open --json number,url
   ```
   `<base>` é a branch de destino (padrão: a branch padrão do repositório). Se já existe PR aberto para a branch, o objetivo passa a ser **atualizar** a descrição (`gh pr edit <n> --body-file ...`), não criar outro. Para mudanças de dependência e arquivos por categoria, rode `python3 .agents/skills/release-flow/scripts/branch_facts.py --base <base>` (ajuste o caminho) ou leia `git diff <base>...HEAD -- <manifestos>`.

2. **Modo.** `release` se a branch é de release ou o fluxo `release-flow` chamou esta skill (há versão decidida em `.release/context.yml`); caso contrário, `feature`.

3. **Respeitar o modelo do repositório.** Se existir `.github/pull_request_template.md` (ou a pasta `.github/PULL_REQUEST_TEMPLATE/`), use os cabeçalhos dele e acrescente só o que faltar de essencial (parte complexa, impacto). Sem modelo, use o do modo escolhido.

4. **Achar a parte mais difícil.** É nela que o revisor deve gastar atenção, então gaste o seu primeiro. Procure no diff, ignorando lockfiles e arquivos gerados:
   - lógica nova ou reescrita com muitos ramos, concorrência, cache, estado ou tratamento de erro;
   - segurança (autenticação, permissões, entrada de usuário), migrations e mudanças de dados;
   - contratos públicos (API, CLI, formatos de arquivo) e novas abstrações;
   - o ponto onde você mais hesitou ao decidir.

   Leia esses trechos e explique: o que fazem, por que são delicados, o que conferir. Se não estiver claro qual foi a parte difícil, **pergunte ao usuário** em uma linha antes de escrever.

5. **Preencher o corpo.** Seções que não se aplicam saem do texto; não escreva "N/A".
   - **Resumo:** 2 ou 3 linhas com o quê e o porquê.
   - **Por onde começar a revisão:** a parte do passo 4, com caminhos de arquivo, em ordem de importância.
   - **O que mudou:** lista curta e agrupada por assunto, não por arquivo.
   - **Decisões técnicas:** cada decisão com o motivo e as alternativas descartadas **que estejam nos commits, em ADRs ou na fala do usuário**. Sem registro do motivo, pergunte; não invente justificativa.
   - **Impacto:** comportamento visível, API, dados e migrations, configuração e variáveis de ambiente, desempenho e segurança quando relevantes, e como reverter (rollback).
   - **Dependências:** tabela com biblioteca, mudança (nova, de 1.2 para 1.4, removida) e motivo. É o que o revisor precisa para instalar e entender o ambiente.
   - **Como testar:** passos ou comandos concretos; capturas de tela se a interface mudou.
   - **Issues:** `Closes #123` só quando o commit ou o usuário citar a issue.
   - **Modo release:** inclua também versão (anterior → nova, bump, justificativa), a seção do changelog dessa versão, um bloco **"Atenção antes de aprovar"** com breaking changes, variáveis de ambiente novas, SDKs novos e migrations (vêm da seção `readme` do contexto), e as instruções de pós-merge (tag e Release).

6. **Título.** Formato Conventional Commits, no imperativo, curto o bastante para aparecer inteiro na listagem: `feat(auth): adiciona login com SSO`. Release: `chore(release): vX.Y.Z`.

7. **Tamanho.** PR muito grande é difícil de revisar. Se o diff mistura assuntos independentes, diga ao usuário e sugira dividir; a decisão é dele.

8. **Mostrar e confirmar.** Grave o corpo em `.release/pr-body.md` e mostre título, branch de origem e destino, rótulos e corpo. Rótulos só os que existem (`gh label list --json name -q '.[].name'`); não crie rótulos. Pergunte: "Posso fazer o push e abrir o PR?".

9. **Abrir (só após o "sim").**
   ```bash
   git push -u origin HEAD
   gh pr create --base <destino> --head <origem> --title "<título>" --body-file .release/pr-body.md [--draft] [--label <rótulo>] [--reviewer <handle>]
   ```
   Passe sempre `--title` e `--body-file`, para o `gh` não abrir prompts interativos. Use `--draft` se o usuário pedir ou se `.release-rules.md` mandar. Sem `gh` ou sem autenticação, entregue o arquivo e os comandos para o usuário rodar.

10. **Registrar e passar adiante.** Preencha a seção `pr` de `.release/context.yml` (modo, número, URL, estado). Informe o link. No fluxo de release, o próximo passo é o merge, que é humano; depois dele vem o `github-release-agent`.

## Cuidados

- O texto descreve o PR **final**. Se o código mudar durante a revisão, atualize a descrição com `gh pr edit`.
- Nada de segredos, tokens ou dados pessoais no corpo.
- Não afirme que testou algo que não rodou. Em "Como testar", separe o que foi executado do que é sugestão.
