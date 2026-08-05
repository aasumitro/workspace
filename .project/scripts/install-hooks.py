#!/usr/bin/env python3
"""Install the Workspace git hooks.

Usage:
    python .project/scripts/install-hooks.py                    # into the workspace's own repo
    python .project/scripts/install-hooks.py --target-repo <p>  # into another repo, e.g. code/<name>

Optional, but recommended once `code/<name>` is a real repo you commit from — that
is almost always the repo that matters here, since it holds the code the checks
actually run against. Currently installs one hook:

    pre-commit  — runs this workspace's `check.py` before every commit, so a
                  workspace that is out of sync (core rules, broken references, an
                  unfilled MANIFEST.yaml marked adopted, a task with a leaked
                  decision) can't be committed by anyone — human or agent —
                  without noticing. Works no matter which repo the hook lives in:
                  the absolute path to *this* workspace's check.py is baked into
                  the installed hook at install time.

Safe to re-run; re-installing overwrites a previously installed copy of the same
hook but refuses to clobber a *different*, hand-written pre-commit hook you
already had (use --force to override that).
"""
import argparse
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent  # .project/
ROOT = PROJECT.parent
HOOKS_SRC = PROJECT / "scripts" / "hooks"
CHECK_PY = PROJECT / "scripts" / "check.py"
MARKER = "Workspace pre-commit hook"


def git_hooks_dir(target_repo: Path) -> Path:
    git_dir = target_repo / ".git"
    if not git_dir.is_dir():
        sys.exit(f"error: {git_dir} not found — {target_repo} is not a git repo root "
                  f"(run `git init` there first, or point --target-repo elsewhere)")
    return git_dir / "hooks"


def install_one(name: str, target_repo: Path, force: bool) -> str:
    src = HOOKS_SRC / name
    if not src.is_file():
        return f"skip: no source hook named {name}"
    dest = git_hooks_dir(target_repo) / name
    if dest.exists() and MARKER not in dest.read_text(encoding="utf-8", errors="replace"):
        if not force:
            return f"skip: {dest} already exists and is not a Workspace hook (use --force)"

    text = src.read_text(encoding="utf-8").replace("{{CHECK_PY}}", str(CHECK_PY.resolve()))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    dest.chmod(0o755)
    return f"installed: {dest} (runs {CHECK_PY.relative_to(ROOT)} from {ROOT})"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target-repo", default=str(ROOT),
                        help="git repo to install into (default: this workspace's own repo)")
    parser.add_argument("--force", action="store_true",
                        help="overwrite a pre-existing non-Workspace hook of the same name")
    args = parser.parse_args()
    target_repo = Path(args.target_repo).resolve()

    for name in sorted(p.name for p in HOOKS_SRC.iterdir() if p.is_file()):
        print(install_one(name, target_repo, args.force))


if __name__ == "__main__":
    main()
