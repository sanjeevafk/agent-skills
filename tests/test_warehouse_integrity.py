"""Layout rules for the warehouse, driven by warehouse.toml."""
import filecmp
import glob
import os
import tomllib
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _manifest():
    with open(os.path.join(ROOT, "warehouse.toml"), "rb") as fh:
        return tomllib.load(fh)


def _same_tree(a, b):
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(_same_tree(os.path.join(a, d), os.path.join(b, d)) for d in cmp.common_dirs)


class TestWarehouseIntegrity(unittest.TestCase):
    def test_no_untracked_duplicates(self):
        """A real dir in skills/ that also exists in collections/ must be a declared fork."""
        forks = _manifest()["forks"]
        # Index all SKILL.md directories at any depth under collections/
        col_skills = {}
        for dirpath, _, filenames in os.walk(os.path.join(ROOT, "collections")):
            if "SKILL.md" in filenames:
                col_skills.setdefault(os.path.basename(dirpath), []).append(dirpath)

        for name in sorted(os.listdir(os.path.join(ROOT, "skills"))):
            local = os.path.join(ROOT, "skills", name)
            if os.path.islink(local) or not os.path.isdir(local):
                continue
            for up in col_skills.get(name, []):
                if _same_tree(local, up):
                    if name in forks:
                        self.fail(f"fork '{name}' is identical to upstream; symlink it and drop it from [forks]")
                    self.fail(f"skills/{name} duplicates {os.path.relpath(up, ROOT)}; replace with a symlink")
            for up in glob.glob(os.path.join(ROOT, "collections", "*", name)):
                if not os.path.isdir(up):
                    continue
                if name not in forks:
                    self.fail(f"skills/{name} diverges from {os.path.relpath(up, ROOT)}; add it to [forks] in warehouse.toml")

    def test_forks_still_exist(self):
        for name, upstream in _manifest()["forks"].items():
            self.assertTrue(os.path.isdir(os.path.join(ROOT, "skills", name)), name)
            self.assertTrue(os.path.isdir(os.path.join(ROOT, upstream)), upstream)

    def test_no_broken_symlinks(self):
        for name in os.listdir(os.path.join(ROOT, "skills")):
            p = os.path.join(ROOT, "skills", name)
            if os.path.islink(p):
                self.assertTrue(os.path.exists(p), f"skills/{name} is a broken symlink")


if __name__ == "__main__":
    unittest.main()
