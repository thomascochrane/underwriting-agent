"""Validate and install authored skills, preserving local edits and prior versions."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

sys.path.insert(0, "/opt/hermes")
import hermes_yaml as yaml
from tools.skill_manager_tool import _validate_frontmatter

SOURCE = Path(__file__).parent / "skills"
CATEGORY = "zivoe-underwriting"
LEGACY_BASELINE = Path(__file__).with_name("skills-v0.1.0-baseline.json")


def validate(source: Path = SOURCE) -> list[Path]:
    paths = sorted(source.glob("*/SKILL.md"))
    if not paths:
        raise ValueError("No repository skills found")
    names = set()
    for path in paths:
        content = path.read_text(encoding="utf-8")
        error = _validate_frontmatter(content, new_skill=True)
        if error:
            raise ValueError(f"{path.parent.name}: {error}")
        fm = yaml.safe_load(content.split("---", 2)[1])
        name = fm["name"]
        if name != path.parent.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ValueError(f"Invalid skill name: {path.parent.name}")
        if name in names:
            raise ValueError(f"Duplicate skill name: {name}")
        names.add(name)
        if len(fm["description"]) > 60 or not fm["description"].endswith("."):
            raise ValueError(f"Invalid description: {name}")
        for heading in ("When to Use", "Prerequisites", "Procedure", "Pitfalls", "Verification"):
            if f"## {heading}" not in content:
                raise ValueError(f"{name}: missing section {heading}")
    return paths


def fingerprint(directory: Path) -> dict[str, str]:
    if directory.is_symlink():
        raise ValueError("Refusing a symlink skill directory")
    result = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError("Refusing a symlink inside a skill")
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def install(home: Path, source: Path = SOURCE) -> int:
    paths = validate(source)
    root = home / "skills"
    destination = root / CATEGORY
    registry = home / ".zivoe-underwriting-installed.json"
    backup_root = home / "skill-backups"
    if any(p.is_symlink() for p in (root, destination, registry, backup_root, backup_root / CATEGORY)):
        raise ValueError("Refusing a symlink installation path")
    known = json.loads(registry.read_text(encoding="utf-8")) if registry.exists() else {}
    legacy = json.loads(LEGACY_BASELINE.read_text(encoding="utf-8-sig")) if LEGACY_BASELINE.exists() else {}
    planned = []
    desired = {}
    for path in paths:
        name = path.parent.name
        target = destination / name
        current_source = fingerprint(path.parent)
        desired[name] = current_source
        for existing in root.glob(f"**/{name}/SKILL.md"):
            if existing != target / "SKILL.md":
                raise ValueError(f"Skill name already exists outside {CATEGORY}: {name}")
        if target.exists() or target.is_symlink():
            current = fingerprint(target)
            if current == current_source:
                continue
            previous = known.get(name)
            legacy_files = {key[len(name)+1:]: value for key, value in legacy.items() if key.startswith(name + "/")}
            if not ((previous and current == previous) or (legacy_files and current == legacy_files)):
                raise ValueError(f"Local skill differs: {name}; reconcile it before installing. Nothing overwritten.")
            if set(current) - set(current_source):
                raise ValueError(f"Skill file removal requires explicit migration: {name}")
            planned.append((path.parent, target, True))
        else:
            planned.append((path.parent, target, False))
    # Check all conflicts before any installation. Preserve every replaced tree.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    backup = backup_root / CATEGORY / stamp
    for src, target, replacing in planned:
        if replacing:
            shutil.copytree(target, backup / target.name)
    for src, target, replacing in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, target, dirs_exist_ok=replacing)
    home.mkdir(parents=True, exist_ok=True)
    temp = registry.with_name(registry.name + "." + uuid.uuid4().hex + ".tmp")
    temp.write_text(json.dumps({**known, **desired}, indent=2) + "\n", encoding="utf-8")
    temp.replace(registry)
    return len(planned)


def verify(home: Path, source: Path = SOURCE) -> int:
    paths = validate(source)
    for path in paths:
        target = home / "skills" / CATEGORY / path.parent.name
        if fingerprint(target) != fingerprint(path.parent):
            raise ValueError(f"Installed skill differs or is missing: {path.parent.name}")
    return len(paths)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("check", "install", "verify"))
    args = parser.parse_args()
    home = Path(os.environ.get("HERMES_HOME", "/opt/data"))
    if args.action == "check":
        print(f"Validated {len(validate())} repository skills with the pinned Hermes validator.")
    elif args.action == "install":
        count = install(home)
        print(f"Installed or updated {count} skills; previous versions backed up and local edits protected.")
    else:
        print(f"Verified {verify(home)} installed skills match repository source.")


if __name__ == "__main__":
    main()