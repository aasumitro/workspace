---
id: PLAN-000
title: {{title}}
status: draft            # draft until the HUMAN approves; then active
updated: {{YYYY-MM-DD}}
links: []                # e.g. [RPT-003]
---

# PLAN-000 — {{title}}

## Problem
{{what needs to exist/change, for whom, and why now}}

## Constraints
{{ADRs and invariants that bound this design (cite by number); scope limits; compatibility}}

## Chosen architecture
{{the design: module placement, contracts/events added or changed, schema impact, data flow.
Name real files and seams — implementation must not have to re-derive this.}}

## Alternatives considered
| Option | Why rejected |
|---|---|
| {{option}} | {{reason}} |

## Risks
{{what could go wrong at runtime or during rollout, and the mitigation}}

## Tradeoffs
{{what this design deliberately gives up}}

## Edge cases
{{enumerated, business-rule style — these get appended to knowledge/MODULES.md on ship}}

## Migration / rollout impact
{{schema migrations (up AND down), data backfill, ordering, feature exposure; "none"}}

## Task breakdown (implementation order: domain → logic → API → UI → tests → docs)

<!--
This section is the contract with implementation. Every decision must already be made
here — a task that has to choose something means this plan is unfinished.

Each row must survive the test: could someone implement it without asking you a
question? If not, decide the open part above and rewrite the row.
-->

| # | Task | Files it touches | Done when | Depends on |
|---|---|---|---|---|
| 1 | {{imperative, one deliverable}} | {{exact paths}} | {{objectively checkable outcome}} | — |
| 2 | {{…}} | {{…}} | {{…}} | 1 |

## Decisions this plan settles
{{The list an implementer must never re-open: naming, shapes, error codes, limits,
which existing helper to extend, what happens on each edge case. If it is not decided
here, it will be improvised at 2am — decide it now or state explicitly that the human
must.}}

## Verification strategy
{{which test layers prove which tasks; what the ship check should re-run}}

---
## Comments
{{> [YYYY-MM-DD] …}}
