# Patterns Reference

## Naming Conventions

- `camelCase` variables/functions; `PascalCase` types/interfaces/classes/enums-if-you-must and
  React components; `SCREAMING_SNAKE_CASE` only for true constants of primitive value.
- No Hungarian: not `IUser`, not `TResponse`, not `userObj`. A type and a value may share a
  name (`const User`, `type User`) when they're the same concept.
- Files: one convention per repo — `kebab-case.ts` is the safe default (case-sensitivity across
  OSes); test files `*.test.ts` colocated or mirrored, per repo convention.
- Booleans read as predicates (`isLoading`, `hasAccess`, `canRetry`); handlers as `onX`
  (props) / `handleX` (implementations).

## Module layout

- ES modules everywhere; `import type` for types; no `namespace`, no side-effectful modules
  (importing must not *do* anything).
- Barrel files (`index.ts`) only at real public boundaries (a package, a feature's public
  surface) — deep barrels create import cycles and kill tree-shaking/build parallelism.
- Feature-first folders over layer-first: `features/billing/{components,hooks,api}` beats
  top-level `components/` graveyards. Shared code earns its move to `shared/`/`lib/` by second
  use, not by speculation.
- Path aliases (`@/lib/...`) configured once in tsconfig; no `../../..` ladders.

## API design

- Options object once past 2 parameters; required first args positional:

```ts
function createInvoice(orgId: OrgId, opts: { currency?: Currency; dryRun?: boolean } = {}) {}
```

- Accept wide, return narrow: parameters as `readonly T[]`/interfaces; returns as concrete
  types. Mark inputs `readonly` (`readonly string[]`, `Readonly<Config>`) — mutation is opt-in.
- Discriminated unions are the modeling workhorse — make invalid states unrepresentable:

```ts
type Payment =
  | { kind: "card"; last4: string }
  | { kind: "transfer"; bank: string };
```

- Functions + modules over classes; classes where identity + lifecycle genuinely pair
  (connections, stateful services). No inheritance chains for code reuse — compose.
- Immutability by default: spread/`with()`/`toSorted()` over in-place mutation; `Map`/`Set`
  over object-as-dictionary when keys are dynamic.

## Boundaries & validation

Parse, don't trust: external data (HTTP, storage, env, URL params) crosses in through a
validator (zod-class) or hand-written type guard that produces a **typed** value; `JSON.parse`
returns are `unknown`, never `as MyType` (`types.md`, `pitfalls.md`). Internals then never
re-check.

## Constants & configuration

`const` object + derived union instead of `enum`:

```ts
const Plan = { solo: "solo", growth: "growth" } as const;
type Plan = (typeof Plan)[keyof typeof Plan];
```

Environment access is centralized in one typed config module — no `process.env.X` scattered
through the codebase.

## React-flavored notes (when the project is React)

Components are pure w.r.t. props; server data lives in the data layer (query library), not in
`useState`; derive state during render instead of syncing with effects; `useEffect` is for
synchronizing with external systems only. Follow the repo's UI conventions doc for the rest.
