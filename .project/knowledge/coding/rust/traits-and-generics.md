# Traits & Generics Reference

## When to abstract

Introduce a trait when there are (or will demonstrably be) **two+ real implementations**, or you
need a seam for testing/plugins. A trait with one impl and no test double is ceremony — use the
concrete type.

## Generics vs trait objects

| | `<T: Trait>` / `impl Trait` | `Box<dyn Trait>` / `&dyn Trait` |
|---|---|---|
| Dispatch | static (monomorphized) | dynamic (vtable) |
| Cost | zero runtime; bigger binary, slower compile | one indirection; smaller binary |
| Collections | homogeneous only | heterogeneous fine |
| Use for | hot paths, combinators, most library APIs | plugin registries, mixed collections, cutting compile times at seams |

`impl Trait` in argument position is sugar for a generic; in return position it's an opaque
type — the standard way to return iterators/futures/closures.

## Designing traits

- Small and focused — one capability per trait (`Storage`, not `StorageAndCacheAndMetrics`);
  compose with supertraits or extra bounds at use sites.
- Put required methods only; ship ergonomics as provided methods with default bodies.
- Take `&self`/`&mut self` in the least-restrictive form that works; a trait that takes
  `self` by value is rarely `dyn`-usable.
- **`dyn` compatibility (object safety)** is a design decision: generic methods, `Self` returns,
  and `where Self: Sized` bounds break it. Decide early whether the trait must support `dyn` —
  retrofitting hurts.
- Async: native `async fn` in traits works for generic use; for `dyn` + `Send` bounds you still
  want the `#[async_trait]`-style boxing or an explicit `-> Pin<Box<dyn Future>>` method.

## Constraints

- Prefer `where` clauses once bounds exceed one trait; bound only what the body uses.
- `T: Into<X>` at edges for caller ergonomics; convert once at the top, use `X` internally.
- Blanket impls (`impl<T: Foo> Bar for T`) are powerful and permanent — coherence means you
  can't add overlapping impls later; write them only for genuinely universal relationships.

## Standard traits to implement (in rough priority)

`Debug` (always, every public type) · `Clone` · `PartialEq`/`Eq` (test assertions need them) ·
`Default` · `Hash` (map keys) · `Display` (user-facing types) · `From`/`TryFrom` for
conversions (never a bespoke `to_x()` when `From` fits — `From` gives you `Into` and `?`
conversions free) · `Serialize`/`Deserialize` behind a `serde` feature flag in libraries ·
`Iterator`/`IntoIterator` for anything collection-like (get every adapter free) ·
`AsRef`/`Borrow` for cheap-view relationships.

## Generic code rules

- Don't over-generalize: a function used with one type is not generic; generics are for logic
  identical across types.
- `PhantomData<T>` to carry type/lifetime relationships in newtypes and typed IDs
  (`struct Id<T>(u64, PhantomData<T>)` — `Id<User>` ≠ `Id<Order>` at compile time).
- Sealed traits (a private supertrait) when downstream impls would break your invariants:

```rust
mod sealed { pub trait Sealed {} }
pub trait Backend: sealed::Sealed { /* ... */ }
```

- Const generics (`struct Matrix<const N: usize>`) for sizes that are genuinely compile-time;
  don't force them where a runtime `usize` field reads better.
