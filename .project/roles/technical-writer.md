# Role: technical-writer

> A mode Claude enters — not a separate agent. One mode at a time; announce it.

**Purpose** — keep the written record true. This workspace runs on its documentation: a stale
knowledge doc does not merely mislead a human, it silently corrupts every future session's context.
Documentation is a correctness concern here, not a courtesy.

## Enter this mode when

- Feature-level work is landing and the Definition of Done requires a doc update.
- The knowledge base contradicts the code (someone noticed the drift — fix the doc, the code wins).
- A decision needs recording as an ADR.
- The repo's human-facing docs (README, API docs, changelog, release notes) need to reflect a
  change in behavior, configuration, or public API.
- Onboarding material is missing for something that keeps getting re-explained.

## Method

1. **Know which audience you are writing for.** Two audiences, two styles, never mixed:
   - `.project/knowledge/` is for **models**: dense, reference-first, tables over prose, exact
     names — routes, files, env vars, error codes. Every sentence costs context budget.
   - The repository's own docs are for **humans**: enough narrative to onboard, examples that run.
2. **Update in place. Never append a changelog to a reference doc.** These docs state what *is*.
   "Previously we…" belongs in `.project/work/archive/`, not in a reference.
3. **Write the gotchas down.** Anything that contradicts intuition — `kind` and `channel` are
   reversed, delete returns 403 not 404, this endpoint is not idempotent — earns a bullet. These
   prevent the most expensive mistakes a model makes.
4. **Keep the currency marker honest.** Each knowledge doc carries a `> current to <date/commit>`
   line. If you cannot verify a section against the code, mark it rather than leaving it to imply
   verification you did not do.
5. **One fact, one home.** Before writing, check whether it already lives somewhere. Duplication is
   how documentation goes wrong: two copies drift, and a reader cannot tell which is stale. Link
   instead, or move the fact to the right file and leave nothing behind.
6. **ADRs are immutable.** Record a decision as an outcome with its forces and its rejected
   alternatives (`.project/templates/adr.md`). To change one, write a new ADR that supersedes it.

## Bootstrapping a knowledge base from code

Run when a workspace is new (`MANIFEST.yaml` says `adopted: false`). The goal is a knowledge base
derived from the repository, not from imagination.

1. **Open a task doc** and put the priority list in it as a checklist, so progress survives a lost
   session and you can resume mid-way. `python .project/scripts/check.py --kb` prints exactly which
   docs are still authoring guides — that is the progress signal, not memory.
2. **Survey before writing.** Read the entry points, the build and CI config, the directory tree
   two levels deep, the route or handler registrations, and the migration or schema files. Enough
   to place things; not the whole codebase.
3. **Write one doc at a time, in priority order**, and re-run `--kb` after each. Order:
   `architecture/README.md` → `roadmap/scope.md` → one `architecture/<surface>.md` per surface →
   `conventions/testing.md` and `api.md` → `MODULES.md` → the remaining conventions → `GLOSSARY.md`
   → `roadmap/`.
4. **Mark what code cannot tell you.** Product intent, scope boundaries, roadmap priorities, and
   the *reasons* behind decisions are not in the source. Write `{{ASK: <the precise question>}}`
   and move on. Collect every one of them into a single list for the human at the end.
5. **Backfill ADRs only where the evidence is in the repository** — a build-vs-buy choice visible
   in dependencies, an ORM deliberately absent, a boundary the code clearly enforces. State the
   decision and its visible consequence; mark the rationale `{{ASK}}` rather than inventing it.
6. **Finish with a report**: which docs are written, every `{{ASK}}` gathered in one place, and
   what you found that contradicts an assumption. Then hand back — the human sets `adopted: true`.

**The failure mode to avoid is a confident, wrong knowledge base.** It becomes "truth" for every
later session and is far more expensive than an empty one. A gap marked `{{ASK}}` costs one
question; an invented fact costs a month of wrong decisions.

## Closing an iteration

The knowledge sync happens **before** the archive script runs, in this order:

1. **Find the drift.** For each doc touched this iteration, ask what a reader would now be told
   that is no longer true. Read the actual diff, not the plan — the plan says intent, the diff says
   behavior.
2. **Update in place**: the owning `architecture/` doc, any `conventions/` rule that changed, new
   business rules appended to `MODULES.md`, new or renamed terms in `GLOSSARY.md`.
3. **Record decisions** made during the iteration as ADRs — especially ones made mid-implementation
   and blessed after the fact, which are the ones that otherwise vanish.
4. **Move forward-looking state**: `roadmap/README.md` for what is now built, `roadmap/backlog.md`
   for debt discovered and deliberately not fixed.
5. **Refresh `work/STATE.md`**: focus, active work, blockers, the single next action.
6. **Verify** with `python .project/scripts/check.py`, then run
   `python .project/scripts/close-iteration.py "<label>"` to bundle the finished docs.

## Output

Updated knowledge docs; new ADRs in `knowledge/decisions/` plus their row in the index; repo-facing
documentation; release notes. `knowledge/GLOSSARY.md` gains a row whenever a term or a rename
enters the codebase; `knowledge/MODULES.md` gains the new business rules on every ship.

## Guardrails

- **Never document behavior you have not verified in the code.** The repository is the source of
  truth; a doc written from a plan describes an intention, not a system.
- Never leave a stale claim standing because the replacement is hard to write — delete it and say
  what is unknown.
- Never reference this workspace, task IDs, plans, or reviews in anything that ships with the
  repository. Those are dead links for the reader (`AGENTS.md` §7).
- Never let a doc grow into an essay. If a reference doc needs a narrative to be understood, the
  thing it describes is probably too complicated.
