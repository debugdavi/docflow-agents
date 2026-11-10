"""Testa o validador de skills e o instalador.

Rodar: python -m unittest discover -s tests -v
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / "scripts" / "validate_skills.py"
INSTALL = ROOT / "scripts" / "install.py"


def run(script, *args):
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)


def make_skill(root, name, frontmatter, body="# T\n"):
    folder = Path(root) / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{body}", encoding="utf-8")
    return folder


class ValidateSkillsTests(unittest.TestCase):
    def test_skills_do_repositorio_sao_validas(self):
        result = run(VALIDATE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_detecta_name_diferente_da_pasta(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp, "pasta-certa", "name: outro-nome\ndescription: Use quando precisar.")
            result = run(VALIDATE, tmp)
            self.assertEqual(result.returncode, 1)
            self.assertIn("igual ao nome da pasta", result.stderr)

    def test_detecta_campo_fora_da_especificacao_e_name_invalido(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp, "Ruim_Nome", "name: Ruim_Nome\ndescription: Use quando precisar.\nfoo: bar")
            result = run(VALIDATE, tmp)
            self.assertEqual(result.returncode, 1)
            self.assertIn("fora da especificação", result.stderr)
            self.assertIn("'name' inválido", result.stderr)

    def test_detecta_link_quebrado_e_skill_inexistente(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(
                tmp, "boa-skill", "name: boa-skill\ndescription: Use quando precisar.",
                body="Veja [x](references/nao-existe.md) e a skill `fantasma-agent`.\n",
            )
            result = run(VALIDATE, tmp)
            self.assertEqual(result.returncode, 1)
            self.assertIn("link quebrado", result.stderr)
            self.assertIn("skill inexistente", result.stderr)

    def test_detecta_description_longa_demais(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp, "longa", "name: longa\ndescription: " + "Use " + "x" * 1100)
            result = run(VALIDATE, tmp)
            self.assertEqual(result.returncode, 1)
            self.assertIn("máximo 1024", result.stderr)


class InstallTests(unittest.TestCase):
    def test_instala_em_projeto_e_e_idempotente(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = run(INSTALL, tmp, "--copy")
            self.assertEqual(first.returncode, 0, first.stderr)
            project = Path(tmp)
            for name in ("release-flow", "changelog-agent", "version-agent", "readme-agent",
                         "github-pr-agent", "github-release-agent"):
                self.assertTrue((project / ".agents" / "skills" / name / "SKILL.md").is_file(), name)
                self.assertTrue((project / ".claude" / "skills" / name / "SKILL.md").is_file(), name)
            self.assertTrue((project / ".release-rules.example.md").is_file())
            self.assertIn(".release/", (project / ".gitignore").read_text(encoding="utf-8"))

            second = run(INSTALL, tmp, "--copy")
            self.assertEqual(second.returncode, 0)
            self.assertEqual((project / ".gitignore").read_text(encoding="utf-8").count(".release/"), 1)

    def test_cria_links_relativos_quando_possivel(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run(INSTALL, tmp).returncode, 0)
            link = Path(tmp) / ".claude" / "skills" / "release-flow"
            self.assertTrue((link / "SKILL.md").is_file())
            if link.is_symlink():
                self.assertFalse(Path(link.readlink() if hasattr(link, "readlink") else "").is_absolute())

    def test_sem_destino_falha_com_mensagem(self):
        result = run(INSTALL)
        self.assertEqual(result.returncode, 1)
        self.assertIn("informe a pasta do projeto", result.stderr)


if __name__ == "__main__":
    unittest.main()
