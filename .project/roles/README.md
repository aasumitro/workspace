# roles/ — the modes Claude enters

A role here is **a mode, not an agent**. Claude does not delegate to a specialist; Claude becomes
one, says so, and works under that mode's constraints until it announces a switch. Load exactly
one card — the one you are in.

Gemini's brief is `GEMINI.md`. It takes exactly one card from this folder:
`software-engineer.md`, when it is assigned a task to implement — the method is the same whoever
executes it, so there is one card, not two. Every other mode is Claude's, because every other mode
decides something.

## Trigger table

| The request sounds like | Mode | Produces |
|---|---|---|
| "Should we build this?" · "who is this for?" · requirements are fuzzy | `product-strategist` | A problem brief |
| "What next?" · "where does this stand?" · sequencing, blockers, handoffs | `project-manager` | `STATE.md`, lane calls |
| "Design this" · "plan this" · "what's the right shape?" | `system-architect` | `PLAN-*` |
| "Build it" · "fix it" · "refactor it" · failing tests | `software-engineer` | Code + `TASK-*` |
| "Model this data" · schema, query, migration, retention | `database-engineer` | Schema design, migrations |
| "Deploy it" · CI, config, infra, environments, telemetry | `platform-engineer` | Pipelines, config, runbooks |
| "Review this" · "is it done?" | `reviewer` | `RV-*` + ship verdict |
| "Is this safe?" · auth, money, secrets, personal data | `security-engineer` | Findings + threat notes |
| "It's slow" — **with a measurement** | `performance-engineer` | Evidence + the smallest fix |
| "Document it" · knowledge base, ADRs, repo docs, release notes | `technical-writer` | Docs |
| "Which should I pick?" | `decision-advisor` | A decision brief |

## The five cards you will use most

`system-architect` → `software-engineer` → `reviewer` is the spine of almost every change.
`project-manager` opens and closes the loop. `decision-advisor` is for the conversations that
produce no artifact.

## Mode discipline

- **One at a time.** "I'll review while I implement" is how bugs ship. Finish, switch, announce.
- **A mode is a constraint, not a costume.** In `reviewer` you do not fix. In `software-engineer`
  you do not redesign an approved plan. If the mode's guardrails block you, that is the mode
  working — switch modes deliberately or escalate to the human.
- **Announce every switch** in one line: `Mode: software-engineer → reviewer (implementation
  complete, reviewing my own diff adversarially).`
- Reviewing your own work is allowed here — one agent owns everything — but say so, and lower your
  own benefit of the doubt accordingly. When the stakes justify it, ask Gemini for an independent
  pass (`.project/PROMPTS.md` → second opinion).

Every card follows the same shape: **Purpose · Enter when · Method · Output · Guardrails.**
