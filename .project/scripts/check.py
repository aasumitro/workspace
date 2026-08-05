#!/usr/bin/env python3
"""Validate the workspace: rules in sync, structure intact, references resolve, tasks prescriptive.

Usage:
    python .project/scripts/check.py          # report problems, exit 1 if any
    python .project/scripts/check.py --fix    # rewrite the core-rules block in the entry files
    python .project/scripts/check.py --kb     # also print knowledge-base completion status

Checks:
  1. core-rules  — the block in CLAUDE.md and GEMINI.md matches AGENTS.md exactly
  2. structure   — every file the startup sequence depends on exists
  3. references  — every relative link and backticked path in a .md file resolves
  4. removed     — no reference to a path this workspace deliberately does not have
  5. tasks       — no design decisions left in the Steps of an active TASK doc
     (text inside backticks is ignored, so a file/symbol name like `Choose.svelte`
     or `Explore.test.ts` never counts as a hedge word)
  6. adoption    — if MANIFEST says adopted, no knowledge doc is still an authoring
     guide, AND MANIFEST.yaml itself has no leftover {{placeholder}}
  7. context     — every path listed in a .project/context/*.yaml profile
     (required: or optional:) resolves under knowledge/
"""
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent  # .project/
ROOT = PROJECT.parent                             # workspace root

BEGIN = "<!-- BEGIN CORE-RULES"
END = "<!-- END CORE-RULES -->"
ENTRY_FILES = ["CLAUDE.md", "GEMINI.md"]

REQUIRED = [
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", "COMMIT.md", "README.md",
    ".project/MANIFEST.yaml", ".project/PROMPTS.md",
    ".project/roles/README.md",
    ".project/knowledge/README.md",
    ".project/context/README.md",
    ".project/memory/README.md",
    ".project/work/STATE.md", ".project/work/active", ".project/work/archive",
    ".project/work/archive/INDEX.md",
    ".project/scripts/new-doc.py", ".project/scripts/check.py",
    ".project/scripts/close-iteration.py",
]

# Paths removed in the template's own v3 redesign. A reference to one means a stale
# doc left over from an old clone of this template itself — this list is template
# maintenance, not something a project adopting Workspace should add to. If you are
# customizing this workspace for your own project, leave this list alone; it has
# nothing to do with your code.
REMOVED = [
    "CODEX.md", "DEEPSEEK.md", "SETUP.md", "USAGE.md",
    "knowledge/design", "knowledge/glossary", "knowledge/modules",
    "knowledge/workflows", "roadmap/future", "roadmap/futures",
    ".project/runtime", ".project/cache", ".project/prompts/", "{project_code}",
    "index-kbase.py", "generate-task.py", "validate-links.py",
]

# Vocabulary that means a decision was left for implementation time. A PLAN is where
# decisions happen; a TASK translates a settled plan into verifiable steps. Mechanical
# discovery ("grep every call site") is fine — deciding is not.
HEDGE_PHRASES = [
    r"check\s+(?:if|whether)", r"see\s+if", r"look\s+into", r"figure\s+out",
    r"\bdecide\b", r"\bdetermine\b", r"\bchoose\b", r"\bconsider\b", r"\binvestigate\b",
    r"\bexplore\b", r"\bevaluate\s+(?:whether|if|options)", r"pick\s+(?:the|a|one|whether)",
    r"if\s+(?:needed|necessary|possible|appropriate)", r"as\s+(?:needed|appropriate)",
    r"where\s+appropriate", r"handle\s+appropriately", r"fix\s+if",
    r"m(?:ay|ight)\s+need\s+to", r"\bTBD\b", r"\bsomehow\b", r"\betc\.", r"and\s+so\s+on",
]
HEDGE = re.compile("|".join(HEDGE_PHRASES), re.I)
CODE_SPAN = re.compile(r"`[^`]*`")


def strip_code_spans(line: str) -> str:
    """Blank out backtick-quoted spans before hedge-scanning a step.

    A step routinely names files and symbols in backticks — `Choose.svelte`,
    `Explore.test.ts`, `Decide.tsx` — that share spelling with a hedge word but are
    not one. Replacing each span with a same-length run of 'x' keeps line length and
    match offsets stable while removing it from consideration.
    """
    return CODE_SPAN.sub(lambda m: "x" * len(m.group(0)), line)


# Knowledge docs in the order the setup guide asks for them.
KB_PRIORITY = [
    ("architecture/README.md", "Orientation — read at the start of every session"),
    ("roadmap/scope.md", "What agents must not touch"),
    ("conventions/testing.md", "Quality gate for every change"),
    ("conventions/api.md", "API rules an engineer writes against"),
    ("MODULES.md", "Business-rule correctness in reviews"),
    ("conventions/database.md", "Schema and migration rules"),
    ("conventions/security.md", "The security review checklist"),
    ("GLOSSARY.md", "Domain terms"),
    ("roadmap/README.md", "Current state and priorities"),
    ("roadmap/backlog.md", "Deferred and declined work"),
]

SKIP_DIRS = {".git", "node_modules", "code", "archive"}
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+?)(?:#[^)]*)?\)")
TICK_REF = re.compile(r"`([\w./{}-]+(?:\.(?:md|ya?ml|py)|/))`")
PLACEHOLDER = re.compile(r"\{\{|XXX|NNNN?|<\w+>|\*")
EXTS = (".md", ".yaml", ".yml", ".py")


def markdown_files():
    for path in sorted(ROOT.rglob("*.md")):
        if SKIP_DIRS & set(path.relative_to(ROOT).parts):
            continue
        yield path


def rules_body(text: str, path: Path) -> str:
    start = text.find(BEGIN)
    end = text.find(END)
    if start == -1 or end == -1:
        sys.exit(f"error: {path.relative_to(ROOT)} has no CORE-RULES block")
    return text[text.index("\n", start) + 1:end]


def check_core_rules(fix: bool) -> list[str]:
    canonical = rules_body((ROOT / "AGENTS.md").read_text(encoding="utf-8"), ROOT / "AGENTS.md")
    problems = []
    for name in ENTRY_FILES:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        if rules_body(text, path) == canonical:
            continue
        if fix:
            start = text.index("\n", text.find(BEGIN)) + 1
            path.write_text(text[:start] + canonical + text[text.find(END):], encoding="utf-8")
            print(f"fixed: synced core rules into {name}")
        else:
            problems.append(f"{name}: core-rules block differs from AGENTS.md (run --fix)")
    return problems


def check_structure() -> list[str]:
    return [f"missing required path: {rel}" for rel in REQUIRED if not (ROOT / rel).exists()]


def is_path_shaped(target: str) -> bool:
    """A workspace path reference, not a bare filename used in prose.

    `utils.py` and `tests/` are generic examples inside the language guides; only a
    reference with an interior slash (`knowledge/coding/`, `../work/archive/`) names
    something in this workspace. Bare stale names are caught by check_removed instead.
    """
    return "/" in target.rstrip("/") and (target.endswith(EXTS) or target.endswith("/"))


def references(text: str):
    for match in MD_LINK.finditer(text):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:", "file://", "#")):
            continue
        if is_path_shaped(target) and not PLACEHOLDER.search(target):
            yield target
    for match in TICK_REF.finditer(text):
        target = match.group(1)
        if is_path_shaped(target) and not PLACEHOLDER.search(target):
            yield target


def check_references() -> list[str]:
    problems = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for target in sorted(set(references(text))):
            bases = (path.parent, ROOT, PROJECT, PROJECT / "knowledge")
            if not any((base / target).exists() for base in bases):
                problems.append(f"{path.relative_to(ROOT)}: broken reference `{target}`")
    return problems


def check_removed() -> list[str]:
    problems = []
    for path in list(markdown_files()) + [PROJECT / "MANIFEST.yaml"]:
        if path.name == "check.py":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for gone in REMOVED:
            if gone in text:
                problems.append(f"{path.relative_to(ROOT)}: references removed path `{gone}`")
    return problems


def section(text: str, heading: str) -> str:
    """The body of one '## heading' section, up to the next '## '."""
    match = re.search(rf"^##\s+{heading}\s*$(.*?)(?=^##\s|\Z)", text, re.S | re.M)
    return match.group(1) if match else ""


def check_tasks() -> list[str]:
    """Steps in an active TASK must be prescriptive — the plan already decided."""
    problems = []
    for path in sorted((PROJECT / "work" / "active").glob("TASK-*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        steps = section(text, "Steps")
        if not steps.strip():
            problems.append(f"{path.relative_to(ROOT)}: no Steps section")
            continue
        for line in steps.splitlines():
            if "{{" in line or not line.strip():
                continue
            found = HEDGE.search(strip_code_spans(line))
            if found:
                problems.append(
                    f"{path.relative_to(ROOT)}: step leaves a decision to implementation "
                    f'("{found.group(0).strip()}") — decide it in the PLAN: {line.strip()[:70]}')
    return problems


def kb_docs() -> list[tuple[str, str, bool]]:
    """(relative path, why it matters, is it still an authoring guide)."""
    knowledge = PROJECT / "knowledge"
    rows = []
    for rel, why in KB_PRIORITY:
        path = knowledge / rel
        if not path.exists():
            rows.append((rel, why, True))
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rows.append((rel, why, "AUTHORING GUIDE" in text or "{{" in text))
    return rows


MANIFEST_PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")


def manifest_placeholders(manifest: str) -> list[str]:
    """Every distinct {{placeholder}} still left in MANIFEST.yaml, in file order."""
    seen: list[str] = []
    for match in MANIFEST_PLACEHOLDER.finditer(manifest):
        if match.group(0) not in seen:
            seen.append(match.group(0))
    return seen


def check_adoption() -> list[str]:
    """A workspace claiming to be adopted must not still ship authoring guides or an
    unfilled MANIFEST.yaml.

    `checks:` in particular is what agents run before calling work done — a leftover
    `{{go test ./...}}` there means every "done" since adoption skipped real
    verification without anyone noticing.
    """
    manifest_path = PROJECT / "MANIFEST.yaml"
    manifest = manifest_path.read_text(encoding="utf-8")
    if not re.search(r"^\s*adopted:\s*true\s*$", manifest, re.M):
        return []
    problems = [f"MANIFEST says adopted: true but {rel} is still an authoring guide"
                for rel, _, pending in kb_docs() if pending]
    problems += [f"MANIFEST.yaml: adopted: true but placeholder `{ph}` is still unfilled"
                 for ph in manifest_placeholders(manifest)]
    return problems


CONTEXT_LIST_KEY = re.compile(r"^(required|optional):\s*$")
CONTEXT_LIST_ITEM = re.compile(r"^\s*-\s*(\S+)\s*$")


def parse_context_profile(text: str) -> tuple[list[str], list[str]]:
    """(required paths, optional paths) from a .project/context/*.yaml profile.

    Deliberately not a real YAML parser — the schema is exactly two flat lists, so a
    tiny line scanner keeps this dependency-free like the rest of the script. `#`
    lines are comments; anything before the first `required:`/`optional:` key
    (including the leading `# name.yaml — ...` header comment every profile starts
    with) is ignored.
    """
    required: list[str] = []
    optional: list[str] = []
    current: list[str] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key = CONTEXT_LIST_KEY.match(line)
        if key:
            current = required if key.group(1) == "required" else optional
            continue
        item = CONTEXT_LIST_ITEM.match(line)
        if item and current is not None:
            current.append(item.group(1))
    return required, optional


def check_context() -> list[str]:
    """Every path a context profile lists must exist under knowledge/ — a profile
    pointing at a renamed or deleted doc is worse than no profile at all."""
    ctx_dir = PROJECT / "context"
    if not ctx_dir.exists():
        return []
    knowledge = PROJECT / "knowledge"
    problems = []
    for path in sorted(ctx_dir.glob("*.yaml")):
        required, optional = parse_context_profile(path.read_text(encoding="utf-8"))
        for rel in required + optional:
            if not (knowledge / rel).exists():
                problems.append(
                    f"{path.relative_to(ROOT)}: profile references missing knowledge doc `{rel}`")
    return problems


def print_kb_status() -> None:
    rows = kb_docs()
    done = sum(1 for _, _, pending in rows if not pending)
    print(f"\nknowledge base: {done}/{len(rows)} priority docs written\n")
    for rel, why, pending in rows:
        print(f"  [{' ' if pending else 'x'}] {rel:<28} {why}")
    if done < len(rows):
        print("\n  fill these with PROMPTS.md -> \"Bootstrap the knowledge base\"")


def main() -> None:
    fix = "--fix" in sys.argv
    problems = (check_core_rules(fix) + check_structure()
                + check_references() + check_removed()
                + check_tasks() + check_adoption() + check_context())

    if "--kb" in sys.argv:
        print_kb_status()
        print()

    if problems:
        print(f"FAILED — {len(problems)} problem(s):\n")
        for problem in problems:
            print(f"  {problem}")
        sys.exit(1)

    print(f"ok: core rules in sync, structure complete, all references resolve "
          f"({len(list(markdown_files()))} markdown files checked)")


if __name__ == "__main__":
    main()
