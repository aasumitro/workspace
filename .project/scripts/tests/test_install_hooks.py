#!/usr/bin/env python3
"""Tests for install-hooks.py.

Run:
    python -m unittest discover -s .project/scripts/tests -v
"""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


install_hooks = load("install_hooks", "install-hooks.py")


def init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)


class TestInstallOne(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name) / "target-repo"
        init_repo(self.target)

    def tearDown(self):
        self.tmp.cleanup()

    def test_bakes_absolute_check_py_path_into_installed_hook(self):
        msg = install_hooks.install_one("pre-commit", self.target, force=False)
        self.assertIn("installed", msg)
        installed = self.target / ".git" / "hooks" / "pre-commit"
        self.assertTrue(installed.exists())
        text = installed.read_text(encoding="utf-8")
        self.assertIn(str(install_hooks.CHECK_PY.resolve()), text)
        self.assertNotIn("{{CHECK_PY}}", text)

    def test_installed_hook_is_executable(self):
        install_hooks.install_one("pre-commit", self.target, force=False)
        installed = self.target / ".git" / "hooks" / "pre-commit"
        self.assertTrue(installed.stat().st_mode & 0o111)

    def test_refuses_to_clobber_a_foreign_hook_without_force(self):
        hooks_dir = self.target / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        foreign = hooks_dir / "pre-commit"
        foreign.write_text("#!/bin/sh\necho mine\n", encoding="utf-8")

        msg = install_hooks.install_one("pre-commit", self.target, force=False)
        self.assertIn("skip", msg)
        self.assertEqual(foreign.read_text(encoding="utf-8"), "#!/bin/sh\necho mine\n")

    def test_force_overwrites_a_foreign_hook(self):
        hooks_dir = self.target / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        (hooks_dir / "pre-commit").write_text("#!/bin/sh\necho mine\n", encoding="utf-8")

        msg = install_hooks.install_one("pre-commit", self.target, force=True)
        self.assertIn("installed", msg)

    def test_reinstalling_a_workspace_hook_never_needs_force(self):
        install_hooks.install_one("pre-commit", self.target, force=False)
        msg = install_hooks.install_one("pre-commit", self.target, force=False)
        self.assertIn("installed", msg)

    def test_errors_clearly_when_target_is_not_a_git_repo(self):
        not_a_repo = Path(self.tmp.name) / "plain-dir"
        not_a_repo.mkdir()
        with self.assertRaises(SystemExit):
            install_hooks.install_one("pre-commit", not_a_repo, force=False)


if __name__ == "__main__":
    unittest.main()
