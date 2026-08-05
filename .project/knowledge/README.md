# Knowledge Base — map and authoring guide

Long-term project truth, written for models: dense, reference-first, kept current to the
repository. Human onboarding docs live in the repo itself.

> **Template state:** while `MANIFEST.yaml` says `adopted: false`, most docs here are *authoring
> guides* — open one, follow its instructions, replace it with real content. `coding/` is ready to
> use as-is. Setup order: `README.md` at the workspace root.

## Map — "I need X, read Y"

| Need | Read |
|---|---|
| Orientation: what this project is, its surfaces, what is built | `architecture/README.md` |
| Work on a surface | `architecture/<surface>.md` |
| A cross-cutting subsystem (billing, events, storage, …) | its own `architecture/<subsystem>.md` |
| API conventions | `conventions/api.md` |
| Schemas and migrations | `conventions/database.md` |
| Auth, authorization, secrets, hardening | `conventions/security.md` |
| Test layers, helpers, commands | `conventions/testing.md` |
| UI component and styling rules | `conventions/user-interface.md` |
| UX rules (states, i18n, destructive flows) | `conventions/user-experience.md` |
| Language rules | `coding/<lang>/` |
| Domain map and exact business rules | `MODULES.md` |
| Term definitions | `GLOSSARY.md` |
| Why a decision stands (binding) | `decisions/README.md` |
| Current state and forward priorities | `roadmap/README.md` |
| Deferred or declined work | `roadmap/backlog.md` |
| What is in and out of scope | `roadmap/scope.md` |
| Dated history ("when did X change") | `../work/archive/` — **history only, never current behavior** |

Loading discipline — how much of this to read for a given task — is in `AGENTS.md` §6. The short
version: one surface doc, at most one concern doc, plus the language guide. Never the folder.

## Invariants — the load-bearing rules

> **Fill this in.** The five to ten rules that must survive every change: architecture boundaries,
> "no X" decisions, data-integrity rules, state-machine constraints. These bind as hard as the
> ADRs. One line each. If someone could waste an hour by not knowing it, it belongs here.
>
> Examples of the *kind* of rule that belongs here:
> - "No cross-module imports — modules communicate only through <seam>."
> - "All database access goes through <layer>." / "No ORM — raw queries only."
> - "Payment state moves only from a verified gateway webhook, never a client call."
> - "The mobile app is out of scope — never start work there."

- The repository is the source of truth — where this knowledge base and the code disagree, the code
  is right and this doc gets fixed. *(keep this one)*
- {{invariant}}
- {{invariant}}

## Writing style for every doc here

- **Dense and reference-first.** Tables over prose; exact names — routes, files, env vars, error
  codes — over descriptions. These load into model context; every sentence costs budget.
- **Current behavior only.** No changelogs, no "recently we…", no dated entries. State what *is*;
  history belongs in `../work/archive/`.
- **Gotchas are the highest-value content.** Anything counterintuitive — "`kind` and `channel` are
  reversed", "delete returns 403, not 404" — earns a bullet. These prevent the most expensive
  mistakes.
- Every doc carries a `> current to <date or commit>` line near the top. Whoever lands
  feature-level work updates the one relevant doc **in place** (`AGENTS.md` §8).
- After restructuring anything, run `python .project/scripts/check.py`.
