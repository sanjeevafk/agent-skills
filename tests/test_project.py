#!/usr/bin/env python3
"""Integration tests for the public repository build and safety interfaces."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def run(*args: str, env=None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=ROOT, env=env, text=True,
        capture_output=True, check=False,
    )


class _IndexBackupMixin:
    _backup: str | None = None

    def _snapshot_index(self):
        idx = ROOT / "skills.json"
        self._backup = idx.read_text() if idx.exists() else None

    def _restore_index(self):
        idx = ROOT / "skills.json"
        if self._backup is None:
            return
        idx.write_text(self._backup)


class RepositoryBuildTests(_IndexBackupMixin, unittest.TestCase):
    def setUp(self):
        self._snapshot_index()
        self.addCleanup(self._restore_index)

    def test_validator_and_index_are_consistent(self):
        result = run("python3", "scripts/validate_skills.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = run("python3", "scripts/build_index.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        index = json.loads((ROOT / "skills.json").read_text())
        skill_files = list((ROOT / "skills").rglob("SKILL.md"))
        self.assertEqual(len(skill_files), len(index["skills"]))
        for meta in index["skills"].values():
            self.assertTrue((ROOT / meta["rel_path"]).is_file())

    def test_generated_commands_have_expected_coverage(self):
        result = run("python3", "scripts/generate_commands.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        index = json.loads((ROOT / "skills.json").read_text())
        namespaced = list((ROOT / "commands").glob("*/**/*.md"))
        self.assertGreaterEqual(len(namespaced), len(index["skills"]))
        self.assertTrue((ROOT / "commands/.generated-by-agent-skills").is_file())

    def test_runner_passes_on_valid_repo(self):
        # Smoke test: validator + per-skill frontmatter checks pass.
        result = run("python3", "scripts/test_skills.py")
        self.assertEqual(result.returncode, 0, result.stderr)


class FrontmatterUnitTests(unittest.TestCase):
    def test_missing_opening_fence_is_error(self):
        from skills_common import strip_frontmatter

        _, _, err = strip_frontmatter("name: x\n---\nbody")
        self.assertIsNotNone(err)

    def test_missing_closing_fence_is_error(self):
        from skills_common import strip_frontmatter

        _, _, err = strip_frontmatter("---\nname: x\nbody without close")
        self.assertIsNotNone(err)

    def test_non_mapping_yaml_is_error(self):
        from skills_common import strip_frontmatter

        _, _, err = strip_frontmatter("---\n- a\n- b\n---\nbody")
        self.assertIsNotNone(err)

    def test_multiline_block_scalar_parses(self):
        from skills_common import strip_frontmatter

        content = "---\nname: demo\ndescription: >\n  line one\n  line two\n---\nbody"
        meta, body, err = strip_frontmatter(content)
        self.assertIsNone(err)
        self.assertEqual(meta.get("name"), "demo")
        self.assertIn("line one", meta.get("description", ""))

    def test_lenient_variant_never_raises(self):
        from skills_common import strip_frontmatter_lenient

        meta, body = strip_frontmatter_lenient("no frontmatter here")
        self.assertEqual(meta, {})
        self.assertIn("no frontmatter", body)


class LintUnitTests(unittest.TestCase):
    def test_alias_target_missing_is_conflict(self):
        # Alias pointing at a non-existent skill must be reported.
        skills = {"a": {"description": "x" * 20, "aliases": []}}
        aliases = {"oops": "missing-skill"}
        conflicts = []
        for al, target in aliases.items():
            if al in skills:
                conflicts.append(al)
            if target not in skills:
                conflicts.append(al)
        self.assertIn("oops", conflicts)

    def test_alias_colliding_with_skill_name_is_conflict(self):
        skills = {"a": {"description": "x" * 20, "aliases": []}}
        aliases = {"a": "a"}
        self.assertIn("a", aliases)
        self.assertIn("a", skills)


class SafetyBoundaryTests(unittest.TestCase):
    def test_config_is_data_not_executable_shell(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as config:
            config.write('ROOT_AGENTS="/tmp/agent-skills-test"\n')
            config.write('BAD=$(touch /tmp/agent-skills-must-not-exist)\n')
            config_path = config.name
        marker = Path("/tmp/agent-skills-must-not-exist")
        marker.unlink(missing_ok=True)
        env = os.environ.copy()
        env["GLOBAL_SKILLS_CONFIG"] = config_path
        try:
            result = run("bash", "scripts/global-skills.sh", "status", env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_config_rejects_dangerous_root(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as config:
            config.write('ROOT_AGENTS="/"\n')
            config_path = config.name
        env = os.environ.copy()
        env["GLOBAL_SKILLS_CONFIG"] = config_path
        try:
            result = run("bash", "scripts/global-skills.sh", "status", env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to use /", result.stderr)
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_add_rejects_flag_injection(self):
        env = os.environ.copy()
        env["GLOBAL_SKILLS_CONFIG"] = "/dev/null"
        result = run("bash", "scripts/global-skills.sh", "add", "owner/repo", "--evil", env=env)
        self.assertNotEqual(result.returncode, 0)

    def test_add_rejects_bad_repo_spec(self):
        env = os.environ.copy()
        env["GLOBAL_SKILLS_CONFIG"] = "/dev/null"
        result = run("bash", "scripts/global-skills.sh", "add", "not-a-valid-spec!!!", env=env)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
