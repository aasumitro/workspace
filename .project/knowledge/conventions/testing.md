# Conventions — Testing (AUTHORING GUIDE)

> **Replace this file** with the project's concrete test architecture. The TESTER role card
> carries the principles; this doc carries YOUR layers, helpers, and commands.

# Conventions — Testing

> current to {{commit sha / date}}

## Layers
*{{table: layer → file/dir convention → infra needed → what it covers. E.g. pure/unit vs
handler/component vs integration vs e2e. State which layer is the default home for business
logic tests.}}*

## Commands
*{{exact commands per suite (unit, integration incl. required env vars like TEST_DATABASE_URL,
e2e incl. prerequisites) — must agree with `MANIFEST.yaml → checks`.}}*

## Helpers & fixtures
*{{the standard test helpers (request builders, fake publishers, module constructors, login
helpers), where they live, and the rule to use them instead of hand-rolling. Test-data
conventions: ID ranges/prefixes claimed per suite, isolation + cleanup pattern.}}*

## Coverage
*{{current rough numbers per area if tracked · what's intentionally untested (entrypoints,
wiring, live-infra adapters) so agents don't "fix" it.}}*

## Rules
- Every bug fix gets a regression test that fails without the fix.
- New business logic gets unit tests; system boundaries get integration tests; run the
  integration suite before feature work is done.
- Prefer pure functions for unit-testable logic (pricing, validation, state transitions).
- Avoid brittle tests: assert behavior, not structure; no sleeps for async.
*(keep these; add project-specific ones — e.g. e2e must never mutate shared accounts' real
state, use route interception for deterministic steps)*
