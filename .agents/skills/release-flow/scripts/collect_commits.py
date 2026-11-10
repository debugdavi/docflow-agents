#!/usr/bin/env python3
"""Lista os commits de um intervalo como JSON estruturado (Conventional Commits).

Parte determinística do changelog-agent: o script lê o git e organiza os fatos;
quem decide categoria, redação e agrupamento é o agente.

Uso:
    collect_commits.py [--base REF] [--head REF] [--repo CAMINHO] [--no-files]

Sem --base, usa a última tag alcançável a partir de --head (sem tag: todo o histórico).
Só depende de git e da biblioteca padrão do Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from urllib.parse import urlsplit

CONVENTIONAL = re.compile(
    r"^(?P<type>[A-Za-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?:\s+(?P<subject>.+)$"
)
BREAKING_FOOTER = re.compile(r"^BREAKING[ -]CHANGE:[ \t]*(?P<first>.*)$", re.M)
ISSUE_REF = re.compile(r"(?<![\w/])#(?P<n>\d+)\b")
TRAILING_PR = re.compile(r"\(#(?P<n>\d+)\)\s*$")
RS, US = "\x1e", "\x1f"


def git(*args, cwd=None, check=True):
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8"
    )
    if check and result.returncode != 0:
        raise SystemExit(f"erro: git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def previous_tag(head, cwd=None):
    """Última tag alcançável de `head`. Se `head` já está na tag, volta uma tag."""
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", head],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        return None, None
    tag = result.stdout.strip()
    tag_commit = git("rev-parse", f"{tag}^{{commit}}", cwd=cwd).strip()
    head_commit = git("rev-parse", f"{head}^{{commit}}", cwd=cwd).strip()
    if tag_commit != head_commit:
        return tag, None
    older = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", f"{tag}^"],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8",
    )
    return (older.stdout.strip() or None), tag


def normalize_remote(url):
    """Converte a URL do remote (ssh ou https) em URL https navegável, sem credenciais."""
    url = (url or "").strip()
    scp = re.match(r"^[\w.-]+@([^:/]+):(.+?)(?:\.git)?/?$", url)
    if scp:
        return f"https://{scp.group(1)}/{scp.group(2)}"
    if url.startswith(("http://", "https://", "ssh://")):
        parts = urlsplit(url)
        host = parts.hostname or ""
        if parts.scheme != "ssh" and parts.port:
            host = f"{host}:{parts.port}"
        path = re.sub(r"\.git$", "", parts.path).rstrip("/")
        return f"https://{host}{path}" if host else None
    return None


def parse_commit(sha, short, date, author, subject, body):
    match = CONVENTIONAL.match(subject)
    footer = BREAKING_FOOTER.search(body)
    note = None
    if footer:
        continuation = body[footer.end():].split("\n\n")[0].strip()
        note = " ".join(part for part in (footer.group("first").strip(), continuation) if part)
    breaking = bool(match and match.group("bang")) or footer is not None
    trailing = TRAILING_PR.search(subject)
    refs = sorted({int(m.group("n")) for m in ISSUE_REF.finditer(f"{subject}\n{body}")})
    return {
        "sha": sha,
        "short": short,
        "date": date,
        "author": author,
        "conventional": bool(match),
        "type": match.group("type").lower() if match else None,
        "scope": (match.group("scope") or None) if match else None,
        "subject": match.group("subject").strip() if match else subject.strip(),
        "raw_subject": subject,
        "breaking": breaking,
        "breaking_note": note,
        "pr_hint": int(trailing.group("n")) if trailing else None,
        "refs": refs,
    }


def collect(base=None, head="HEAD", cwd=None, with_files=True):
    head_tag = None
    if base is None:
        base, head_tag = previous_tag(head, cwd)
    rng = f"{base}..{head}" if base else head
    fmt = "%x1e%H%x1f%h%x1f%ad%x1f%an%x1f%s%x1f%b%x1f"
    out = git("log", "--no-merges", "--date=short", f"--format={fmt}", "--name-only", rng, cwd=cwd)
    commits = []
    for record in out.split(RS)[1:]:
        sha, short, date, author, subject, body, tail = record.split(US)
        commit = parse_commit(sha, short, date, author, subject, body.strip())
        if with_files:
            commit["files"] = [line for line in tail.splitlines() if line.strip()]
        commits.append(commit)

    remote = git("remote", "get-url", "origin", cwd=cwd, check=False).strip()
    repo_url = normalize_remote(remote)
    if repo_url:
        for commit in commits:
            commit["commit_url"] = f"{repo_url}/commit/{commit['sha']}"

    by_type = Counter(c["type"] for c in commits if c["conventional"])
    return {
        "range": {
            "base": base,
            "head": head,
            "head_is_tagged": head_tag,  # preenchido quando HEAD já está numa tag
            "first_release": base is None,
        },
        "repo_url": repo_url,
        "summary": {
            "total": len(commits),
            "by_type": dict(sorted(by_type.items())),
            "breaking": sum(1 for c in commits if c["breaking"]),
            "non_conventional": sum(1 for c in commits if not c["conventional"]),
        },
        "commits": commits,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", help="referência inicial (padrão: última tag)")
    parser.add_argument("--head", default="HEAD", help="referência final (padrão: HEAD)")
    parser.add_argument("--repo", default=".", help="caminho do repositório")
    parser.add_argument("--no-files", action="store_true", help="omite a lista de arquivos")
    args = parser.parse_args(argv)
    data = collect(args.base, args.head, args.repo, with_files=not args.no_files)
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
