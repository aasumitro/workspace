#!/usr/bin/env python3
"""Tests for new-doc.py.

The script's own filename has a hyphen, so it is loaded via importlib rather than
a normal `import` statement. Every test works inside a temp directory — nothing
here touches the real workspace's .project/work/.

Run:
    python -m unittest discover -s .project/scripts/tests -v
"""
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


new_doc = load("new_doc", "new-doc.py")


class TempWorkspace(unittest.TestCase):
    """Points new_doc's module-level paths at a scratch dir for the duration of a test."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        project = root / ".project"
        (project / "templates").mkdir(parents=True)
        (project / "templates" / "task.md").write_text(
            "---\nid: TASK-000\ntitle: {{title}}\nstatus: draft\nupdated: {{YYYY-MM-DD}}\n"
            "---\n\n# TASK-000 — {{title}}\n", encoding="utf-8")
        (project / "templates" / "plan.md").write_text(
            "---\nid: PLAN-000\ntitle: {{title}}\nstatus: draft\nupdated: {{YYYY-MM-DD}}\n"
            "---\n", encoding="utf-8")

        self._orig = (new_doc.PROJECT, new_doc.ACTIVE, new_doc.ARCHIVE)
        new_doc.PROJECT = project
        new_doc.ACTIVE = project / "work" / "active"
        new_doc.ARCHIVE = project / "work" / "archive"

    def tearDown(self):
        new_doc.PROJECT, new_doc.ACTIVE, new_doc.ARCHIVE = self._orig
        self.tmp.cleanup()


class TestSlugify(unittest.TestCase):
    def test_lowercases_and_hyphenates(self):
        self.assertEqual(new_doc.slugify("Add Inventory Expiry Alerts"),
                          "add-inventory-expiry-alerts")

    def test_strips_punctuation(self):
        self.assertEqual(new_doc.slugify("Fix: the /login endpoint!"), "fix-the-login-endpoint")

    def test_empty_title_falls_back(self):
        self.assertEqual(new_doc.slugify("!!!"), "untitled")

    def test_truncates_to_60_chars(self):
        long_title = "x" * 100
        self.assertLessEqual(len(new_doc.slugify(long_title)), 60)


class TestNextSeq(TempWorkspace):
    def test_first_doc_is_001(self):
        self.assertEqual(new_doc.next_seq("TASK"), 1)

    def test_increments_past_loose_files_in_active(self):
        new_doc.ACTIVE.mkdir(parents=True, exist_ok=True)
        (new_doc.ACTIVE / "TASK-004-something.md").write_text("x", encoding="utf-8")
        self.assertEqual(new_doc.next_seq("TASK"), 5)

    def test_considers_ids_inside_archive_zips(self):
        new_doc.ARCHIVE.mkdir(parents=True, exist_ok=True)
        bundle = new_doc.ARCHIVE / "2026-01-01-iteration.zip"
        with zipfile.ZipFile(bundle, "w") as z:
            z.writestr("TASK-009-old-work.md", "x")
        self.assertEqual(new_doc.next_seq("TASK"), 10)

    def test_ignores_unreadable_zip_instead_of_crashing(self):
        new_doc.ARCHIVE.mkdir(parents=True, exist_ok=True)
        (new_doc.ARCHIVE / "corrupt.zip").write_text("not actually a zip", encoding="utf-8")
        # Should not raise, and should fall back to whatever loose files say.
        self.assertEqual(new_doc.next_seq("TASK"), 1)

    def test_different_prefixes_are_independent(self):
        new_doc.ACTIVE.mkdir(parents=True, exist_ok=True)
        (new_doc.ACTIVE / "TASK-007-x.md").write_text("x", encoding="utf-8")
        (new_doc.ACTIVE / "PLAN-002-y.md").write_text("y", encoding="utf-8")
        self.assertEqual(new_doc.next_seq("TASK"), 8)
        self.assertEqual(new_doc.next_seq("PLAN"), 3)


class TestMainCreatesStampedDoc(TempWorkspace):
    def test_creates_file_with_id_title_and_date_stamped(self):
        import sys as _sys
        argv = _sys.argv
        try:
            _sys.argv = ["new-doc.py", "task", "Add inventory expiry alerts"]
            new_doc.main()
        finally:
            _sys.argv = argv

        created = list(new_doc.ACTIVE.glob("TASK-001-*.md"))
        self.assertEqual(len(created), 1)
        text = created[0].read_text(encoding="utf-8")
        self.assertIn("id: TASK-001", text)
        self.assertIn("title: Add inventory expiry alerts", text)
        self.assertNotIn("{{title}}", text)
        self.assertNotIn("{{YYYY-MM-DD}}", text)

    def test_refuses_to_overwrite_an_existing_doc(self):
        import sys as _sys
        argv = _sys.argv
        orig_next_seq = new_doc.next_seq
        try:
            # Pin next_seq so two calls collide on the same ID+slug, the way they
            # would if next_seq's own bookkeeping ever regressed.
            new_doc.next_seq = lambda prefix: 1
            _sys.argv = ["new-doc.py", "task", "Duplicate title"]
            new_doc.main()
            with self.assertRaises(SystemExit):
                new_doc.main()
        finally:
            new_doc.next_seq = orig_next_seq
            _sys.argv = argv


if __name__ == "__main__":
    unittest.main()
