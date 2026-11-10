# <Nome do projeto>

![versão](https://img.shields.io/badge/vers%C3%A3o-<X.Y.Z>-blue)

<Um parágrafo: o que o projeto faz, para quem e qual problema resolve.>

**Área:** <Back-end | Front-end | Dados | ML | IA — pode combinar, ex.: Back-end + IA>

## Stack e SDKs

| Categoria | Tecnologia | Versão | Papel |
|---|---|---|---|
| Linguagem | <ex.: Python> | <3.12> | <linguagem principal> |
| Framework | <ex.: FastAPI> | <0.115> | <API HTTP> |
| Banco de dados | <ex.: PostgreSQL> | <16> | <persistência> |
| Cloud / SDK | <ex.: AWS SDK> | <versão> | <uso> |

> Versões lidas de `<lockfile>`. Intervalos "declarados" vêm do manifesto, quando não há lockfile.

## Principais bibliotecas

| Biblioteca | Versão | Para que serve no projeto |
|---|---|---|
| <nome> | <versão> | <papel> |

## Decisões técnicas

| Escolha | Por quê | Fonte |
|---|---|---|
| <ex.: PostgreSQL com pgvector> | <motivo em uma frase> | <ADR-0002, #57 ou commit> |
| <escolha sem registro> | a confirmar | — |

## Pré-requisitos

- <runtime e versão, ex.: Python 3.12+>
- <ferramentas, ex.: Docker 24+, GitHub CLI>

## Instalação

```bash
<comandos exatos, copiados dos scripts do projeto>
```

## Configuração

Copie `.env.example` para `.env` e preencha:

| Variável | Obrigatória | Descrição | Exemplo |
|---|---|---|---|
| `API_URL` | sim | <descrição> | `https://exemplo.local` |
| `API_KEY` | sim | <descrição> | `YOUR_API_KEY_HERE` |

## Como executar e testar

```bash
<executar localmente>
<rodar testes>
```

## Estrutura do projeto

```text
<árvore curta com as pastas principais e o papel de cada uma>
```

## Contribuindo e licença

<Seções já existentes do projeto: preservar.>
