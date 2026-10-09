"""Offline tests of skill installation and protection of runtime customizations."""
from pathlib import Path
import tempfile
import re
import unittest

import skills


class SkillInstallationTests(unittest.TestCase):
    def test_install_and_repeat_preserve_other_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            other = home / "skills" / "unrelated" / "SKILL.md"
            other.parent.mkdir(parents=True)
            other.write_text("keep this customization")
            count = len(skills.validate())
            self.assertEqual(skills.install(home), count)
            self.assertEqual(skills.install(home), 0)
            self.assertEqual(skills.verify(home), count)
            self.assertEqual(other.read_text(), "keep this customization")

    def test_conflict_is_detected_before_any_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            paths = skills.validate()
            conflicting = home / "skills" / skills.CATEGORY / paths[-1].parent.name / "SKILL.md"
            conflicting.parent.mkdir(parents=True)
            conflicting.write_text("user edited this")
            before = sorted(str(p.relative_to(home)) for p in home.rglob("*"))
            with self.assertRaisesRegex(ValueError, "Local skill differs"):
                skills.install(home)
            self.assertEqual(sorted(str(p.relative_to(home)) for p in home.rglob("*")), before)
            self.assertEqual(conflicting.read_text(), "user edited this")

    def test_invalid_skill_cannot_be_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source"
            bad = source / "broken" / "SKILL.md"
            bad.parent.mkdir(parents=True)
            bad.write_text("no frontmatter")
            with self.assertRaises(ValueError):
                skills.install(base / "home", source)
            self.assertFalse((base / "home").exists())

    def test_name_collision_preserves_existing_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            first = skills.validate()[0]
            existing = home / "skills" / "another-category" / first.parent.name / "SKILL.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("existing skill")
            with self.assertRaisesRegex(ValueError, "already exists"):
                skills.install(home)
            self.assertFalse((home / "skills" / skills.CATEGORY).exists())



    def test_managed_upgrade_backs_up_previous_version(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source"
            shutil.copytree(skills.SOURCE, source)
            home = base / "home"
            skills.install(home, source)
            first = skills.validate(source)[0]
            old = first.read_bytes()
            first.write_text(re.sub(r"(?m)^version: .+$", "version: 999.0.0", first.read_text(), count=1))
            self.assertEqual(skills.install(home, source), 1)
            self.assertEqual(skills.verify(home, source), len(skills.validate(source)))
            backups = list((home / "skill-backups").glob(f"**/{first.parent.name}/SKILL.md"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), old)

    def test_managed_local_edit_blocks_all_upgrades(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source"
            shutil.copytree(skills.SOURCE, source)
            home = base / "home"
            skills.install(home, source)
            paths = skills.validate(source)
            target = home / "skills" / skills.CATEGORY / paths[-1].parent.name / "SKILL.md"
            target.write_text(target.read_text() + "\nLocal customization\n")
            before = skills.fingerprint(home / "skills")
            for path in paths:
                path.write_text(re.sub(r"(?m)^version: .+$", "version: 999.0.0", path.read_text(), count=1))
            with self.assertRaisesRegex(ValueError, "Local skill differs"):
                skills.install(home, source)
            self.assertEqual(skills.fingerprint(home / "skills"), before)
            self.assertFalse((home / "skill-backups").exists())

    def test_legacy_upgrade_checks_exact_hash(self):
        import hashlib
        import json
        import shutil
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source"
            shutil.copytree(skills.SOURCE, source)
            first = skills.validate(source)[0]
            home = base / "home"
            target = home / "skills" / skills.CATEGORY / first.parent.name / "SKILL.md"
            target.parent.mkdir(parents=True)
            old = re.sub(r"(?m)^version: .+$", "version: 0.1.0", first.read_text(), count=1).encode()
            target.write_bytes(old)
            baseline = base / "baseline.json"
            baseline.write_text(json.dumps({f"{first.parent.name}/SKILL.md": hashlib.sha256(old).hexdigest()}))
            with patch.object(skills, "LEGACY_BASELINE", baseline):
                skills.install(home, source)
            self.assertEqual(skills.verify(home, source), len(skills.validate(source)))
            backup = next((home / "skill-backups").glob(f"**/{first.parent.name}/SKILL.md"))
            self.assertEqual(backup.read_bytes(), old)


if __name__ == "__main__":
    unittest.main()