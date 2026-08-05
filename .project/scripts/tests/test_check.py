#!/usr/bin/env python3
"""Tests for check.py.

Stdlib only — no pytest/pip install required, so these run in any clone with no
setup. From the workspace root:

    python -m unittest discover -s .project/scripts/tests -v

Two groups:
  - Unit tests for the pure functions (no filesystem), including regression tests
    for the two bugs this test file was added alongside:
      * hedge words false-positiving on backtick-quoted file/symbol names
      * MANIFEST.yaml placeholders surviving adopted: true undetected
  - One integration smoke test that runs check.py against the real template tree,
    since ROOT/PROJECT in check.py are resolved from the script's own location —
    the template itself is the only "fixture" worth building for those checks.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import check  # noqa: E402


class TestHedgeCodeSpans(unittest.TestCase):
    """Regression tests: file/symbol names must never count as hedge words."""

    def test_component_names_do_not_false_positive(self):
        lines = [
            "- [ ] Update `Choose.svelte` to add a disabled prop — button greys out when true",
            "- [ ] Add unit test to `Explore.test.ts` — covers empty-results state",
            "- [ ] Rename `Decide.tsx` to `ConfirmDialog.tsx` — all imports updated",
        ]
        for line in lines:
            with self.subTest(line=line):
                self.assertIsNone(check.HEDGE.search(check.strip_code_spans(line)),
                                  f"false positive on backticked identifier: {line}")

    def test_genuine_hedges_are_still_caught_outside_code_spans(self):
        lines = [
            "- [ ] Check if the cache needs invalidating — update `cache.py`",
            "- [ ] Decide whether to paginate the response",
            "- [ ] Add a migration if needed for the schema change in `db.py`",
        ]
        for line in lines:
            with self.subTest(line=line):
                self.assertIsNotNone(check.HEDGE.search(check.strip_code_spans(line)),
                                     f"failed to catch a real hedge: {line}")

    def test_hedge_word_inside_backticks_is_ignored_but_prose_hedge_still_caught(self):
        # The identifier is backticked and must be ignored; the plain-prose "decide"
        # right after it is real prose and must still be caught.
        line = "- [ ] Rename `Decide.tsx` — decide the new file name before implementing"
        stripped = check.strip_code_spans(line)
        self.assertNotIn("Decide", stripped)          # code span was blanked
        self.assertIsNotNone(check.HEDGE.search(stripped))  # prose hedge still found

    def test_strip_code_spans_preserves_line_length(self):
        line = "- [ ] Update `Choose.svelte` and `Explore.test.ts` together"
        self.assertEqual(len(check.strip_code_spans(line)), len(line))


class TestManifestPlaceholders(unittest.TestCase):
    """Regression tests: adopted: true must not hide an unfilled MANIFEST.yaml."""

    def test_finds_each_distinct_placeholder_once(self):
        manifest = (
            "workspace:\n"
            "  name: \"{{project-name}}\"\n"
            "  adopted: true\n"
            "repos:\n"
            "  - name: \"{{repo-name}}\"\n"
            "    path: \"code/{{repo-name}}\"\n"
        )
        found = check.manifest_placeholders(manifest)
        self.assertEqual(found, ["{{project-name}}", "{{repo-name}}"])

    def test_no_placeholders_in_a_filled_manifest(self):
        manifest = (
            "workspace:\n"
            "  name: \"acme-billing\"\n"
            "  adopted: true\n"
            "repos:\n"
            "  - name: \"billing-api\"\n"
        )
        self.assertEqual(check.manifest_placeholders(manifest), [])

    def test_check_adoption_flags_unfilled_manifest_when_adopted_true(self):
        manifest = 'workspace:\n  adopted: true\nrepos:\n  - name: "{{repo-name}}"\n'
        # check_adoption() reads the real MANIFEST.yaml via PROJECT; exercise the
        # regex/placeholder logic it depends on directly instead of touching disk.
        self.assertTrue(re.search(r"^\s*adopted:\s*true\s*$", manifest, re.M))
        self.assertEqual(check.manifest_placeholders(manifest), ["{{repo-name}}"])

    def test_check_adoption_is_a_noop_while_not_adopted(self):
        # The real template ships with adopted: false — check_adoption() must not
        # report anything even though every knowledge doc is still an authoring
        # guide and MANIFEST.yaml is full of placeholders.
        self.assertEqual(check.check_adoption(), [])


class TestSectionExtraction(unittest.TestCase):
    def test_extracts_steps_section_up_to_next_heading(self):
        text = "# T\n\n## Steps\n- [ ] a\n- [ ] b\n\n## Verification\nsomething\n"
        steps = check.section(text, "Steps")
        self.assertIn("- [ ] a", steps)
        self.assertNotIn("Verification", steps)


class TestIsPathShaped(unittest.TestCase):
    def test_bare_filename_is_not_path_shaped(self):
        self.assertFalse(check.is_path_shaped("utils.py"))

    def test_workspace_relative_path_is_path_shaped(self):
        self.assertTrue(check.is_path_shaped("knowledge/coding/py/README.md"))


class TestContextProfiles(unittest.TestCase):
    """parse_context_profile() and check_context() — the .project/context/ system."""

    def test_parses_required_and_optional_lists(self):
        text = (
            "# frontend.yaml — context profile for frontend/UI work\n"
            "required:\n"
            "  - architecture/frontend.md\n"
            "  - conventions/user-interface.md\n"
            "optional:\n"
            "  - conventions/testing.md\n"
        )
        required, optional = check.parse_context_profile(text)
        self.assertEqual(required, ["architecture/frontend.md", "conventions/user-interface.md"])
        self.assertEqual(optional, ["conventions/testing.md"])

    def test_missing_optional_section_is_empty_list(self):
        required, optional = check.parse_context_profile("required:\n  - architecture/backend.md\n")
        self.assertEqual(required, ["architecture/backend.md"])
        self.assertEqual(optional, [])

    def test_comment_and_blank_lines_are_ignored(self):
        text = "# a header comment\n\nrequired:\n  - architecture/backend.md\n\n# trailing\n"
        required, optional = check.parse_context_profile(text)
        self.assertEqual(required, ["architecture/backend.md"])

    def test_check_context_flags_a_profile_pointing_at_a_missing_doc(self):
        ctx_dir = check.PROJECT / "context"
        scratch = ctx_dir / "_test_scratch.yaml"
        scratch.write_text("required:\n  - architecture/does-not-exist.md\n", encoding="utf-8")
        try:
            problems = check.check_context()
        finally:
            scratch.unlink()
        self.assertTrue(any("does-not-exist.md" in p for p in problems),
                         "check_context() did not flag a profile referencing a missing doc")

    def test_shipped_profiles_pass_check_context(self):
        # frontend.yaml and backend.yaml ship with the template — every path they
        # list must be real, or the profile is actively misleading.
        self.assertEqual(check.check_context(), [])


class TestStructure(unittest.TestCase):
    def test_context_and_memory_readmes_are_required(self):
        self.assertIn(".project/context/README.md", check.REQUIRED)
        self.assertIn(".project/memory/README.md", check.REQUIRED)

    def test_required_paths_all_exist_on_the_shipped_template(self):
        self.assertEqual(check.check_structure(), [])


class TestIntegrationSmoke(unittest.TestCase):
    """Runs the real script against the real template tree (adopted: false)."""

    def test_check_py_passes_on_the_shipped_template(self):
        root = SCRIPTS.parent.parent  # workspace root
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "check.py")],
            cwd=root, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok:", result.stdout)


if __name__ == "__main__":
    unittest.main()
