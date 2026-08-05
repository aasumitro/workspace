# TypeScript Pitfalls

## Floating promises

```ts
sendReceipt(order);        // async, never awaited — failures vanish, ordering is luck
```
Await it, return it, or `void sendReceipt(order)  // fire-and-forget: <why>`. Lint-enforced
(`no-floating-promises`); the variant `items.forEach(async ...)` doesn't await anything —
`for...of` with await, or `Promise.all(items.map(...))`.

## `as` lies compound

`as MyType` on `JSON.parse`/`fetch` results types a hope. The value is `unknown` — validate at
the boundary (`types.md`). An `as` deep in the codebase is a bug with a delay fuse; `as any` is
disabling the compiler locally and silently.

## Enums

`enum` has surprising runtime/emit semantics (reverse mappings, const-enum inlining across
packages) and doesn't survive some compiler modes. Union literals or `as const` objects
(`patterns.md`) do everything you actually wanted.

## `||` for defaults

`value || fallback` replaces `0`, `""`, and `false`. Use `??` (nullish only) — and `??=` for
assignment.

## Truthiness on optional numbers/strings

`if (limit)` skips a legitimate `0`; `if (name)` skips `""`. Compare explicitly:
`if (limit !== undefined)`.

## Mutating shared references

`const` prevents rebinding, not mutation. Sorting props in place (`items.sort()`) mutates the
caller's array — use `toSorted`/`toReversed`/spread. Same for objects passed into functions:
treat inputs as `readonly` (and type them so).

## Index access optimism

`arr[i]` and `record[key]` are `T` by default even when absent — that's the hole
`noUncheckedIndexedAccess` closes. With it on, handle the `undefined`; without it, you're
one off-by-one from `cannot read properties of undefined`.

## Structural typing surprises

- Excess-property checks fire only on *fresh object literals* — a widened variable with extra
  props passes silently.
- Two IDs that are both `string` interchange freely — brand them (`types.md`).
- Empty interfaces/`{}` match nearly everything; `object`/`Record<string, unknown>` say what
  you mean.

## `this` capture

Method references lose `this`: `setTimeout(obj.tick, 1000)` calls with `this === undefined`.
Arrow-bind at the call (`() => obj.tick()`) or define as arrow property when the class hands
methods out.

## Async in constructors

`constructor` can't await; a promise-launching constructor creates half-initialized objects.
Static async factory: `static async create(...): Promise<Conn>`.

## Date, number, JSON

`Date` months are 0-based and `Date` is mutable — prefer the project's date library at edges.
`JSON.stringify` drops `undefined`/functions and throws on `BigInt`/cycles. Money: integer
minor units (cents), never floats — `0.1 + 0.2 !== 0.3` here too.

## Type-only imports that aren't

Without `verbatimModuleSyntax`, a "type" import that's actually a value (or vice versa) can
change emit and create phantom runtime cycles. Turn the flag on; write `import type`
explicitly.

## Barrel-file import cycles

`index.ts` re-export webs create cycles that surface as "undefined is not a function" at
module-init time (an import evaluated before its dependency). Deep barrels are also why "cmd-
click goes to a re-export, not code". Keep barrels shallow and boundary-only.

## Exhaustiveness that silently rots

A `switch` over a union without a `never` default keeps compiling when a variant is added —
and silently mishandles it. Always the `const _exhaustive: never` arm (`types.md`), plus the
`switch-exhaustiveness-check` lint.

## Test-only traps

`@ts-expect-error` without a reason comment; snapshots of volatile data; `vi.mock` hoisting
surprises (mock declared after import use). See `testing.md`.
