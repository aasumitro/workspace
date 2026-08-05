# Frontend Surface (AUTHORING GUIDE)

> **Replace this file** with your frontend reference — the doc an agent loads before touching UI
> code. Delete sections that don't apply; duplicate per additional client (mobile.md, admin.md…).

# {{Web}} — {{framework}} (`{{path}}`)

*Reference: structure, routing, state, conventions. Current behavior only. The backend is the
source of truth — never invent endpoints or DTOs.*

> current to {{commit sha / date}}

## Stack
*{{framework, language, build tool, router, data-fetching, forms, styling, component library,
auth SDK, i18n — with versions where they matter.}}*

## Hard rules
*{{one line each — the "all API calls through the wrapper / no global store for server data /
never edit generated components / all text through i18n" class. These are what reviews cite.}}*

## Key files
*{{the load-bearing files an agent must know exist: API client wrapper, route tree, auth
provider, shared hooks/utilities — path + one-line purpose each.}}*

## Folder structure
*{{annotated tree of the src/ layout: where components, features/pages, hooks, lib, routes,
types live — and the rule for what goes where.}}*

## Shared primitives — reuse before creating
*{{the component/hook inventory: tables, dialogs, empty/error/loading states, guards,
formatters. Agents hand-roll duplicates of anything not listed here — keep it complete.}}*

## State management
*{{what goes where: server data → ?, auth/session → ?, URL state → ?, local UI state → ?,
forms → ?. One line per category.}}*

## API integration
*{{response envelope shape, error handling flow (incl. validation-error → field mapping),
pagination pattern, auth token flow.}}*

## Routing & guards
*{{how routes are declared, the guard/redirect chains (public/authed/onboarding/…), and any
route-tree regeneration step with its gotcha.}}*

## Gotchas
*{{backend-vs-intuition discrepancies (verbs, status codes, naming), generated-file traps,
build-cache lies. Grow on every surprise.}}*
