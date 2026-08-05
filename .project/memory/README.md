# memory/ — cross-session continuity

`.project/work/STATE.md` is the live board: what's in flight *right now*. It is deliberately kept
to one screen and gets wiped clean as work finishes. `memory/` answers a different question — "what
should I know from before this session that STATE.md, being current-only, no longer says?" It is
not part of the mandatory startup sequence (`AGENTS.md` §1); read it only when you need it:

| File | Answers | Typically read by |
|---|---|---|
| `summary.md` | What is this project, in one paragraph, right now | Anyone resuming after a long gap |
| `recent.md` | What shipped in the last few iterations | `project-manager` sequencing next work |
| `hot-files.md` | Which files are fragile, high-traffic, or easy to break | `reviewer`, anyone about to touch one |
| `active-features.md` | What's in progress across *multiple* iterations, not just this week | `project-manager`, `product-strategist` |

**Why this doesn't duplicate `STATE.md`:** `STATE.md` tracks open work *docs* (`PLAN-*`, `TASK-*`)
for the current iteration and is reset as they close. `memory/` tracks the code- and
product-level facts that outlive any one doc — a file's blast radius doesn't stop being true when
the task that revealed it gets archived.

## Keeping it current

Refreshed at iteration close (`AGENTS.md` §5a, `.project/PROMPTS.md` → "Close the iteration") —
never mid-session. Update only what actually changed; an untouched file is not a stale one.
`recent.md` is a short rolling log — keep roughly the last 10 entries and drop the rest, they're
already in `work/archive/`. This folder is per-project state, not template machinery: it starts
near-empty and is written by the project, not shipped pre-filled.
