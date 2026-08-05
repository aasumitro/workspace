# Conventions — User Interface (AUTHORING GUIDE)

> **Replace this file** with the component/styling/state rules every frontend change must follow
> — what an engineer builds against and a reviewer cites. Feature detail lives in
> `../architecture/frontend.md`; this doc is the *rules*.

# Conventions — User Interface

> current to {{commit sha / date}}

## Hard rules
*{{one line each: dependency policy · "all backend calls through <wrapper>" · type source of
truth ("no invented DTOs — use <types dir>") · server-state policy (no global store?) ·
generated-code no-touch zones · i18n requirement (which languages, at introduction time) ·
"frontend authz is UI-only".}}*

## Component inventory — reuse before creating
*{{the shared primitives (tables, dialogs, drawers, badges, banners, guards, form sections,
empty/error/loading states) and shared hooks/formatters — name + one-line purpose. Anything not
listed gets duplicated by agents; keep it complete.}}*

## State placement
*{{one line per category: server data → ? · session → ? · URL state → ? · cross-component UI
state → ? · local state → ? · forms → ?}}*

## API access pattern
*{{the wrapper functions and their error/unwrap behavior · sanctioned raw exceptions (SDKs,
streams, downloads) · pagination pattern · validation-error → field mapping.}}*

## Styling
*{{design system / component library + its config (theme, tokens) · dark-mode policy ·
responsive breakpoints and patterns (e.g. table→card at <768px) · icon set · font.}}*

## Routing conventions
*{{file-based vs code-based · what a route file may contain · guard patterns · any generated
route tree + its update procedure/gotcha.}}*

## Verification
*{{the exact commands before declaring done (typecheck/lint/format/build/e2e) — must agree with
`MANIFEST.yaml → checks`; include known cache lies ("re-run tsc with --incremental false after
big refactors").}}*
