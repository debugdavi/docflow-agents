"""Testes dos scripts determinísticos (git real em repositórios temporários).

Rodar: python -m unittest discover -s tests -v
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / ".agents" / "skills" / "release-flow" / "scripts"


def load(name):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


collect_commits = load("collect_commits")
branch_facts = load("branch_facts")
extract_release_notes = load("extract_release_notes")


class Repo:
    """Repositório git temporário com helpers para criar commits e tags."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = self._tmp.name
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "teste@example.com")
        self.git("config", "user.name", "Teste")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args):
        result = subprocess.run(
            ["git", *args], cwd=self.path, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()

    def write(self, rel, content):
        target = Path(self.path) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def commit(self, subject, body=None, files=None):
        for rel, content in (files or {"f.txt": subject}).items():
            self.write(rel, content)
        self.git("add", "-A")
        message = [subject] + ([body] if body else [])
        args = ["commit", "-q"]
        for part in message:
            args += ["-m", part]
        self.git(*args)

    def cleanup(self):
        self._tmp.cleanup()


class CollectCommitsTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def test_sem_tag_lista_todo_o_historico(self):
        self.repo.commit("feat: primeira feature")
        self.repo.commit("fix(api): corrige erro (#7)")
        data = collect_commits.collect(cwd=self.repo.path)
        self.assertTrue(data["range"]["first_release"])
        self.assertEqual(data["summary"]["total"], 2)
        self.assertEqual(data["summary"]["by_type"], {"feat": 1, "fix": 1})

    def test_usa_ultima_tag_como_base(self):
        self.repo.commit("feat: antiga")
        self.repo.git("tag", "-a", "v1.0.0", "-m", "v1.0.0")
        self.repo.commit("fix: nova")
        data = collect_commits.collect(cwd=self.repo.path)
        self.assertEqual(data["range"]["base"], "v1.0.0")
        self.assertEqual([c["subject"] for c in data["commits"]], ["nova"])

    def test_head_ja_taggeado_volta_uma_tag(self):
        self.repo.commit("feat: a")
        self.repo.git("tag", "-a", "v1.0.0", "-m", "v1.0.0")
        self.repo.commit("feat: b")
        self.repo.git("tag", "-a", "v1.1.0", "-m", "v1.1.0")
        data = collect_commits.collect(cwd=self.repo.path)
        self.assertEqual(data["range"]["base"], "v1.0.0")
        self.assertEqual(data["range"]["head_is_tagged"], "v1.1.0")

    def test_detecta_breaking_por_bang_e_por_rodape(self):
        self.repo.commit("feat(api)!: remove endpoint antigo")
        self.repo.commit("feat: muda contrato", body="BREAKING CHANGE: use /v2/orders no lugar de /v1/orders")
        data = collect_commits.collect(cwd=self.repo.path)
        by_subject = {c["subject"]: c for c in data["commits"]}
        self.assertTrue(by_subject["remove endpoint antigo"]["breaking"])
        footer = by_subject["muda contrato"]
        self.assertTrue(footer["breaking"])
        self.assertIn("/v2/orders", footer["breaking_note"])
        self.assertEqual(data["summary"]["breaking"], 2)

    def test_rodape_so_aparece_com_body_completo(self):
        """--oneline esconde o rodapé; o coletor precisa ler o corpo."""
        self.repo.commit("fix: ajuste", body="BREAKING CHANGE: campo X removido")
        oneline = self.repo.git("log", "--oneline")
        self.assertNotIn("BREAKING", oneline)
        self.assertTrue(collect_commits.collect(cwd=self.repo.path)["commits"][0]["breaking"])

    def test_refs_escopo_e_nao_conventional(self):
        self.repo.commit("feat(auth): login com SSO (#42)", body="Closes #40")
        self.repo.commit("ajusta coisa sem padrão")
        data = collect_commits.collect(cwd=self.repo.path)
        by_raw = {c["raw_subject"]: c for c in data["commits"]}
        auth = by_raw["feat(auth): login com SSO (#42)"]
        self.assertEqual(auth["scope"], "auth")
        self.assertEqual(auth["pr_hint"], 42)
        self.assertEqual(auth["refs"], [40, 42])
        self.assertFalse(by_raw["ajusta coisa sem padrão"]["conventional"])
        self.assertEqual(data["summary"]["non_conventional"], 1)

    def test_lista_arquivos_por_commit(self):
        self.repo.commit("feat: x", files={"src/a.py": "1", "src/b.py": "2"})
        commit = collect_commits.collect(cwd=self.repo.path)["commits"][0]
        self.assertEqual(sorted(commit["files"]), ["src/a.py", "src/b.py"])

    def test_normalize_remote(self):
        norm = collect_commits.normalize_remote
        self.assertEqual(norm("git@github.com:dono/repo.git"), "https://github.com/dono/repo")
        self.assertEqual(norm("https://github.com/dono/repo.git"), "https://github.com/dono/repo")
        self.assertEqual(norm("https://user:token@github.com/dono/repo"), "https://github.com/dono/repo")
        self.assertEqual(norm("ssh://git@github.com/dono/repo.git"), "https://github.com/dono/repo")
        self.assertIsNone(norm(""))


class BranchFactsTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)
        self.repo.commit(
            "chore: base",
            files={
                "package.json": json.dumps(
                    {"name": "x", "version": "1.2.0", "dependencies": {"express": "^4.18.0", "lodash": "^4.0.0"}}
                ),
                "src/index.js": "module.exports = {}",
            },
        )
        self.repo.git("tag", "-a", "v1.2.0", "-m", "v1.2.0")

    def test_dependencias_migrations_e_hints(self):
        self.repo.commit(
            "feat: nova rota",
            files={
                "package.json": json.dumps(
                    {"name": "x", "version": "1.2.0", "dependencies": {"express": "^5.0.0", "zod": "^3.0.0"}}
                ),
                "db/migrations/001_add_col.sql": "ALTER TABLE t ADD c int;",
                "src/routes.js": "// nova rota",
            },
        )
        facts = branch_facts.facts(cwd=self.repo.path)
        deps = facts["dependency_changes"]["package.json"]["dependencies"]
        self.assertEqual(deps["added"], {"zod": "^3.0.0"})
        self.assertEqual(deps["removed"], {"lodash": "^4.0.0"})
        self.assertEqual(deps["changed"]["express"], {"from": "^4.18.0", "to": "^5.0.0"})
        self.assertIn("db/migrations/001_add_col.sql", facts["changed_files"]["migrations"])
        self.assertIn("package.json", facts["changed_files"]["manifests"])
        joined = " ".join(facts["hints"])
        self.assertIn("express mudou de major (4 -> 5)", joined)
        self.assertIn("Migrations", joined)
        self.assertEqual(facts["manifest_versions"]["package.json"], "1.2.0")
        self.assertEqual(facts["range"]["base"], "v1.2.0")

    def test_arquivo_removido_vira_dica_de_api_publica(self):
        (Path(self.repo.path) / "src" / "index.js").unlink()
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "refactor: remove entrada antiga")
        facts = branch_facts.facts(cwd=self.repo.path)
        self.assertEqual(facts["removed_files"], ["src/index.js"])
        self.assertTrue(any("API pública" in h for h in facts["hints"]))

    def test_so_docs_sugere_sem_nova_versao(self):
        self.repo.commit("docs: ajusta leitura", files={"README.md": "# x"})
        facts = branch_facts.facts(cwd=self.repo.path)
        self.assertTrue(any("provavelmente não exige nova versão" in h for h in facts["hints"]))

    def test_cli_emite_json_valido(self):
        self.repo.commit("fix: algo", files={"src/a.js": "1"})
        script = SCRIPTS / "branch_facts.py"
        out = subprocess.run(
            [sys.executable, str(script), "--repo", self.repo.path],
            capture_output=True, text=True, check=True,
        ).stdout
        self.assertEqual(json.loads(out)["commits"]["total"], 1)


class ExtractReleaseNotesTests(unittest.TestCase):
    CHANGELOG = (
        "# Changelog\n\n## [Unreleased]\n\n## [1.3.0] - 2026-11-10\n\n### Added\n- Item A\n\n"
        "## [1.2.0] - 2026-10-01\n\n### Fixed\n- Item B\n\n"
        "[Unreleased]: https://x/compare/v1.3.0...HEAD\n[1.3.0]: https://x/compare/v1.2.0...v1.3.0\n"
        "[1.2.0]: https://x/releases/tag/v1.2.0\n"
    )

    def test_extrai_secao_do_meio(self):
        notes = extract_release_notes.extract(self.CHANGELOG, "1.3.0")
        self.assertEqual(notes, "### Added\n- Item A")

    def test_ultima_secao_nao_leva_links_de_rodape(self):
        notes = extract_release_notes.extract(self.CHANGELOG, "v1.2.0")
        self.assertEqual(notes, "### Fixed\n- Item B")

    def test_versao_inexistente(self):
        self.assertIsNone(extract_release_notes.extract(self.CHANGELOG, "9.9.9"))

    def test_cli_codigos_de_saida(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHANGELOG.md"
            path.write_text(self.CHANGELOG, encoding="utf-8")
            script = str(SCRIPTS / "extract_release_notes.py")
            ok = subprocess.run([sys.executable, script, str(path), "1.3.0"], capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0)
            self.assertIn("Item A", ok.stdout)
            missing = subprocess.run([sys.executable, script, str(path), "0.0.1"], capture_output=True, text=True)
            self.assertEqual(missing.returncode, 2)


if __name__ == "__main__":
    unittest.main()
