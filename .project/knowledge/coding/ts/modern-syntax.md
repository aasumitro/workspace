# Modern TypeScript Syntax Reference

Use features up to the project's `typescript` version. Never use features from newer versions.
**Stop reading at your project's version boundary.**

## TS 4.9+

- `satisfies` — check a value against a type **without widening** it:

```ts
const config = {
  port: 8000,
  env: "dev",
} satisfies Config;      // config.env stays "dev", not string
```

- `in` narrowing for unlisted properties.

## TS 5.0+

- Standard (stage-3) decorators — class members only, no `experimentalDecorators` needed.
- `const` type parameters — infer literal types without `as const` at call sites:

```ts
function route<const T extends string>(path: T): Route<T> { ... }
route("/users/:id")   // T = "/users/:id", not string
```

- `export type *`; multiple files in `extends` (tsconfig).

## TS 5.2+

- `using` / `await using` — explicit resource management (Symbol.dispose):

```ts
await using conn = await pool.acquire();   // disposed at scope exit, even on throw
```

## TS 5.4+ – 5.9

- Preserved narrowing in closures after last assignment (5.4); `NoInfer<T>` (5.4).
- `Object.groupBy`/`Map.groupBy` types (5.4); Iterator helper types (`.map`, `.filter`,
  `.take` on iterators, matching the JS proposal) (5.6).
- Inferred type predicates — `const evens = xs.filter(x => x != null)` narrows without a
  hand-written guard (5.5).
- Checked import attributes (`with { type: "json" }`); `require(esm)` interop era —
  `module: "nodenext"` handles it (5.8+).
- Growing strictness around unreachable/unused narrowing paths — treat new errors after an
  upgrade as found bugs, not noise.

## TS 6.x — the bridge line

TS 6 is the last JS-implemented compiler line, deliberately aligned with 7's behavior:
- Deprecated/legacy options removed or hard-errored (old `target`s, `namespace`-era patterns,
  AMD/UMD-era module modes) — a clean TS 6 config is the compatibility gate for 7.
- Language features continue landing here first; codebase-visible behavior matches 7 by design.
- Treat every TS 6 deprecation warning as a migration task, not a suppression target
  (`tooling-and-migration.md`).

## TS 7.x — the native compiler

Same language, new engine (native Go port; ~10x faster builds/editor responsiveness):
- Config surface is the cleaned-up TS 6 set; projects that build warning-free on 6 move with
  little or no change.
- Toolchain integration changes (`tsgo`-based CLI/LSP) — build scripts and editor plugins are
  what migrate, not your source.
- API-based tooling (custom transformers, compiler-API scripts) is the main breakage surface —
  audit anything importing `typescript` programmatically.

## Idiom upgrades (any modern version)

| Old | New |
|---|---|
| `as SomeType` to shape a literal | `satisfies SomeType` (keeps inference honest) |
| `as const` at every call site | `const` type parameters in the API |
| `enum Color { ... }` | union of literals (`"red" \| "blue"`) or `const` object + `keyof` |
| `namespace` | ES modules |
| hand-rolled `isX` guards for null-filters | inferred type predicates (5.5+) |
| try/finally resource cleanup | `using` / `await using` |
| `import { type X, y }` mixed by habit | `import type { X }` — explicit type-only imports |
| `require`/CJS in new code | ESM (`module: "nodenext"`, `"type": "module"`) |
