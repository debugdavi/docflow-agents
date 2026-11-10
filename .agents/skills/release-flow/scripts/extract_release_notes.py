#!/usr/bin/env python3
"""Extrai de um CHANGELOG.md (Keep a Changelog) o corpo de uma versão.

Uso:
    extract_release_notes.py CHANGELOG.md 1.3.0 > release-notes.md

Imprime o conteúdo entre `## [1.3.0] - data` e o próximo `## [`, sem o cabeçalho
e sem as linhas de link de rodapé (`[1.3.0]: https://...`).
Códigos de saída: 0 ok, 2 versão não encontrada, 3 seção vazia.
"""
from __future__ import annotations

import re
import sys

LINK_DEF = re.compile(r"^\[[^\]]+\]:\s*\S+")


def extract(text, version):
    version = version.lstrip("vV")
    heading = re.compile(rf"^##\s+\[{re.escape(version)}\](\s|$)")
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if heading.match(line)), None)
    if start is None:
        return None
    body = []
    for line in lines[start + 1:]:
        if line.startswith("## ["):
            break
        body.append(line)
    # remove links de rodapé que pertençam à última seção do arquivo
    while body and (not body[-1].strip() or LINK_DEF.match(body[-1])):
        body.pop()
    return "\n".join(body).strip("\n")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1
    path, version = argv
    with open(path, encoding="utf-8") as handle:
        notes = extract(handle.read(), version)
    if notes is None:
        print(f"erro: versão {version} não encontrada em {path}", file=sys.stderr)
        return 2
    if not notes.strip():
        print(f"erro: a seção {version} está vazia", file=sys.stderr)
        return 3
    print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
