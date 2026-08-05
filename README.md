# Workspace — an AI-assisted workspace

A reusable, project-agnostic workspace for building software with **Claude as the primary AI** and
**Gemini (Antigravity) as support**. Clone it once per project, drop the codebase into `code/`,
describe the project in `.project/knowledge/`, and work.

> **What this is — and isn't.** This is a **single-orchestrator, human-in-the-loop** workspace, not
> a multi-agent swarm. One primary AI (Claude) enters expert *modes* and does the work; one support
> AI (Gemini) researches and implements assigned tasks; a human approves every plan and makes every
> commit. There is no fleet of autonomous agents negotiating with each other, and nothing lands
> without a human gate. If a swarm-style topology is what you're after, this isn't it — and doesn't
> try to be.

> **This file is for humans.** Agents read `AGENTS.md` — that is the authoritative manual, and it
> is the only file that carries rules.

> **Is this too much for your project?** Workspace is built for something you and an AI will keep
> coming back to over weeks or months — a real codebase with more than one person's worth of
> context to track. For a single throwaway script, a weekend prototype, or a one-off fix, the
> lanes system already has an escape hatch (**direct** lane, no plan, no review) — but if most of
> your work would live in that lane forever, you probably don't need the workspace at all: just
> talk to Claude in the repo directly. Adopt Workspace when the *standard* and *full* lanes are where
> real work lives, not the exception.

```
              ┌──────────────────────────┐
              │          HUMAN           │   approves plans · commits · decides
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │         CLAUDE           │   CLAUDE.md
              │       primary AI         │   product · planning · architecture ·
              │   enters expert modes    │   implementation · review · docs
              └──────┬────────────┬──────┘
                     │            │  research · alternatives · validation ·
                     │            │  second opinions · implements tasks
                     │     ┌──────▼──────────────────┐
                     │     │        GEMINI           │   GEMINI.md
                     │     │     supporting AI       │   never decides
                     │     └─────────────────────────┘
                     │            │
                     │            └──► code ──► Claude reviews it
                     │                          (a real gate, not a self-check)
                     ▼
              .project/work/     plans · tasks · reviews · reports · state
```

## The shape of it

**One primary AI, many modes.** Claude does not hand work to a fleet of specialist agents; it
*enters a mode* — system architect, software engineer, reviewer, security engineer — announces
which one, and works under that mode's constraints. Eleven modes cover product discovery through
production operations. They live in `.project/roles/`.

**Gemini supports.** It researches, explores alternatives, validates claims, gives independent
second opinions, and **implements tasks**. What it never does is decide — architecture, the chosen
option, the review verdict, and scope stay with Claude and you.

That split is about authority, not capability. Once you approve a plan, its tasks contain no
decisions left to make (`check.py` enforces that), so either AI can execute one. The pairing worth
defaulting to is **Gemini implements, Claude reviews** — a reviewer who did not write the code is a
real gate, where Claude reviewing itself is a self-check.

**You approve and commit.** Agents never commit, never push, never open pull requests. A plan stays
`draft` until you approve it. Commit messages are written to `COMMIT.md` for you to use.

## Layout

```
workspace/
├── AGENTS.md          THE manual — authoritative for every agent
├── CLAUDE.md          Claude's entry file: startup, core rules, modes
├── GEMINI.md          Gemini's entry file: startup, core rules, its brief
├── COMMIT.md          agent-written commit messages; the human commits
├── code/              ← clone the actual codebase(s) here
└── .project/
    ├── MANIFEST.yaml  machine facts: paths, surfaces, check commands
    ├── PROMPTS.md     copy-paste kickoffs for every workflow
    ├── roles/         the 11 modes Claude enters
    ├── knowledge/     long-term project truth (you fill this in)
    │   ├── architecture/   overview + one doc per surface/subsystem
    │   ├── conventions/    api · database · security · testing · ui · ux
    │   ├── coding/         language guides — go · py · rust · sql · ts · mongodb
    │   ├── decisions/      ADR log
    │   ├── roadmap/        state · backlog · scope
    │   ├── MODULES.md      domain map + exact business rules
    │   └── GLOSSARY.md     terms
    ├── context/       optional: per-surface "read exactly this" profiles, refining §6
    ├── memory/        optional: cross-session notes — recent · hot files · active features · summary
    ├── templates/     plan · task · review · report · adr · issue · pr
    ├── work/          STATE.md + active/ + archive/ — everything in flight
    └── scripts/       new-doc.py · check.py · close-iteration.py · install-hooks.py · tests/
```

**`knowledge/` versus `work/`** — `knowledge/` is what stays true next month: architecture,
conventions, decisions. `work/` is what is true this week: the plan in flight, the task being
executed. Work docs get archived; knowledge docs are updated in place and never expire.

**`context/` and `memory/` are optional and neither is a mandatory read.** `context/` holds
per-surface YAML profiles — this project's own, more precise version of `AGENTS.md` §6's generic
loading table. `memory/` holds what `STATE.md` no longer says once it's been reset for a new
iteration: what shipped recently, which files are fragile, what's in progress across more than one
iteration. Both are refreshed at iteration close, not mid-session — see `.project/context/README.md`
and `.project/memory/README.md`.

**The machinery is ready to use.** Entry files, modes, templates, prompts, scripts, and the
language guides in `coding/` work as-is. Everything else under `knowledge/` is per-project and
ships as an authoring guide that tells you what to write there.

## Setup — about 30 minutes

**1. Clone and add the code**

```bash
git clone <this-template> my-workspace && cd my-workspace
cd code && git clone <your-repo> <name>
```

Optionally, once `code/<name>` is a real repo you commit from, install the pre-commit hook that
runs `check.py` before every commit there — the one technical backstop behind "agents never
commit, humans do and check first":

```bash
python .project/scripts/install-hooks.py --target-repo code/<name>
```

**2. Fill `.project/MANIFEST.yaml`**

Replace every `{{placeholder}}`: workspace name, repo path and remote, the **surfaces** (backend,
web, …) with their paths, and the **checks** — the exact commands CI runs per surface. The checks
matter most: agents run them before calling anything done.

**3. Write the knowledge base**

Every doc under `knowledge/` ships as an authoring guide. Open it, follow its instructions, replace
it. Priority order — the first three unlock real work:

| # | Doc | Unlocks |
|---|---|---|
| 1 | `knowledge/architecture/README.md` | Orientation — the first doc every agent reads |
| 2 | `knowledge/roadmap/scope.md` | Agents knowing what *not* to touch |
| 3 | one `knowledge/architecture/<surface>.md` per surface | Surface work |
| 4 | `knowledge/conventions/testing.md` + `api.md` | Quality gates |
| 5 | `knowledge/MODULES.md` | Business-rule correctness in reviews |
| 6 | the rest of `conventions/` · `GLOSSARY.md` · `decisions/` | Depth |
| 7 | `knowledge/roadmap/README.md` + `backlog.md` | Planning quality |

`knowledge/coding/` ships with Go, Python, Rust, SQL, TypeScript, and MongoDB guides — keep what
matches your stack, delete the rest.

Or hand the whole thing to Claude and come back to review — the full prompt is in
`.project/PROMPTS.md` under **"Bootstrap the knowledge base"**. It works through the priority
order autonomously, deriving everything from the actual code, and writes `{{ASK: …}}` wherever the
code cannot answer (product intent, scope, the *why* behind a decision) instead of inventing an
answer. It comes back with the written docs and one list of questions.

Track progress at any time:

```bash
python .project/scripts/check.py --kb
```

**4. Flip the switch and verify**

Review what it wrote, answer the `{{ASK}}` list, then set `adopted: true` in `MANIFEST.yaml`, fill
`.project/work/STATE.md`, and run:

```bash
python .project/scripts/check.py
```

It verifies the rule blocks are in sync, required files exist, references resolve, active tasks
contain no unresolved design decisions, and — once `adopted: true` — that no knowledge doc is
still a placeholder. Run it after any restructuring.

**5. First session**

```bash
claude          # auto-reads CLAUDE.md
gemini          # auto-reads GEMINI.md
```

Claude's first message should be a four-line header: mode, lane, files loaded, next action. If it
is not, the startup sequence was skipped — say "run the startup sequence" and it will recover.

Give it something small first — a bugfix through the standard lane — and let the Definition of Done
start keeping the knowledge base current from day one.

## Daily use

| You want | Say |
|---|---|
| A design | *"Enter system-architect mode and plan X"* → a `PLAN` in `draft` |
| It built | *(to either AI)* *"Implement TASK-004"* → code + `COMMIT.md` |
| It checked | *(to Claude)* *"Review TASK-004 against PLAN-003"* → an `RV` doc with a verdict |
| Options | *(to Gemini)* *"Compare X and Y for this use case"* → an `RPT` report |
| A second opinion | *(to Gemini)* *"Review this plan independently and disagree where you do"* |
| A decision | *"Enter decision-advisor mode: should we X or Y?"* → a brief, no artifacts |

Running both at once is safe as long as each task's declared file set is disjoint — check before
handing out two, and record who owns what in `.project/work/STATE.md`.

Filled-in versions of all of these: `.project/PROMPTS.md`.

Lanes keep ceremony proportional: **direct** for a typo, **standard** (plan → approve → implement →
review) for real changes, **full** (adds research and a ship gate) for features and schema changes.

**Plans decide; tasks execute.** Once you approve a plan, every architectural and behavioral
decision is settled — tasks only translate it into steps that name a file and a checkable outcome.
A task step saying *"check if…"* or *"choose…"* means a decision leaked out of the plan, and
`check.py` fails on it. Claude is instructed to hand such a task back rather than improvise.

## Closing an iteration

At the end of a work cycle, one prompt and one command:

```
"Close the iteration"          →  Claude syncs knowledge/, ADRs, roadmap, and STATE.md
                                  against what actually shipped (.project/PROMPTS.md)

python .project/scripts/close-iteration.py "expiry tracking"
```

The script folds every `done` doc — the week's report, plan, tasks, and review — into one
`work/archive/<date>-<label>.zip`, and records the contents in `work/archive/INDEX.md` so you can
find a doc without unzipping. Unfinished work stays in `active/`. Knowledge sync runs first: once
the docs are zipped, the context needed to write them is gone.

## Maintaining the template

Improvements to the *machinery* — modes, prompts, templates, scripts, `AGENTS.md`, entry files —
belong back in the template so future clones benefit. Everything under `knowledge/`, `work/`,
`MANIFEST.yaml`, and `COMMIT.md` is per-project and never flows back. See `CONTRIBUTING.md` for the
process, and run `python -m unittest discover -s .project/scripts/tests` before sending a script
change back — it covers `check.py`, `new-doc.py`, `close-iteration.py`, and `install-hooks.py`.

One workspace per product. Runtime IDs, state, and knowledge are all per-product; sharing them
across two products poisons both.
