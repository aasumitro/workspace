# Patterns Reference

## Naming Conventions

- **Types/traits/enums/variants**: `UpperCamelCase`. **Functions/methods/variables/modules**:
  `snake_case`. **Constants/statics**: `SCREAMING_SNAKE_CASE`. **Lifetimes**: short, lowercase
  (`'a`, `'de`, `'src`).
- Acronyms follow case rules: `HttpClient`, `parse_url`, `next_id` — not `HTTPClient`/`parseURL`.
- Conversions: `as_` (cheap borrow), `to_` (expensive/owned), `into_` (consuming). Constructors:
  `new`, or `with_*`/`from_*` for variants. Getters without `get_` (`name()`, not `get_name()`);
  `get(...)` is for keyed/indexed lookup returning `Option`.
- Predicates read as questions: `is_empty`, `has_remaining`, `contains`.

## Module & crate layout

- One concept per module; `mod.rs`-free style (`foo.rs` + `foo/` subdir).
- Re-export the public API at the crate root (`pub use`) — consumers import from one place;
  deep paths are an implementation detail.
- Keep `lib.rs`/`main.rs` thin: wiring and re-exports, not logic. Binaries that grow logic
  should push it into the library crate so it's testable.
- Visibility is a design tool: default private; `pub(crate)` before `pub`. Every `pub` item is
  API you must keep stable.

## API design

- **Accept generously, return concretely**: parameters as `&str`, `&[T]`, `impl AsRef<Path>`,
  `impl IntoIterator`; return owned concrete types (or `impl Trait` for iterators/futures).
- Builders for 3+ optional parameters; `Default` + struct update syntax
  (`Config { retries: 5, ..Default::default() }`) for simple cases.
- Newtypes over primitive obsession: `struct OrderId(Uuid);` — the compiler enforces what a
  comment only suggests. Implement `Display`/`FromStr` as needed.
- Make invalid states unrepresentable: prefer an enum over a struct of `Option`s whose validity
  rules live in comments.

```rust
// Bad: caller must know only one may be Some
struct Payment { card: Option<Card>, transfer: Option<Transfer> }
// Good:
enum Payment { Card(Card), Transfer(Transfer) }
```

- Derive liberally and in canonical order:
  `#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]` — every public type gets
  `Debug`; `Copy` only for small, semantically-copyable values.

## Trait objects vs generics

Generics (`impl Trait` / `<T: Trait>`) for hot paths and when monomorphization is fine;
`Box<dyn Trait>` when you need heterogeneous collections, smaller binaries, or object-safe
plugin seams. Don't make a trait `dyn`-compatible at the cost of its ergonomics unless a real
`dyn` use exists.

## Exhaustiveness as a feature

`match` without a catch-all arm wherever practical — adding an enum variant should *break the
build* at every site that must handle it. Use `#[non_exhaustive]` on public enums/structs you
expect to grow, knowing it forces downstream `_` arms (trade deliberately).

## Interior mutability & shared state

Escalate only as far as needed: `&mut` → `Cell`/`RefCell` (single-thread) →
`Mutex`/`RwLock` (shared across threads) → `Arc<Mutex<T>>` (shared + owned). An
`Arc<Mutex<HashMap>>` as the first design is a smell — consider message passing or ownership
restructure first.
