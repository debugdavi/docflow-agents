# Como reconhecer stack e área do projeto

Pistas, não regras. Confirme sempre no código e, se a pista for ambígua, pergunte.

## Onde ficam versões e requisitos

| Arquivo | O que revela |
|---|---|
| `package.json` | libs, `engines.node`, scripts (`build`, `test`, `start`) |
| `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` | versões resolvidas |
| `pyproject.toml`, `requirements*.txt`, `poetry.lock`, `uv.lock` | libs Python, `requires-python` |
| `*.csproj`, `global.json`, `Directory.Build.props` | `TargetFramework`, SDK do .NET, pacotes NuGet |
| `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle` | módulos e versão da linguagem |
| `Dockerfile`, `docker-compose.yml` | imagem base (runtime), serviços de apoio (banco, cache, fila) |
| `.github/workflows/*.yml` | versões usadas no CI, comandos de build e teste |
| `.nvmrc`, `.python-version`, `.tool-versions` | versão exata do runtime |
| `.env.example` | variáveis de ambiente esperadas |
| `Makefile`, `justfile`, `scripts/` | comandos de desenvolvimento |

## Área do projeto

Uma ou mais, conforme as evidências.

| Área | Sinais comuns |
|---|---|
| Back-end | Express, Fastify, NestJS, FastAPI, Django, Flask, Spring, ASP.NET, Gin; pastas `routes/`, `controllers/`; migrations; ORM |
| Front-end | React, Vue, Angular, Svelte, Next.js, Vite; `src/components/`; CSS/Tailwind; testes de UI |
| Dados | pandas, polars, Spark, dbt, Airflow, Dagster; SQL em lote; notebooks de análise; pipelines ETL |
| ML | scikit-learn, PyTorch, TensorFlow, XGBoost, MLflow; pastas `models/`, `training/`; métricas e datasets |
| IA | SDKs de LLM, LangChain, LlamaIndex, embeddings, bancos vetoriais (pgvector, Chroma, FAISS), prompts versionados, avaliação |

## Dependências diretas x transitivas

Liste apenas o que o projeto declara no manifesto (diretas). Dependências que só aparecem no lockfile são transitivas e ficam fora do README.

## Onde procurar o motivo de uma decisão

1. `docs/adr/`, `docs/decisions/`, `adr/`
2. O commit que introduziu a dependência: `git log -S'"lib"' -- <manifesto>`
3. O PR desse commit: `gh pr list --state merged --search "<sha>"`
4. Descrições de PR e corpo de commits
5. O usuário
