---
id: TASK-000
title: {{imperative title}}
status: draft            # draft | active | blocked | done
updated: {{YYYY-MM-DD}}
links: []                # the PLAN this implements, e.g. [PLAN-007]
---

# TASK-000 — {{title}}

<!--
A TASK is prescriptive, never exploratory. The PLAN already decided the architecture
and the behavior; this doc only translates settled decisions into verifiable steps.

Every step: an imperative verb · a named file or symbol · an outcome you can check.
Banned in Steps — each one means a decision leaked out of the plan:
  "check if" · "see if" · "decide" · "determine" · "choose" · "consider" ·
  "investigate" · "explore" · "figure out" · "if needed" · "as appropriate" ·
  "handle appropriately" · "may need to" · "TBD" · "etc."
`check.py` fails the workspace if one appears. If you cannot write a step without
one, the plan is unfinished: set status: blocked and hand it back to the architect.

Mechanical discovery is fine — "grep every caller of X and update them" is a step,
because the outcome is objective. Deciding is not.
-->

## Goal
{{one paragraph: what exists and is true when this is done}}

## Source
{{PLAN-XXX step N | direct-lane fix — state why no plan was needed}}

## Definition of ready — all true before status becomes `active`
- [ ] The plan this comes from is `status: active` (human-approved)
- [ ] Every step below names a file or symbol and a checkable outcome
- [ ] No step contains a decision — nothing left to choose at implementation time
- [ ] The expected file set is written down and the task fits inside it
- [ ] Dependencies on other tasks are declared below

## Surface & scope
- Surface: {{backend | web | …}}
- Expected file set: {{paths — going beyond this is a deviation, record it}}
- Depends on: {{TASK-XXX must land first | nothing}}

## Steps
<!-- Shape: - [ ] <verb> <file/symbol> — <verifiable outcome> -->
- [ ] {{Add `Field` to `path/to/file` — <what is true afterwards>}}
- [ ] {{Update every caller of `Symbol` (grep `path/`) — all compile against the new signature}}
- [ ] Add {{regression | unit | integration}} test in `{{path}}` — fails without the change
- [ ] Run the full check suite for this surface — output pasted below, clean

## Deviations from the plan
{{none | what changed and WHY — a deviation without a reason is a protocol violation.
If the deviation is a design decision, stop: set status: blocked and return to the architect.}}

## Verification
```
{{commands run + trimmed real output — not "tests pass"}}
```

## Handoff notes for the reviewer
{{what deserves attention; known-ugly spots; what you would challenge}}

---
## Comments
{{append here: > [YYYY-MM-DD] …}}
