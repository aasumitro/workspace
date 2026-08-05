# Rust Guide — use when working with `.rs` files

> Current to **Rust 1.97, Edition 2024**. General-purpose reference + style guide —
> project-independent. Match features to the project's toolchain (`rust-version` in `Cargo.toml`
> / `rust-toolchain.toml`): use everything up to it, nothing past it (`modern-syntax.md` is
> version-gated).

## Files

| File | Read when |
|---|---|
| `modern-syntax.md` | Always at least once — version-gated feature reference through 1.97 / Edition 2024 |
| `patterns.md` | Naming, module layout, API design — the "how Rust code looks" doc |
| `ownership-and-borrowing.md` | Fighting the borrow checker; designing data ownership |
| `error-handling.md` | Any fallible path: `Result`, `?`, `thiserror`/`anyhow` split |
| `traits-and-generics.md` | Trait design, generics vs `dyn`, when to abstract |
| `concurrency-and-async.md` | Threads, channels, `Send`/`Sync`, async/await, tokio |
| `testing.md` | Unit/integration/doc tests, property tests |
| `performance.md` | Only with a measured symptom — allocation, clones, iterators |
| `pitfalls.md` | Reviewing or debugging — the classic traps (unwrap, deadlocks, `.clone()` reflex) |

## The five rules that outrank everything

1. `cargo fmt` and `cargo clippy -- -D warnings` are part of "done".
2. No `unwrap()`/`expect()` on fallible paths in production code — propagate with `?` or handle;
   `expect("why this cannot fail")` only for true invariants.
3. Libraries return typed errors (`thiserror`); binaries may use `anyhow` at the edges.
4. `unsafe` needs a `// SAFETY:` comment proving the invariant, and Edition 2024's
   `unsafe_op_in_unsafe_fn` means every unsafe operation is explicit — no silent unsafety.
5. Prefer borrowing to cloning; a `.clone()` added to silence the borrow checker is a design
   smell — restructure ownership first.
