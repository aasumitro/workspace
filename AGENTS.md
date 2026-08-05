# AGENTS.md — Workspace Manual

**This file is authoritative.** Every AI working in this workspace obeys it. Where any other
document disagrees with this one, this one wins.

Two AIs operate here:

| AI | Entry file | Standing |
|---|---|---|
| **Claude** | `CLAUDE.md` | **Primary.** Owns product thinking, planning, architecture, review, documentation, and every final decision. Implements too. |
| **Gemini** (Antigravity) | `GEMINI.md` | **Supporting.** Researches, explores alternatives, validates, gives second opinions, and implements assigned tasks. Never decides. |

The split is **decision authority, not capability.** Claude is the source of truth for
architecture and final calls; Gemini's output is input to Claude's decision, never a substitute
for it. But an `active` task carries no decisions — the plan settled them and `check.py` enforces
it — so **either AI can implement one.**

**Prefer Gemini implements, Claude reviews.** Claude reviewing its own code is the weakest gate in
this workspace; a reviewer who did not write the diff is a real one. Use that pairing whenever both
are available and the work matters.

---

## 1. Startup sequence — run this before anything else, every session

Three reads, one announcement. Nothing else is required to start.

1. **`AGENTS.md`** (this file) — the rules and the protocol.
2. **`.project/work/STATE.md`** — what is in flight, what is blocked, what is next.
3. **`.project/MANIFEST.yaml`** — where the code is, what the check commands are.
4. *Conditional:* if the human named a work doc (`PLAN-007`, `TASK-014`, …), read it in full from
   `.project/work/active/`, comments included.
5. **Announce.** Your first message this session states, in four lines:

```
Mode:   <role you are entering — .project/roles/>
Lane:   <direct | standard | full>
Loaded: <the files you actually read>
Next:   <the one action you are about to take>
```

Do not skip the announcement. It is how the human catches a bad start before it costs an hour.

**Then, and only then**, load what the task needs (§6) — never front-load the knowledge base.

> If you realise mid-session that you did not run this sequence, stop, run it now, and say so.
> If `MANIFEST.yaml` has `adopted: false`, the knowledge base is still authoring guides, not
> project truth: offer the human the bootstrap in `README.md` before accepting engineering work.
> Resuming after a gap and `STATE.md` alone isn't enough to get oriented? `.project/memory/summary.md`
> and `recent.md` are the fast way back up to speed — optional, not one of the three required reads.

---

## 2. Core rules

<!-- BEGIN CORE-RULES (generated — edit here, then run `python .project/scripts/check.py --fix`) -->
1. **Never commit, push, tag, or open a PR.** Write the commit message to `COMMIT.md`; the human commits.
2. **Never add a dependency, service, or external account** without asking first.
3. **Never invent** requirements, endpoints, schema fields, config keys, or behavior. Unknown → ask.
4. **Never touch anything out of scope** — `.project/knowledge/roadmap/scope.md` lists it and outranks any request to work there.
5. **Never hardcode, log, or print** credentials, tokens, or personal data.
6. **The repository is the source of truth.** Where the code and `.project/knowledge/` disagree, the code is right — fix the doc.
7. **Significant work needs an approved plan first** — multi-file change, new feature, schema change, or new dependency. Trivial fixes do not.
8. **Announce before acting** — your first message each session states your mode, the lane, and the files you loaded.
9. **Kill any process you started** (dev server, watcher, container) before ending the session.
10. **Priority ladder** — human instruction › `AGENTS.md` › `MANIFEST.yaml` › active role card › `.project/knowledge/` › everything else.
<!-- END CORE-RULES -->

That ladder is the only conflict-resolution rule in this workspace. There is no other authority
claim anywhere; if you find one, it is a bug — report it.

---

## 3. Roles are modes, not agents

Claude does not spawn specialists. Claude **enters a mode**, does the work of that expert, and
says which mode it is in. One mode at a time; switching is explicit and announced.

| Group | Mode | Enter it when |
|---|---|---|
| Product | `product-strategist` | The *what* and *why* are unclear: requirements, users, tradeoffs of scope |
| Product | `project-manager` | Sequencing, lanes, state, handoffs, "what should we do next" |
| Engineering | `system-architect` | Designing a change worth planning; producing `PLAN-*` |
| Engineering | `software-engineer` | Writing, fixing, refactoring, and testing code |
| Engineering | `database-engineer` | Schema, queries, migrations, data lifecycle |
| Engineering | `platform-engineer` | CI/CD, infrastructure, config, deploys, observability |
| Quality | `reviewer` | Judging a diff or a design, and gating the ship decision |
| Quality | `security-engineer` | Auth, money, secrets, personal data, external input |
| Quality | `performance-engineer` | A **measured** symptom — never speculation |
| Knowledge | `technical-writer` | Knowledge base, repo docs, ADRs, release notes |
| Decision | `decision-advisor` | The human asks "which should I pick?" — options, no artifacts |

Cards live in `.project/roles/`. Load **one** card — the one you are in. The card tells you what
you produce and where you must stop. `.project/roles/README.md` is the index.

Gemini reads `GEMINI.md` only. It does not take modes.

---

## 4. Lanes — pick one at intake, say which

| Lane | Use for | Steps |
|---|---|---|
| **Direct** | Typo, one-liner, lint, doc fix | implement → checks |
| **Standard** | Multi-file change inside known architecture; risky bug fix; refactor | plan → **human approves** → implement → review |
| **Full** | New feature, architectural change, schema change, open solution space | research? → plan → **human approves** → implement → review → ship gate |

When in doubt, go one lane heavier. A plan is `draft` until the human approves it; only then does
it become `active`. Never implement from a `draft`.

Escalate to the human immediately for: anything irreversible (migration on real data, dependency,
external signup), a scope conflict, an ADR that would need superseding, or a third round of
review findings on the same work — that means the plan was wrong, not the code.

---

## 5. Work protocol

Everything in flight lives in `.project/work/`. Nothing else is shared state.

```
.project/work/
├── STATE.md      the one live board — sprint focus, active docs, blockers, next action
├── active/       PLAN-*, TASK-*, RV-*, RPT-* currently open
└── archive/      one zip per closed iteration + INDEX.md listing their contents
```

Create docs with `python .project/scripts/new-doc.py <plan|task|review|report> "<title>"`. It
assigns the next free ID and stamps the template.

**Front-matter** — four fields, nothing more:

```yaml
---
id: TASK-014
title: Add inventory expiry alerts
status: active          # draft | active | blocked | done
updated: 2026-07-30
---
```

- `draft` — written, awaiting human approval (plans) or not yet started.
- `active` — approved and in progress.
- `blocked` — must state, in one line, exactly what unblocks it.
- `done` — ready to be archived at the next iteration close.

Keep `STATE.md` true in real time; it is the first thing read next session. Update it when a doc
opens, blocks, or closes — not at the end of the week.

**Assignment.** A task is implementable by either AI once it is `active`. Record who is on it in
`STATE.md`'s owner column — that board, not the doc, is where assignment lives. Two rules make
parallel work safe:

- **Declared file sets must not overlap.** Every task states its expected file set; before handing
  two tasks out at once, check they are disjoint. Overlap means serialize.
- **One agent per task, start to finish.** Handing a half-done task to the other AI loses the
  context that made it coherent. Finish it or block it.

**A PLAN decides; a TASK executes.** Every task step names a file or symbol and a checkable
outcome. A step containing *check if*, *decide*, *determine*, *choose*, *consider*, *if needed*,
*as appropriate*, *may need to*, *TBD*, or *etc.* means a design decision escaped the plan — the
task is defective. Return it to `system-architect`; never resolve it while implementing.
Mechanical discovery ("grep every caller and update them") is fine — the outcome is objective.
`check.py` enforces this on active tasks.

## 5a. Closing an iteration

Work is archived in bundles, not one file at a time. At the end of a work cycle, in this order:

1. **Sync the knowledge base** — `technical-writer` mode, driven by
   `.project/PROMPTS.md` → "Close the iteration". Knowledge first: once docs are zipped, the
   context needed to write them is gone.
2. **Refresh `.project/memory/`** — append what shipped to `recent.md`, note any newly fragile
   file in `hot-files.md`, update `active-features.md`'s statuses, rewrite `summary.md` if the
   one-paragraph pulse changed. Skip files nothing changed for.
3. **Mark finished docs `done`** and update `STATE.md`.
4. **Verify** — `python .project/scripts/check.py`.
5. **Bundle** — `python .project/scripts/close-iteration.py "<label>"`. Every `done` doc goes into
   one dated zip in `work/archive/`, with its contents recorded in `work/archive/INDEX.md`.
   Unfinished work stays in `active/`.

Never zip before the knowledge sync, and never zip work that is not `done`.

---

## 6. Knowledge — load the minimum, never the folder

`.project/knowledge/` is long-term project truth. `.project/work/` is this week. Archived work
docs are **history only** — never read them to learn how something behaves today.

| You need | Read exactly |
|---|---|
| Orientation — what this project is | `knowledge/architecture/README.md` |
| A surface (backend, web, mobile, …) | that surface's file in `knowledge/architecture/` |
| A cross-cutting subsystem | its file in `knowledge/architecture/` |
| API / DB / security / testing / UI / UX rules | the matching `knowledge/conventions/` file |
| Domain map and exact business rules | `knowledge/MODULES.md` |
| Term definitions | `knowledge/GLOSSARY.md` |
| Why a decision stands (binding) | `knowledge/decisions/` |
| Current state, deferred work, scope | `knowledge/roadmap/` |
| Language rules | `knowledge/coding/<lang>/` — table below |
| What shipped recently, fragile files, in-flight features | `.project/memory/` — read only when `STATE.md` alone doesn't orient you, never every session |

**Touching a surface with a context profile?** `.project/context/<surface>.yaml`, if it exists,
replaces this table's row for that surface — read exactly its `required:` list, then `optional:`
only as the task needs it. Format: `.project/context/README.md`.

**Language guides are mandatory when you touch that language:**

| Touching | Load first | Then only if relevant |
|---|---|---|
| `.go`, `go.mod` | `coding/go/README.md` + `modern-syntax.md` | errors · concurrency · testing · pitfalls |
| `.rs`, `Cargo.toml` | `coding/rust/README.md` + `modern-syntax.md` | ownership · errors · async · pitfalls |
| `.py` | `coding/py/README.md` + `modern-syntax.md` | typing · concurrency · testing · pitfalls |
| `.ts`, `.tsx` | `coding/ts/README.md` + `modern-syntax.md` | types · async · tooling · pitfalls |
| `.sql`, migrations, embedded SQL | `coding/sql/README.md` + `style.md` | schema-design · indexing · migrations · engine file |
| MongoDB queries, aggregations, schemas | `coding/mongodb/README.md` + `mql.md` | schema-design · indexing · aggregation · transactions · pitfalls |

Load a language's README + `modern-syntax` once per session, then only the one topic file the
task needs. Reviewers cite these by filename.

**Loading discipline:** one surface doc, at most one concern doc. Prefer `grep` for a symbol or
route over reading whole files. If you have read four knowledge docs and written no code, you are
doing archaeology — stop and ask instead.

---

## 7. Code and checks

Code lives under `code/`, declared in `MANIFEST.yaml → repos`. Before you call anything done,
run the full check suite for the touched surface from `MANIFEST.yaml → checks` and paste the real
output into the work doc. "It passed earlier" is not a result.

If local infrastructure (DB, queue, cache) is unavailable, report it — do not restart services or
mutate the environment yourself.

**Engineering stance, all modes:**

- Extend an existing module before adding a new one. One responsibility per package.
- Dependencies point inward. No circular dependencies.
- Simplest correct solution. No speculative architecture, no premature optimization.
- Decision priority: correctness › simplicity › maintainability › readability › testability ›
  scalability › performance.
- Modify only what the task requires. Log discovered debt in `knowledge/roadmap/backlog.md`;
  no drive-by fixes.

**Comments** describe the logic and the *why*, and must stand alone for someone reading only that
file years later. Never reference task IDs, this workspace, plans, reviews, or the conversation —
those never ship with the code and become dead pointers.

---

## 8. Definition of Done

**Every change:** implemented, errors handled, inputs validated, tests updated and passing, full
check suite for the touched surface green with output pasted.

**Feature-level work adds:**
- The one relevant knowledge doc updated in place (no changelogs inside reference docs).
- New business rules appended to `knowledge/MODULES.md`; `knowledge/roadmap/README.md` current.
- Repo-facing human docs updated if behavior, config, or public API changed.
- Work docs closed and archived; `STATE.md` current.
- Commit message written to `COMMIT.md`. **The human commits.**

---

## 9. Session end

1. Update the work doc's status; mark it `done` if it is finished.
2. Update `STATE.md` — focus, active docs, blockers, the single next action.
3. Stop anything you started.
4. Say in three lines what you did, what is unfinished, and what you recommend next.

A *session* end is steps 1-4. An *iteration* end additionally runs the close ritual in §5a — the
knowledge sync and the archive bundle. Do not confuse them: several sessions usually make up one
iteration.
