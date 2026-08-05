# work/ — everything in flight

Short-term state. Contrast with `../knowledge/`, which is what stays true next month.
Full protocol: `AGENTS.md` §5.

| Path | Holds |
|---|---|
| `STATE.md` | The one live board — focus, active docs, blockers, next action |
| `active/` | Open docs: `PLAN-*`, `TASK-*`, `RV-*`, `RPT-*` |
| `archive/` | One zip per closed iteration, plus `INDEX.md` listing their contents |

Create a doc: `python ../scripts/new-doc.py <plan|task|review|report> "<title>"`.

Statuses: `draft` → `active` → `done`, plus `blocked` (which must name what unblocks it).

## Closing an iteration

Sync the knowledge base **first** (`../PROMPTS.md` → "Close the iteration"), then bundle:

```bash
python ../scripts/close-iteration.py "expiry tracking" --dry-run
python ../scripts/close-iteration.py "expiry tracking"
```

Every `done` doc goes into `archive/<date>-<label>.zip` — one bundle per iteration, so a week's
report, plan, tasks, and review travel together — and `archive/INDEX.md` records what is inside so
you never unzip to find something. Unfinished docs stay in `active/`; an iteration boundary must
not swallow work in progress.

IDs are never reused: `new-doc.py` reads inside the zips when assigning the next one.

Archived docs are **history only**. Never read them to learn how something behaves today; the
knowledge base is authoritative for current behavior.
