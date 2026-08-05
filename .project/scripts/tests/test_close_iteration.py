#!/usr/bin/env python3
"""Tests for close-iteration.py, run against a scratch .project/work/, never the
real one.

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


close_iter = load("close_iteration", "close-iteration.py")


def make_doc(path: Path, doc_id: str, title: str, status: str) -> None:
    path.write_text(
        f"---\nid: {doc_id}\ntitle: {title}\nstatus: {status}\nupdated: 2026-01-01\n---\n\n"
        f"# {doc_id} — {title}\n", encoding="utf-8")


class TempWorkspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        project = root / ".project"
        self.active = project / "work" / "active"
        self.archive = project / "work" / "archive"
        self.active.mkdir(parents=True)
        self.archive.mkdir(parents=True)

        self._orig = (close_iter.PROJECT, close_iter.ACTIVE, close_iter.ARCHIVE,
                      close_iter.INDEX)
        close_iter.PROJECT = project
        close_iter.ACTIVE = self.active
        close_iter.ARCHIVE = self.archive
        close_iter.INDEX = self.archive / "INDEX.md"

    def tearDown(self):
        (close_iter.PROJECT, close_iter.ACTIVE, close_iter.ARCHIVE,
         close_iter.INDEX) = self._orig
        self.tmp.cleanup()


class TestFieldParsing(unittest.TestCase):
    def test_reads_a_front_matter_field(self):
        text = "---\nid: TASK-001\ntitle: Something\nstatus: done\n---\nbody\n"
        self.assertEqual(close_iter.field(text, "status"), "done")
        self.assertEqual(close_iter.field(text, "id"), "TASK-001")

    def test_strips_trailing_comment(self):
        text = "---\nstatus: draft   # awaiting approval\n---\n"
        self.assertEqual(close_iter.field(text, "status"), "draft")

    def test_missing_field_returns_empty_string(self):
        text = "---\nid: TASK-001\n---\n"
        self.assertEqual(close_iter.field(text, "title"), "")


class TestSlugify(unittest.TestCase):
    def test_matches_new_doc_style(self):
        self.assertEqual(close_iter.slugify("Expiry Tracking"), "expiry-tracking")


class TestCollect(TempWorkspace):
    def test_only_done_docs_collected_by_default(self):
        make_doc(self.active / "TASK-001-a.md", "TASK-001", "A", "done")
        make_doc(self.active / "TASK-002-b.md", "TASK-002", "B", "active")
        docs, skipped = close_iter.collect(include_open=False)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0][1], "TASK-001")
        self.assertEqual(skipped, ["TASK-002 (active)"])

    def test_include_open_collects_everything(self):
        make_doc(self.active / "TASK-001-a.md", "TASK-001", "A", "done")
        make_doc(self.active / "TASK-002-b.md", "TASK-002", "B", "active")
        docs, skipped = close_iter.collect(include_open=True)
        self.assertEqual(len(docs), 2)
        self.assertEqual(skipped, [])


class TestMainBundling(TempWorkspace):
    def test_bundles_done_docs_and_leaves_open_ones(self):
        make_doc(self.active / "TASK-001-a.md", "TASK-001", "Ship it", "done")
        make_doc(self.active / "TASK-002-b.md", "TASK-002", "Still cooking", "active")

        import sys
        argv = sys.argv
        try:
            sys.argv = ["close-iteration.py", "expiry tracking"]
            close_iter.main()
        finally:
            sys.argv = argv

        bundles = list(self.archive.glob("*.zip"))
        self.assertEqual(len(bundles), 1)
        with zipfile.ZipFile(bundles[0]) as z:
            self.assertEqual(z.namelist(), ["TASK-001-a.md"])

        # done doc removed from active/, open doc left alone
        self.assertFalse((self.active / "TASK-001-a.md").exists())
        self.assertTrue((self.active / "TASK-002-b.md").exists())

        index = close_iter.INDEX.read_text(encoding="utf-8")
        self.assertIn("TASK-001", index)
        self.assertIn("Ship it", index)
        self.assertNotIn("TASK-002", index)

    def test_dry_run_makes_no_changes(self):
        make_doc(self.active / "TASK-001-a.md", "TASK-001", "Ship it", "done")
        import sys
        argv = sys.argv
        try:
            sys.argv = ["close-iteration.py", "expiry tracking", "--dry-run"]
            close_iter.main()
        finally:
            sys.argv = argv
        self.assertTrue((self.active / "TASK-001-a.md").exists())
        self.assertEqual(list(self.archive.glob("*.zip")), [])

    def test_nothing_to_archive_is_a_no_op(self):
        import sys
        argv = sys.argv
        try:
            sys.argv = ["close-iteration.py", "empty iteration"]
            close_iter.main()  # should just print and return, not raise
        finally:
            sys.argv = argv
        self.assertEqual(list(self.archive.glob("*.zip")), [])

    def test_refuses_to_overwrite_an_existing_bundle_same_day(self):
        make_doc(self.active / "TASK-001-a.md", "TASK-001", "First", "done")
        import sys
        argv = sys.argv
        try:
            sys.argv = ["close-iteration.py", "same label"]
            close_iter.main()
            make_doc(self.active / "TASK-002-b.md", "TASK-002", "Second", "done")
            sys.argv = ["close-iteration.py", "same label"]
            with self.assertRaises(SystemExit):
                close_iter.main()
        finally:
            sys.argv = argv


if __name__ == "__main__":
    unittest.main()
