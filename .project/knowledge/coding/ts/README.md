# TypeScript Guide — use when working with `.ts` / `.tsx` files

> Current to **TypeScript 6 / 7** (6.x = final JS-based compiler line; 7.x = the native
> Go-port compiler, ~10x faster, same language). General-purpose reference + style guide —
> project-independent. Match features to the project's `typescript` version in `package.json`;
> `tooling-and-migration.md` covers the 5.x → 6 → 7 path.

## Files

| File | Read when |
|---|---|
| `modern-syntax.md` | Always at least once — version-gated feature reference, 4.9 → 6/7 |
| `patterns.md` | Naming, module layout, API design — the "how TS code looks" doc |
| `types.md` | Type-level design: unions, narrowing, generics, `unknown`/`any` policy |
| `error-handling.md` | Errors: throwing, Result-style, async failures |
| `async-patterns.md` | Promises, async/await, cancellation, streams |
| `testing.md` | Vitest/Jest conventions, typing tests, mocking discipline |
| `tooling-and-migration.md` | tsconfig baseline, strictness flags, TS 6 → 7 migration |
| `pitfalls.md` | Reviewing or debugging — the classic traps (enums, `as`, floating promises…) |

## The five rules that outrank everything

1. `strict: true` is the floor, not the goal — plus the hardening flags in
   `tooling-and-migration.md`. A type error is a build error.
2. `any` is quarantined at boundaries; inside, it's `unknown` + narrowing — `types.md` binds.
3. No floating promises: every promise is awaited, returned, or explicitly `void`-ed with a
   reason (lint-enforced).
4. Type-only imports are explicit (`import type`), and runtime/type boundaries stay visible
   (`verbatimModuleSyntax`).
5. The formatter (prettier/biome) and linter are part of "done" — style debates are settled by
   tools, not reviews.
