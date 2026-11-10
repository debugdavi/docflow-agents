## Resumo

<O que a versão vX.Y.Z entrega, em 2 ou 3 linhas.>

## Versão

| | |
|---|---|
| Anterior → nova | `<X.Y.Z>` → `<A.B.C>` |
| Tipo do bump | `MAJOR` / `MINOR` / `PATCH` |
| Por quê | <evidência: item do changelog e fato da branch; regras do usuário aplicadas> |

## Atenção antes de aprovar

<Só se houver. Estes itens quebram ambientes quando passam despercebidos.>

- **Breaking changes:** <item e instrução de migração>
- **Variáveis de ambiente novas:** `<NOME>`: <para que serve>
- **SDKs / bibliotecas novas:** `<nome versão>`
- **Migrations:** <arquivo e observação sobre rollback>

## Changelog desta versão

<Cole aqui a seção `## [A.B.C]` do CHANGELOG.md, com os links de cada item.>

## Por onde começar a revisão

1. `CHANGELOG.md`: confira se cada item corresponde a uma mudança real e se os breaking têm migração.
2. <Manifestos alterados>: confira a versão `<A.B.C>`.
3. `README.md`: <o que mudou, ou "sem mudanças">.

## Documentação

<Resumo do que mudou no README e nos manifestos.>

## Depois do merge

A tag e a Release são criadas a partir da branch de destino atualizada:

```bash
git switch <destino> && git pull
git tag -a v<A.B.C> -m "<mensagem da tag>"
git push origin v<A.B.C>
gh release create v<A.B.C> --verify-tag --title "<título>" --notes-file release-notes.md
```

## Checklist de revisão

- [ ] CI verde
- [ ] A versão é a mesma no changelog, nos manifestos e no título do PR
- [ ] Breaking changes têm instrução de migração
- [ ] Variáveis de ambiente novas estão documentadas e configuradas nos ambientes
- [ ] A tag `v<A.B.C>` ainda não existe no remoto
