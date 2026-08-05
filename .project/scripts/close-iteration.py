#!/usr/bin/env python3
"""Close an iteration: fold finished work docs into one dated archive zip.

Usage:
    python .project/scripts/close-iteration.py "<label>"
    python .project/scripts/close-iteration.py "<label>" --dry-run
    python .project/scripts/close-iteration.py "<label>" --include-open

Collects every `status: done` doc in work/active/ into
work/archive/<YYYY-MM-DD>-<label>.zip, removes the originals, and records what
went in to work/archive/INDEX.md so the bundle is searchable without unzipping.

Docs that are not done are left in active/ — an iteration boundary should not
swallow unfinished work. --include-open overrides that deliberately.

Run the knowledge-base sync FIRST (PROMPTS.md -> "Close the iteration"). This
script is the mechanical half; it does not update knowledge/ for you.
"""
import argparse
import datetime
import re
import sys
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent  # .project/
ACTIVE = PROJECT / "work" / "active"
ARCHIVE = PROJECT / "work" / "archive"
INDEX = ARCHIVE / "INDEX.md"

FRONT_MATTER = re.compile(r"^---\n(.*?)\n---", re.S)
INDEX_HEADER = """# Archive Index

Closed work, newest bundle first. Every iteration folds its finished docs into one
zip; this index lists what is inside each so you can find a doc without unzipping.

**History only.** Never read an archived doc to learn how something behaves today —
`../../knowledge/` is authoritative for current behavior.
"""


def field(text: str, name: str) -> str:
    """A front-matter value, with any trailing ` # comment` stripped."""
    match = FRONT_MATTER.search(text)
    if not match:
        return ""
    found = re.search(rf"^{name}:\s*(.+?)\s*$", match.group(1), re.M)
    if not found:
        return ""
    return re.sub(r"\s+#.*$", "", found.group(1)).strip()


def slugify(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:60] or "iteration"


def collect(include_open: bool) -> tuple[list[tuple[Path, str, str, str]], list[str]]:
    docs, skipped = [], []
    for path in sorted(ACTIVE.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        status = field(text, "status") or "unknown"
        doc_id = field(text, "id") or path.stem
        title = field(text, "title") or "-"
        if status == "done" or include_open:
            docs.append((path, doc_id, title, status))
        else:
            skipped.append(f"{doc_id} ({status})")
    return docs, skipped


def write_index(bundle_name: str, label: str, today: str,
                docs: list[tuple[Path, str, str, str]]) -> None:
    rows = "\n".join(f"| `{doc_id}` | {title} |" for _, doc_id, title, _ in docs)
    entry = (f"## {today} — {label}\n\n"
             f"`{bundle_name}` · {len(docs)} doc(s)\n\n"
             f"| Doc | Title |\n|---|---|\n{rows}\n")

    if INDEX.exists():
        existing = INDEX.read_text(encoding="utf-8")
        body = existing.split("\n## ", 1)
        head = body[0].replace("_(no iterations closed yet)_", "").rstrip("\n")
        rest = ("\n## " + body[1]) if len(body) > 1 else ""
        INDEX.write_text(f"{head}\n\n{entry}{rest}", encoding="utf-8")
    else:
        INDEX.write_text(f"{INDEX_HEADER}\n{entry}", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("label", help='what this iteration was, e.g. "expiry tracking"')
    parser.add_argument("--dry-run", action="store_true", help="show what would happen")
    parser.add_argument("--include-open", action="store_true",
                        help="also archive docs that are not done")
    args = parser.parse_args()

    if not ACTIVE.is_dir():
        sys.exit(f"error: {ACTIVE} does not exist")

    docs, skipped = collect(args.include_open)
    if not docs:
        print("nothing to archive: no finished docs in work/active/")
        if skipped:
            print("  still open: " + ", ".join(skipped))
        return

    today = datetime.date.today().isoformat()
    bundle_name = f"{today}-{slugify(args.label)}.zip"
    bundle = ARCHIVE / bundle_name

    if bundle.exists() and not args.dry_run:
        sys.exit(f"error: {bundle_name} already exists — pick another label")

    print(f"{'would archive' if args.dry_run else 'archiving'} {len(docs)} doc(s) "
          f"-> work/archive/{bundle_name}")
    for _, doc_id, title, status in docs:
        print(f"  {doc_id:<9} {title} [{status}]")
    if skipped:
        print("  left in active/: " + ", ".join(skipped))

    if args.dry_run:
        return

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, _, _, _ in docs:
            archive.write(path, arcname=path.name)

    with zipfile.ZipFile(bundle) as archive:
        stored = set(archive.namelist())
    missing = [p.name for p, _, _, _ in docs if p.name not in stored]
    if missing:
        sys.exit(f"error: bundle incomplete, originals kept: {', '.join(missing)}")

    for path, _, _, _ in docs:
        path.unlink()

    write_index(bundle_name, args.label, today, docs)
    print(f"\ndone. {len(docs)} doc(s) archived, originals removed, INDEX.md updated.")
    print("next: update work/STATE.md (focus, active work, next action), "
          "then run python .project/scripts/check.py")


if __name__ == "__main__":
    main()
