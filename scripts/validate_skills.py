#!/usr/bin/env python3
"""Valida as skills de .agents/skills contra a especificação Agent Skills.

Checa: frontmatter (campos permitidos, formato do name, limites de tamanho),
corpo com no máximo 500 linhas, links relativos existentes, referências a outras
skills e a scripts existentes. Só usa a biblioteca padrão.

Uso: python scripts/validate_skills.py [CAMINHO_DAS_SKILLS]
Saída: 0 se tudo certo; 1 se houver erro.
Especificação: https://agentskills.io/specification
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_BODY_LINES = 500
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
SCRIPT_RE = re.compile(r"\.agents/skills/([a-z0-9-]+)/(scripts/[\w.\-]+)")


def parse_frontmatter(text):
    """Lê o frontmatter YAML. Usa PyYAML se existir; senão um leitor mínimo do subconjunto usado."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None, text
    raw, body = match.group(1), text[match.end():]
    try:
        import yaml  # type: ignore

        return yaml.safe_load(raw), body
    except ImportError:
        pass
    data, current = {}, None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            if current is None or not isinstance(data.get(current), dict):
                continue
            key, _, value = line.strip().partition(":")
            data[current][key.strip()] = value.strip().strip("\"'")
        else:
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            if value == "":
                data[key], current = {}, key
            else:
                data[key], current = value.strip("\"'"), None
    return data, body


def strip_code(text):
    """Remove blocos e trechos de código: o que está neles não é link de verdade."""
    text = re.sub(r"(?ms)^```.*?^```", "", text)
    return re.sub(r"(`+)[^\n]+?\1", "", text)


def validate_skill(skill_dir: Path, known_skills: set, skills_root: Path):
    errors, warnings = [], []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir.name}: falta SKILL.md"], warnings
    text = skill_md.read_text(encoding="utf-8")
    front, body = parse_frontmatter(text)
    where = skill_dir.name
    if not isinstance(front, dict):
        return [f"{where}: frontmatter ausente ou inválido"], warnings

    unknown = set(front) - ALLOWED_KEYS
    if unknown:
        errors.append(f"{where}: campos fora da especificação: {sorted(unknown)}")

    name = front.get("name")
    if not isinstance(name, str) or not name:
        errors.append(f"{where}: 'name' obrigatório")
    else:
        if len(name) > 64 or not NAME_RE.match(name):
            errors.append(f"{where}: 'name' inválido ({name!r}): use a-z, 0-9 e hífens, até 64 caracteres")
        if name != skill_dir.name:
            errors.append(f"{where}: 'name' ({name}) deve ser igual ao nome da pasta")

    description = front.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{where}: 'description' obrigatória")
    else:
        if len(description) > 1024:
            errors.append(f"{where}: 'description' tem {len(description)} caracteres (máximo 1024)")
        if not re.search(r"\b[Uu]se\b|\b[Uu]sar\b|\b[Qq]uando\b", description):
            warnings.append(f"{where}: a description deveria dizer quando usar a skill")

    compat = front.get("compatibility")
    if compat is not None and (not isinstance(compat, str) or not 1 <= len(compat) <= 500):
        errors.append(f"{where}: 'compatibility' deve ter entre 1 e 500 caracteres")

    metadata = front.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict) or not all(isinstance(v, str) for v in metadata.values()):
            errors.append(f"{where}: 'metadata' deve mapear texto para texto (ponha a versão entre aspas)")

    body_lines = body.count("\n") + 1
    if body_lines > MAX_BODY_LINES:
        errors.append(f"{where}: SKILL.md tem {body_lines} linhas (máximo recomendado {MAX_BODY_LINES})")

    for target in LINK_RE.findall(strip_code(body)):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = target.split("#", 1)[0]
        if path and not (skill_dir / path).exists():
            errors.append(f"{where}: link quebrado: {target}")

    for token in BACKTICK_RE.findall(body):
        if re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*-agent|release-flow", token) and token not in known_skills:
            errors.append(f"{where}: referência a skill inexistente: `{token}`")

    for skill, rel in SCRIPT_RE.findall(body):
        if not (skills_root / skill / rel).is_file():
            errors.append(f"{where}: script citado não existe: .agents/skills/{skill}/{rel}")

    return errors, warnings


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    root = Path(argv[0]) if argv else Path(__file__).resolve().parent.parent / ".agents" / "skills"
    if not root.is_dir():
        print(f"erro: pasta de skills não encontrada: {root}", file=sys.stderr)
        return 1
    skill_dirs = sorted(p for p in root.iterdir() if p.is_dir())
    known = {p.name for p in skill_dirs}
    all_errors, all_warnings = [], []
    for skill_dir in skill_dirs:
        errors, warnings = validate_skill(skill_dir, known, root)
        all_errors += errors
        all_warnings += warnings
        status = "ERRO" if errors else "ok"
        print(f"[{status}] {skill_dir.name}")
    for warning in all_warnings:
        print(f"aviso: {warning}")
    for error in all_errors:
        print(f"erro: {error}", file=sys.stderr)
    print(f"\n{len(skill_dirs)} skill(s), {len(all_errors)} erro(s), {len(all_warnings)} aviso(s)")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
