# Backend Surface (AUTHORING GUIDE)

> **Replace this file** with your backend reference — the doc an agent loads before touching
> backend code. Optimize for "find the right pattern/route/file fast". Delete sections that
> don't apply; rename the file if your surface isn't called "backend".

# {{Backend}} — {{lang/framework}}

*Reference: routes, patterns, key packages. Current behavior only.*

> current to {{commit sha / date}}

## Stack & entrypoints
*{{versions of lang/framework/DB/queue/cache; each binary/service entrypoint and what wires it
(the composition root file agents should read to understand construction order).}}*

## Hard rules
*{{the non-negotiables for this surface, one line each — the "no ORM / no init() wiring /
handlers thin / never panic" class of rule. Duplicate the truly load-bearing ones into
`../README.md` §Invariants.}}*

## Key dependencies
*{{the deps that matter, with pinned-version gotchas if any. State the rule: no new deps without
asking.}}*

## Architecture patterns
*{{table: pattern → convention. Cover at least: error handling/wrapping · response envelope ·
how cross-module/service calls work · events/queues · dependency wiring · where shared
infrastructure lives. Exact helper names.}}*

## Middleware / request path
*{{the actual execution order of middleware/guards, engine-level and per-group, with any
ordering traps ("rate-limit must come after auth or it keys by IP").}}*

## Routes / endpoints
*{{per module: a table of route → auth/role → one-line behavior. This is the doc agents check
instead of inventing endpoints — completeness matters more than prose.}}*

## API documentation convention
*{{how endpoints are documented (OpenAPI/swag/comments), the regen command, and annotation
gotchas. If none exists yet: say so explicitly so agents don't invent one.}}*

## Gotchas (load-bearing, counterintuitive)
*{{the list that saves agents hours: naming reversals, soft-delete status codes, fire-and-forget
writes, fail-open vs fail-closed dependencies… Grow it every time an agent gets surprised.}}*
