# Backlog (AUTHORING GUIDE)

> **Replace the placeholder rows.** This is the record of *deliberately deferred or declined*
> work — it prevents agents from re-proposing (or accidentally building) what you already
> decided against. Nothing here is required to ship. The most useful pattern: deferred items get
> a **trigger** ("build when X happens"), not a date. Landmark decisions behind declines live in
> `../decisions/`.

# Backlog

> updated {{date}}

## Declined (will not build)
| Item | Reason |
|---|---|
| {{item}} | {{why — cite the ADR if one exists}} |

## Deferred — add when triggered
| Item | Trigger |
|---|---|
| {{item}} | {{the concrete event that makes it worth building}} |

## Decisions already made (do not revisit without strong reason)
*{{one-line list of the standing "no X" decisions, each with its ADR reference.}}*

## Discovered debt
*{{agents append here when scope discipline forbids a drive-by fix: file/area · what's wrong ·
suggested fix · found during TASK-XXX.}}*
