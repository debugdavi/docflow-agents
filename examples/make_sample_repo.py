#!/usr/bin/env python3
"""Cria um repositório git de exemplo (tasks-api) para ensaiar o fluxo.

Autor e datas são fixos, então os hashes dos commits são os mesmos em qualquer máquina
e o passo a passo em examples/walkthrough.md pode citá-los.

Uso: python examples/make_sample_repo.py /caminho/novo/tasks-api
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

DATES = iter(f"2026-10-{day:02d}T12:00:00" for day in range(1, 29))
FIXED = {"GIT_AUTHOR_NAME": "Ana Dev", "GIT_AUTHOR_EMAIL": "ana@example.com",
         "GIT_COMMITTER_NAME": "Ana Dev", "GIT_COMMITTER_EMAIL": "ana@example.com"}


def git(repo, *args, date=None):
    env = {**os.environ, **FIXED}
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True)


def write(repo, rel, content):
    target = Path(repo) / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def commit(repo, subject, body=None, files=None, delete=()):
    for rel, content in (files or {}).items():
        write(repo, rel, content)
    for rel in delete:
        (Path(repo) / rel).unlink()
    git(repo, "add", "-A")
    args = ["commit", "-q", "-m", subject] + (["-m", body] if body else [])
    git(repo, *args, date=next(DATES))


def package(version, deps):
    return json.dumps({"name": "tasks-api", "version": version, "engines": {"node": ">=20"},
                       "scripts": {"start": "node src/index.js", "test": "node --test"},
                       "dependencies": deps}, indent=2) + "\n"


def main(dest):
    repo = Path(dest)
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "remote", "add", "origin", "git@github.com:acme/tasks-api.git")
    git(repo, "config", "commit.gpgsign", "false")

    commit(repo, "chore: estrutura inicial", files={
        "package.json": package("1.2.0", {"express": "^4.18.0"}),
        "README.md": "# tasks-api\n\nAPI de tarefas.\n",
        "src/index.js": "// servidor\n",
        "src/routes/v1/tasks.js": "// GET /v1/tasks\n",
        ".env.example": "PORT=3000\n",
    })
    git(repo, "tag", "-a", "v1.2.0", "-m", "v1.2.0", date=next(DATES))

    commit(repo, "feat(tasks): adiciona filtro por status (#12)",
           files={"src/routes/v2/tasks.js": "// GET /v2/tasks?status=\n"})
    commit(repo, "fix(tasks): corrige paginação que repetia itens (#13)",
           files={"src/pagination.js": "// paginação estável\n"})
    commit(repo, "refactor: extrai validação para módulo próprio",
           files={"src/validate.js": "// validação\n"})
    commit(repo, "feat(auth): aceita autenticação opcional por JWT (#14)",
           body="Usa JWT para manter a API sem estado e permitir escalar horizontalmente.",
           files={
               "package.json": package("1.2.0", {"express": "^4.18.0", "jsonwebtoken": "^9.0.2"}),
               ".env.example": "PORT=3000\nJWT_SECRET=YOUR_JWT_SECRET_HERE\n",
               "db/migrations/002_add_user_id.sql": "ALTER TABLE tasks ADD COLUMN user_id int;\n",
               "src/auth.js": "// verifica o token\n",
           })
    commit(repo, "feat(api)!: remove endpoint GET /v1/tasks (#15)",
           body="BREAKING CHANGE: use GET /v2/tasks, que agora devolve a resposta paginada.",
           delete=["src/routes/v1/tasks.js"])
    commit(repo, "chore(deps): atualiza express para 5.0 (#16)",
           body="Express 5 trata erros de rotas assíncronas nativamente.",
           files={"package.json": package("1.2.0", {"express": "^5.0.0", "jsonwebtoken": "^9.0.2"})})
    commit(repo, "docs: corrige link do README", files={"README.md": "# tasks-api\n\nAPI de tarefas.\nVeja /docs.\n"})
    commit(repo, "ci: cacheia dependências", files={".github/workflows/ci.yml": "name: ci\non: [push]\n"})
    print(f"repositório de exemplo criado em {repo}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
