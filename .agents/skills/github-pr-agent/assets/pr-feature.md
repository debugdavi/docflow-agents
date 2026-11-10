## Resumo

<2 ou 3 linhas: o que muda e por quê. Quem só ler isto deve entender o PR.>

## Por onde começar a revisão

<A parte mais complexa da mudança, em ordem de importância.>

1. `<caminho/do/arquivo>`: <o que faz, por que é delicado, o que conferir>
2. `<caminho/do/arquivo>`: <idem>

## O que mudou

- <assunto 1: uma linha>
- <assunto 2: uma linha>

## Decisões técnicas

| Decisão | Por quê | Alternativas descartadas |
|---|---|---|
| <o que foi decidido> | <motivo> | <opção e por que ficou de fora> |

## Impacto

- **Comportamento / API:** <o que muda para quem usa; breaking changes, se houver>
- **Dados / migrations:** <migrations, compatibilidade, backfill>
- **Configuração:** <variáveis de ambiente novas ou renomeadas>
- **Desempenho / segurança:** <se relevante>
- **Rollback:** <como reverter>

## Dependências

| Biblioteca | Mudança | Motivo |
|---|---|---|
| `<nome>` | nova (`<versão>`) / `<de>` → `<para>` / removida | <por que> |

## Como testar

```bash
<comandos ou passos>
```

<Capturas de tela, se a interface mudou.>

## Issues relacionadas

Closes #<número>
