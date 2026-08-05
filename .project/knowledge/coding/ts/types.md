# Types Reference

## The `any` / `unknown` policy

- `any` disables checking and **spreads** through everything it touches. Quarantine it at
  boundaries (untyped deps, migration seams), convert to `unknown` immediately, narrow to
  typed. Inside the codebase, `any` is a review blocker; `as any` doubly so.
- `unknown` is the honest "don't know yet" — unusable until narrowed, which is the point.

## Narrowing toolbox

`typeof` / `instanceof` / `in` / equality on discriminants / `Array.isArray` — structure code
so guards fall out naturally (early returns). Custom guards where reuse demands:

```ts
function isPaid(inv: Invoice): inv is PaidInvoice {
  return inv.status === "paid";
}
```

Inferred type predicates (TS 5.5+) cover the simple lambda cases — don't hand-write
`(x): x is T` for a null filter anymore.

## Discriminated unions + exhaustiveness

The core modeling tool. Always pair with an exhaustiveness check so adding a variant breaks
every switch that must handle it:

```ts
switch (event.kind) {
  case "created": ...
  case "paid": ...
  default: {
    const _exhaustive: never = event;   // compile error on a new variant
    throw new Error(`unhandled: ${JSON.stringify(event)}`);
  }
}
```

## Generics

- Generic only when the *relationship* between types matters (`T in → T out`); a type parameter
  used once is usually noise — take the concrete/wide type.
- Constrain meaningfully (`<T extends { id: string }>`); default sparingly
  (`<T = never>` traps); `NoInfer<T>` to pin inference sites; `const T` to keep literals.
- Prefer inference over explicit call-site type arguments — if callers must write `<Foo>`
  routinely, redesign.

## Object shapes: `interface` vs `type`

Either is fine; be consistent per repo (common default: `interface` for extendable object
shapes and public contracts, `type` for unions, intersections, mapped/conditional results).
Never use declaration merging as a design feature inside app code.

## Utility & mapped types

Know the built-ins before writing conditional types: `Pick`/`Omit`/`Partial`/`Required`/
`Readonly`/`Record`/`ReturnType`/`Parameters`/`Awaited`/`Extract`/`Exclude`/`NonNullable`.
Derive, don't duplicate:

```ts
type CreateOrderInput = Omit<Order, "id" | "createdAt">;
type OrderStatus = Order["status"];
```

Template literal types for pattern-shaped strings (`` type EventName = `${Domain}.${Action}` ``).
Hand-rolled recursive conditional types are a last resort — they're the code reviewers can't
read and the compiler pays for; if it takes a blog post to explain, simplify the design.

## Branded / nominal types

TS is structural; brand IDs that must not cross:

```ts
type OrderId = string & { readonly __brand: "OrderId" };
const OrderId = (s: string): OrderId => s as OrderId;   // one sanctioned cast, at the boundary
```

## `null` vs `undefined`

Pick one absence value per codebase (default: `undefined` internally; `null` where wire
formats demand it) and encode it in types. `?.` and `??` (never `||` for defaults — it eats
`0`/`""`/`false`).

## Assertions

`as` is a claim the compiler can't verify — every `as` (beyond `as const` and sanctioned
boundary casts) is a potential lie that will be "true" until 3am. The ladder: restructure →
narrow with a guard → `satisfies` → `as` with a comment justifying soundness.
