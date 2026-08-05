# Rust Pitfalls

## The `.clone()` reflex

Cloning to silence the borrow checker compounds: today's `clone` becomes tomorrow's
"why is this slow" and hides the real ownership question. Restructure first
(`ownership-and-borrowing.md`); clone deliberately, not reflexively.

## `unwrap()` in production paths

Every `unwrap()` is a panic with no message at 3am. Grep-audit before shipping:
fallible → `?`; invariant → `expect("invariant: why this cannot fail")`.

## Holding a lock across `.await`

```rust
let guard = state.lock().unwrap();
do_io().await;               // deadlock/starvation: lock held while parked
```
Scope the guard (`{ let g = ...; g.value }`) before awaiting, or use `tokio::sync::Mutex`
knowingly. The compiler only catches this when the future must be `Send`.

## Silent cancellation

Any `.await` may never return — the future can be dropped there (select loser, timeout,
task abort). Code *after* an await is not guaranteed to run; cleanup belongs in `Drop` guards.
A `select!` arm losing the race cancels its future mid-flight — only select over
cancellation-safe operations.

## Blocking the async runtime

`std::thread::sleep`, sync file/network I/O, or a long CPU loop inside `async fn` stalls the
whole worker thread. `tokio::time::sleep`, async I/O, `spawn_blocking`.

## Integer overflow: debug panics, release wraps

Arithmetic overflow panics in debug and silently wraps in release. Money/counters: use
`checked_add`/`saturating_sub`/`wrapping_*` to make the policy explicit — the default is a
behavior *difference* between your tests and production.

## `as` casts truncate silently

`u64 as u32` chops bits without complaint. Narrowing: `u32::try_from(x)?`. Reserve `as` for
provably-lossless or intentionally-truncating casts (commented).

## Shadowing + unused `Result`

`let _ = fallible();` swallows errors invisibly; `#[must_use]` warnings exist — don't discard
them. Rebinding (`let x = ...; let x = ...;`) is idiomatic but re-check you didn't shadow the
value you meant to update inside a loop.

## `RefCell` panics at runtime

`borrow()`/`borrow_mut()` conflicts move borrow errors from compile time to a runtime panic —
usually via reentrancy (a callback re-entering the borrowing scope). If a `RefCell` needs
comments explaining why it won't double-borrow, restructure.

## `Rc`/`Arc` cycles leak

Parent↔child with strong refs both ways never drops. Back-edges are `Weak`.

## Iterator invalidation, Rust flavor

You can't mutate a collection while iterating it (compile error) — the trap is the workaround:
collecting indices then mutating by index can still shift/reorder. Prefer `retain`, `drain`,
`extract_if`, or build-new-collection.

## Trait impl surprises

- `Deref` abuse for inheritance-like method forwarding confuses resolution — implement real
  methods or traits.
- Implementing `PartialOrd` inconsistently with `Ord`/`PartialEq` breaks sort/map invariants —
  derive all four together or none.
- A manual `Hash` that disagrees with `Eq` corrupts `HashMap`s silently.

## Feature-flag drift

`cfg(feature = ...)` code that CI never compiles rots. CI matrix must include
`--no-default-features` and `--all-features` builds for libraries.

## Edition-2024 specifics

- `impl Trait` returns now capture all in-scope lifetimes by default — over-borrowing
  regressions after migration; fix with precise capturing `+ use<...>`.
- `unsafe_op_in_unsafe_fn`: an `unsafe fn` body no longer grants blanket unsafety — each unsafe
  op needs its own block (this is the point: per-op SAFETY reasoning).
