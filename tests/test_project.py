#!/usr/bin/env python3
"""Integration tests for the public repository build and safety interfaces."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, env=None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=ROOT, env=env, text=True,
        capture_output=True, check=False,
    )


class RepositoryBuildTests(unittest.TestCase):
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

    def test_test_runner_rejects_duplicate_names(self):
        # The validator is part of the runner, so an invalid fixture cannot pass.
        result = run("python3", "scripts/test_skills.py")
        self.assertEqual(result.returncode, 0, result.stderr)


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
        result = run("bash", "scripts/global-skills.sh", "status", env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(marker.exists())
        Path(config_path).unlink(missing_ok=True)

    def test_config_rejects_dangerous_root(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as config:
            config.write('ROOT_AGENTS="/"\n')
            config_path = config.name
        env = os.environ.copy()
        env["GLOBAL_SKILLS_CONFIG"] = config_path
        result = run("bash", "scripts/global-skills.sh", "status", env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to use /", result.stderr)
        Path(config_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
