# PROMPTS.md — copy-paste kickoffs

Fill the `{{blanks}}`, paste, go. These start a workflow; they never restate rules — the rules are
in `AGENTS.md` and the role card, and those win if a prompt ever disagrees.

---

## Bootstrap the knowledge base → Claude, `technical-writer`

Run once, after cloning the code into `code/` and filling `MANIFEST.yaml`. Expect it to take a
while and to come back with questions — leave it running and review at the end.

```
Enter technical-writer mode and bootstrap the knowledge base from the code
in code/{{repo}}.

Work autonomously through the priority order in your role card, one doc at a
time. Open a TASK doc first with the full checklist so progress survives a
lost session, and run `python .project/scripts/check.py --kb` after each doc
to confirm what is left.

The repository is the source of truth: derive everything from the actual code —
entry points, routes, migrations, build config, tests. Where the code cannot
tell you (product intent, scope, roadmap, WHY a decision was made), write
{{ASK: <precise question>}} and keep going. Do not invent, do not infer intent
from naming, and do not fill a section to make it look complete.

When done, report: which docs are written, every {{ASK}} collected in one list,
and anything you found that contradicts what I told you. Do not set
adopted: true — I will, after reviewing.
```

---

## Close the iteration → Claude, `technical-writer`

Run at the end of a work cycle, before archiving. This is what keeps the knowledge base in sync
with what actually shipped.

```
Enter technical-writer mode and close this iteration.

1. Read the diff of what actually landed — not the plan, the diff.
2. Update every knowledge doc the change made stale, in place: the owning
   architecture doc, any conventions rule that changed, new business rules
   appended to MODULES.md, new or renamed terms in GLOSSARY.md.
3. Record any decision made during this iteration as an ADR — including ones
   made mid-implementation and blessed afterwards.
4. Update roadmap/README.md (what is now built) and roadmap/backlog.md
   (debt found and deliberately not fixed).
5. Refresh .project/memory/: append what shipped to recent.md, note any newly
   fragile file in hot-files.md, update active-features.md's statuses, rewrite
   summary.md if the one-paragraph pulse changed. Skip files nothing changed for.
6. Refresh work/STATE.md: focus, active work, blockers, next action.
7. Mark finished work docs status: done.
8. Run `python .project/scripts/check.py` and fix what it reports.

Then tell me the label to archive under, and show me a one-paragraph summary
of what changed in the knowledge base. Do not run close-iteration.py until I
confirm the label.
```

Then bundle the finished docs:

```bash
python .project/scripts/close-iteration.py "expiry tracking" --dry-run   # preview
python .project/scripts/close-iteration.py "expiry tracking"             # do it
```

---

## Plan → Claude, `system-architect`

```
Enter system-architect mode.

Problem: {{one paragraph — what needs to change, for whom, and why now}}
Constraints beyond the standard ones: {{deadlines, compatibility, "must not touch X" | none}}
Prior material: {{RPT-XXX, earlier plans | none}}

Produce a PLAN per .project/templates/plan.md. Check it against the ADRs and the
invariants, and call out anything that would supersede one. Do not implement.
Leave it in status: draft and tell me what you most want challenged.
```

---

## Implement → Claude, `software-engineer`

```
Enter software-engineer mode.

Implement {{PLAN-XXX (must be status: active) | this direct-lane fix: <describe>}}.
Start at {{step N | the first unfinished step}}.

Track it in a TASK doc: tick steps as they land, record every deviation with its reason,
and set status: blocked instead of improvising if the plan turns out wrong.
Run the full check suite for the touched surface and paste the real output.
Write the commit message to COMMIT.md. Do not commit.
```

---

## Implement → Gemini

The default when both AIs are available: Gemini writes it, Claude reviews it. The review is a real
gate that way, not a self-check.

```
You are the supporting AI. Read AGENTS.md, GEMINI.md, and
.project/roles/software-engineer.md first — that card binds you exactly as it
binds Claude.

Implement TASK-{{XXX}} (status must be active — stop and say so if it is not).
Stay inside its declared file set.

Every step in that task is already decided. If any step asks you to check if,
choose, determine, or decide something, the task is defective: set
status: blocked, name the undecided question in one line, and hand it back.
Do not resolve it yourself — you have no design authority here.

Tick steps as they land, record deviations with reasons, run the full check
suite for the surface and paste the real output. Write the commit message to
COMMIT.md. Do not commit. Claude reviews this when you are done.
```

---

## Bugfix → Claude, `software-engineer`

```
Enter software-engineer mode on a bugfix.

Bug: {{what happens}}
Expected: {{what should happen}}
Repro / evidence: {{steps, request, logs — whatever exists}}
Surface: {{backend | web | unknown}}

In order: reproduce it (a failing test is the best repro) → check knowledge/MODULES.md
in case this is documented intended behavior → state the root cause in one sentence →
fix minimally, no drive-by refactors → add the regression test that fails without the fix →
run the check suite. If the root cause is architectural, stop and hand it back for planning.
```

---

## Review → Claude, `reviewer`

```
Enter reviewer mode. You are not the author of what you are reviewing — if you wrote it,
say so and review it as an adversary.

Target: {{PLAN-XXX (design review) | TASK-XXX + the working diff (code review) | path}}
Special attention: {{what the author flagged | none}}

Work the checklist in order and deliver an RV doc with a verdict —
approve / approve-with-nits / request-changes — every finding as
severity + file:line + what is wrong + why (cite the rule you are enforcing).
Suggest fixes; do not apply them.
```

---

## Research → Gemini

```
You are the supporting AI. Read AGENTS.md and GEMINI.md first.

Question: {{"Compare X vs Y for <use case>" | "What are our options for Z?"}}
This feeds: {{the decision or plan it will inform}}
Bounding constraints: {{invariants and ADRs that apply, scale, budget, team familiarity | none}}
Depth: {{quick survey — top 3-4, one screen each | deep comparison — the 2-3 serious candidates}}

Deliver an RPT doc in the standard shape. Mark every external claim [verified] or [recalled].
Flag anything that would require superseding an ADR. Ranked recommendation welcome —
no decision.
```

---

## Second opinion → Gemini

```
You are the supporting AI. Read AGENTS.md and GEMINI.md first.

Review this independently and disagree where you actually disagree:
{{PLAN-XXX | the diff | the claim}}

Tell me: what would fail in production, what alternative was not considered,
and what in it you cannot verify. Findings as severity + file:line + why.
Your verdict is input to Claude's decision, not the decision.
```

---

## Decide → Claude, `decision-advisor`

```
Enter decision-advisor mode.

Decision: {{what I am choosing between}}
What I care about: {{cost, speed, maintenance, reversibility, team skills…}}

Give me the real options (including doing nothing), what each commits us to, how each
fails, which are reversible, and your recommendation with the reason it wins.
No code, no plan, no artifacts — just the brief. I decide.
```
