#!/usr/bin/env python3
"""Instala as skills do DocFlow em um projeto (ou no seu usuário) de forma portátil.

As skills ficam em `.agents/skills/` (lido por Copilot, Cursor, Gemini CLI, Codex e
outros). O Claude Code lê `.claude/skills/`, então o instalador cria ali um link
para cada skill (ou uma cópia, se o sistema não permitir links, como o Windows sem
modo de desenvolvedor).

Uso:
    python scripts/install.py /caminho/do/projeto     # instala no projeto
    python scripts/install.py --personal              # instala em ~/.agents/skills
    python scripts/install.py --here                  # só cria .claude/skills neste repositório
Opções: --copy (copia em vez de linkar), --force (sobrescreve skills existentes)
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / ".agents" / "skills"
RULES_EXAMPLE = SOURCE / "release-flow" / "assets" / "release-rules.example.md"


def skill_names():
    return sorted(p.name for p in SOURCE.iterdir() if (p / "SKILL.md").is_file())


def copy_skills(dest: Path, force: bool, log):
    dest.mkdir(parents=True, exist_ok=True)
    for name in skill_names():
        target = dest / name
        if target.exists() and not force:
            log(f"  já existe, mantido: {target}  (use --force para sobrescrever)")
            continue
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(SOURCE / name, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        log(f"  copiado: {target}")


def link_skill(agents_dir: Path, claude_dir: Path, name: str, copy: bool, force: bool, log):
    claude_dir.mkdir(parents=True, exist_ok=True)
    link = claude_dir / name
    if link.exists() or link.is_symlink():
        if not force:
            log(f"  já existe, mantido: {link}")
            return
        if link.is_symlink() or link.is_file():
            link.unlink()
        else:
            shutil.rmtree(link)
    real = agents_dir / name
    if not copy:
        try:
            relative = os.path.relpath(real, claude_dir)
            os.symlink(relative, link, target_is_directory=True)
            log(f"  link: {link} -> {relative}")
            return
        except (OSError, NotImplementedError):
            log("  sem suporte a links neste sistema; usando cópia")
    shutil.copytree(real, link, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    log(f"  copiado: {link}")


def ensure_gitignore(project: Path, log):
    path = project / ".gitignore"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if ".release/" in existing.splitlines():
        return
    with path.open("a", encoding="utf-8") as handle:
        if existing and not existing.endswith("\n"):
            handle.write("\n")
        handle.write("# estado de trabalho do DocFlow\n.release/\n")
    log(f"  .gitignore atualizado: {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("target", nargs="?", help="pasta do projeto onde instalar")
    parser.add_argument("--personal", action="store_true", help="instala no diretório do usuário")
    parser.add_argument("--here", action="store_true", help="só cria .claude/skills neste repositório")
    parser.add_argument("--copy", action="store_true", help="copia em vez de criar links")
    parser.add_argument("--force", action="store_true", help="sobrescreve o que já existe")
    args = parser.parse_args(argv)

    if args.here:
        root = REPO
    elif args.personal:
        root = Path.home()
    elif args.target:
        root = Path(args.target).expanduser().resolve()
        if not root.is_dir():
            print(f"erro: pasta não encontrada: {root}", file=sys.stderr)
            return 1
    else:
        parser.print_usage(sys.stderr)
        print("erro: informe a pasta do projeto, --personal ou --here", file=sys.stderr)
        return 1

    log = print
    agents_dir = root / ".agents" / "skills"
    log(f"Instalando em {root}")
    if agents_dir.resolve() != SOURCE.resolve():
        copy_skills(agents_dir, args.force, log)
    for name in skill_names():
        link_skill(agents_dir, root / ".claude" / "skills", name, args.copy, args.force, log)

    if not args.personal and not args.here:
        example = root / ".release-rules.example.md"
        if not example.exists():
            shutil.copyfile(RULES_EXAMPLE, example)
            log(f"  regras de exemplo: {example}")
        ensure_gitignore(root, log)

    log("\nPronto. Próximos passos:")
    log("  1. (opcional) copie .release-rules.example.md para .release-rules.md e ajuste as regras do seu time")
    log("  2. instale e autentique o GitHub CLI: gh auth login")
    log("  3. peça à sua IA: \"prepare a release\" (skill release-flow)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
