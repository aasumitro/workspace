# Conventions — API (AUTHORING GUIDE)

> **Replace this file** with the rules every API change must follow — the conventions extract an
> engineer writes against and a reviewer checks against. Routes live in the surface doc; this
> doc is the *rules*.

# Conventions — API

> current to {{commit sha / date}}

## Hard rules
*{{one line each. Cover: dependency policy · layering (where business logic lives vs handlers) ·
error-handling contract (wrapping, typed errors, who maps to HTTP) · what handlers may/may not
do · how auth context reaches code · documentation requirement per endpoint.}}*

## Response envelope
*{{the exact success/paginated/error/validation-error JSON shapes, as code blocks. Include
pagination style (cursor/offset) and its parameter names.}}*

## Request lifecycle
*{{middleware/guard order and where a new route must hook in; any ordering traps.}}*

## Patterns
*{{table: pattern → convention. Versioning, idempotency, naming (paths, params, error codes),
timeouts/retries for outbound calls, event publishing rules.}}*

## API documentation
*{{tool + regen command + annotation shape + known gotchas; or "none yet — do not invent one
without a plan".}}*

## Gotchas
*{{route-level surprises that bit someone once. Grow this list.}}*
