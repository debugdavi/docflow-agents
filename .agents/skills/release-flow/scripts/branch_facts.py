#!/usr/bin/env python3
"""Levanta fatos sobre o que mudou na branch para apoiar a decisão de versão e o PR.

O script não decide nada: reúne evidências (arquivos por categoria, diffs de
dependências, commits com breaking change) e gera dicas. O julgamento sobre
MAJOR, MINOR ou PATCH é do agente, junto com as regras do usuário.

Uso:
    branch_facts.py [--base REF] [--head REF] [--repo CAMINHO]

Sem --base, usa a última tag (sem tag: compara com a árvore vazia).
Só depende de git e da biblioteca padrão do Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect_commits import collect, git  # noqa: E402

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

LOCKFILES = re.compile(
    r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|Pipfile\.lock|"
    r"Cargo\.lock|go\.sum|composer\.lock|Gemfile\.lock|packages\.lock\.json|uv\.lock)$"
)
MANIFESTS = re.compile(
    r"(^|/)(package\.json|pyproject\.toml|setup\.py|setup\.cfg|requirements[^/]*\.txt|Pipfile|"
    r"Cargo\.toml|go\.mod|pom\.xml|build\.gradle(\.kts)?|composer\.json|Gemfile|"
    r"[^/]+\.csproj|Directory\.Build\.props)$"
)
MIGRATIONS = re.compile(
    r"(^|/)(migrations?|alembic|db/migrate|prisma/migrations)(/|$)|\.sql$", re.I
)
API_CONTRACTS = re.compile(
    r"(openapi|swagger)[^/]*\.(ya?ml|json)$|\.proto$|\.(graphql|gql)$", re.I
)
CONFIG_ENV = re.compile(
    r"(^|/)(\.env(\.example|\.sample|\.template)?|config/.*|application[^/]*\.(ya?ml|properties)|"
    r"appsettings[^/]*\.json)$",
    re.I,
)
INFRA_CI = re.compile(
    r"(^|/)(Dockerfile[^/]*|docker-compose[^/]*\.ya?ml|\.github/workflows/.*|\.gitlab-ci\.ya?ml|Jenkinsfile)$"
)
TESTS = re.compile(r"(^|/)(tests?|__tests__|spec)(/|$)|\.(test|spec)\.[^/]+$|_test\.[^/]+$", re.I)
DOCS = re.compile(r"\.(md|rst|adoc)$|(^|/)docs?/", re.I)

CATEGORIES = (
    ("lockfiles", LOCKFILES),
    ("manifests", MANIFESTS),
    ("migrations", MIGRATIONS),
    ("api_contracts", API_CONTRACTS),
    ("config_env", CONFIG_ENV),
    ("infra_ci", INFRA_CI),
    ("tests", TESTS),
    ("docs", DOCS),
)


def categorize(path):
    for name, pattern in CATEGORIES:
        if pattern.search(path):
            return name
    return "source"


def show(ref, path, cwd):
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=cwd, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout if result.returncode == 0 else None


def name_status(base, head, cwd):
    out = git("diff", "--name-status", "-M", base or EMPTY_TREE, head, cwd=cwd)
    entries = []
    for line in out.splitlines():
        parts = line.split("\t")
        status = parts[0][0]
        if status == "R":
            entries.append({"status": "R", "path": parts[2], "old_path": parts[1]})
        else:
            entries.append({"status": status, "path": parts[1]})
    return entries


def shortstat(base, head, cwd):
    out = git("diff", "--shortstat", base or EMPTY_TREE, head, cwd=cwd)
    nums = {key: 0 for key in ("files", "insertions", "deletions")}
    for value, label in re.findall(r"(\d+) (file|insertion|deletion)", out):
        key = {"file": "files", "insertion": "insertions", "deletion": "deletions"}[label]
        nums[key] = int(value)
    return nums


def diff_maps(old, new):
    old, new = old or {}, new or {}
    result = {
        "added": {k: v for k, v in new.items() if k not in old},
        "removed": {k: v for k, v in old.items() if k not in new},
        "changed": {k: {"from": old[k], "to": new[k]} for k in new if k in old and old[k] != new[k]},
    }
    return {k: v for k, v in result.items() if v}


def package_json_deps(text):
    if not text:
        return {}
    try:
        data = json.loads(text)
    except ValueError:
        return {}
    sections = ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
    return {s: data.get(s) or {} for s in sections}


def requirements_deps(text):
    deps = {}
    for line in (text or "").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        match = re.match(r"^([A-Za-z0-9_.\-\[\]]+)\s*(.*)$", line)
        if match:
            deps[match.group(1)] = match.group(2).strip() or "*"
    return deps


def dependency_changes(entries, base, head, cwd):
    changes = {}
    for entry in entries:
        path = entry["path"]
        name = os.path.basename(path)
        if name == "package.json":
            old = package_json_deps(show(base, path, cwd) if base else None)
            new = package_json_deps(show(head, path, cwd))
            for section in set(old) | set(new):
                delta = diff_maps(old.get(section), new.get(section))
                if delta:
                    changes.setdefault(path, {})[section] = delta
        elif re.match(r"requirements[^/]*\.txt$", name):
            old = requirements_deps(show(base, path, cwd) if base else None)
            new = requirements_deps(show(head, path, cwd))
            delta = diff_maps(old, new)
            if delta:
                changes.setdefault(path, {})["requirements"] = delta
    return changes


def section_version(text, sections):
    current = None
    for line in text.splitlines():
        header = re.match(r"^\[([^\]]+)\]\s*$", line)
        if header:
            current = header.group(1)
            continue
        if current in sections:
            match = re.match(r"^version\s*=\s*[\"']([^\"']+)[\"']", line)
            if match:
                return match.group(1)
    return None


def manifest_versions(head, cwd):
    found = {}
    files = git("ls-files", cwd=cwd).splitlines() if head == "HEAD" else git(
        "ls-tree", "-r", "--name-only", head, cwd=cwd
    ).splitlines()
    candidates = [f for f in files if re.search(r"(^|/)(package\.json|pyproject\.toml|Cargo\.toml)$|\.csproj$", f)]
    for path in candidates[:20]:
        text = show(head, path, cwd)
        if not text:
            continue
        name = os.path.basename(path)
        version = None
        if name == "package.json":
            try:
                version = json.loads(text).get("version")
            except ValueError:
                pass
        elif name == "pyproject.toml":
            version = section_version(text, {"project", "tool.poetry"})
        elif name == "Cargo.toml":
            version = section_version(text, {"package"})
        else:
            match = re.search(r"<Version>([^<]+)</Version>", text)
            version = match.group(1) if match else None
        if version:
            found[path] = version
    return found


def major_of(spec):
    match = re.search(r"(\d+)\.", spec or "")
    return int(match.group(1)) if match else None


def build_hints(groups, entries, deps, commit_summary):
    hints = []
    if commit_summary["breaking"]:
        hints.append(f"{commit_summary['breaking']} commit(s) marcados como breaking change.")
    if groups.get("migrations"):
        hints.append("Migrations/SQL alterados: verifique compatibilidade de dados e plano de rollback.")
    if groups.get("api_contracts"):
        hints.append("Contratos de API alterados (OpenAPI/proto/GraphQL): compare com a versão anterior.")
    removed_source = [e["path"] for e in entries if e["status"] == "D" and categorize(e["path"]) == "source"]
    if removed_source:
        hints.append(f"{len(removed_source)} arquivo(s) de código removidos: possível remoção de API pública.")
    if groups.get("config_env"):
        hints.append("Arquivos de configuração/ambiente alterados: procure variáveis novas ou renomeadas.")
    for path, sections in deps.items():
        for section, delta in sections.items():
            for lib, change in delta.get("changed", {}).items():
                before, after = major_of(change["from"]), major_of(change["to"])
                if before is not None and after is not None and before != after:
                    hints.append(f"{path}: {lib} mudou de major ({before} -> {after}).")
            if delta.get("removed"):
                hints.append(f"{path}: dependências removidas em {section}: {', '.join(delta['removed'])}.")
    non_doc = [g for g in groups if g not in ("docs", "tests") and groups[g]]
    if entries and not non_doc:
        hints.append("Só documentação/testes mudaram: provavelmente não exige nova versão.")
    return hints


def facts(base=None, head="HEAD", cwd=None):
    commits = collect(base, head, cwd, with_files=False)
    base_ref = commits["range"]["base"]
    entries = name_status(base_ref, head, cwd)
    groups = {}
    for entry in entries:
        groups.setdefault(categorize(entry["path"]), []).append(entry["path"])
    deps = dependency_changes(entries, base_ref, head, cwd)
    branch = git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd, check=False).strip()
    return {
        "branch": branch,
        "range": commits["range"],
        "repo_url": commits["repo_url"],
        "commits": {
            **commits["summary"],
            "breaking_commits": [
                {"short": c["short"], "subject": c["raw_subject"], "note": c["breaking_note"]}
                for c in commits["commits"]
                if c["breaking"]
            ],
        },
        "diff": {**shortstat(base_ref, head, cwd), "by_status": _count(entries)},
        "changed_files": groups,
        "removed_files": [e["path"] for e in entries if e["status"] == "D"],
        "dependency_changes": deps,
        "manifest_versions": manifest_versions(head, cwd),
        "hints": build_hints(groups, entries, deps, commits["summary"]),
    }


def _count(entries):
    counts = {}
    for entry in entries:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", help="referência inicial (padrão: última tag)")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args(argv)
    json.dump(facts(args.base, args.head, args.repo), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
