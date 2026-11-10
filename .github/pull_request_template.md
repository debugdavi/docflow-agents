## Resumo

<O que muda e por quê, em 2 ou 3 linhas.>

## Por onde começar a revisão

<A parte mais complexa da mudança e o que conferir nela.>

## O que mudou

- <assunto 1>

## Impacto

<Mudou o comportamento de alguma skill? Há breaking change para quem já usa? Scripts alterados?>

## Como testar

```bash
python scripts/validate_skills.py
python -m unittest discover -s tests -v
```

## Checklist

- [ ] Validador e testes passando
- [ ] `description` das skills alteradas diz o que fazem e quando usar
- [ ] Decisão relevante registrada em `docs/adr/`
- [ ] `CHANGELOG.md` atualizado em `[Unreleased]`
