#!/usr/bin/env python3
"""Create a work doc (plan/task/review/report) with the next free ID.

Usage:
    python .project/scripts/new-doc.py <plan|task|review|report> "<title>"

Scans work/active/ and work/archive/ — including inside archive zips — so IDs are
never reused, then stamps the template's front-matter (id / title / status / updated).
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

KINDS = {
    "plan":   {"prefix": "PLAN", "template": "templates/plan.md"},
    "task":   {"prefix": "TASK", "template": "templates/task.md"},
    "review": {"prefix": "RV",   "template": "templates/review.md"},
    "report": {"prefix": "RPT",  "template": "templates/report.md"},
}


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "untitled"


def next_seq(prefix: str) -> int:
    """Highest existing sequence + 1.

    Scans loose files in active/ and archive/ AND the contents of archive zips —
    close-iteration.py folds finished docs into zips, and an ID inside a zip is
    still taken. IDs are never reused.
    """
    pattern = re.compile(rf"^{prefix}-(\d+)")
    highest = 0

    def consider(name: str) -> None:
        nonlocal highest
        match = pattern.match(name)
        if match:
            highest = max(highest, int(match.group(1)))

    for directory in (ACTIVE, ARCHIVE):
        if not directory.is_dir():
            continue
        for path in directory.iterdir():
            consider(path.name)
            if path.suffix == ".zip":
                try:
                    with zipfile.ZipFile(path) as bundle:
                        for member in bundle.namelist():
                            consider(Path(member).name)
                except zipfile.BadZipFile:
                    print(f"warning: skipping unreadable archive {path.name}", file=sys.stderr)
    return highest + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=sorted(KINDS))
    parser.add_argument("title")
    args = parser.parse_args()

    kind = KINDS[args.kind]
    template = PROJECT / kind["template"]
    if not template.is_file():
        sys.exit(f"error: template not found: {template}")

    ACTIVE.mkdir(parents=True, exist_ok=True)
    doc_id = f"{kind['prefix']}-{next_seq(kind['prefix']):03d}"
    today = datetime.date.today().isoformat()

    text = template.read_text(encoding="utf-8")
    text = text.replace(f"{kind['prefix']}-000", doc_id)
    text = re.sub(r"^title: .*$", f"title: {args.title}", text, count=1, flags=re.M)
    text = re.sub(r"^updated: .*$", f"updated: {today}", text, count=1, flags=re.M)
    text = text.replace("{{title}}", args.title).replace("{{YYYY-MM-DD}}", today)

    out = ACTIVE / f"{doc_id}-{slugify(args.title)}.md"
    if out.exists():
        sys.exit(f"error: {out} already exists")
    out.write_text(text, encoding="utf-8")
    print(f"created {out.relative_to(PROJECT.parent)}  (id={doc_id})")


if __name__ == "__main__":
    main()
