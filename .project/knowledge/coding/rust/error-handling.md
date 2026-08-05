# Error Handling Reference

Error messages: lowercase, no trailing punctuation, no "error:" prefix (the caller adds context).

## The split that decides everything

| You are writing | Error type | Crate |
|---|---|---|
| a library (callers must match on failures) | dedicated enum per fallible area | `thiserror` |
| a binary / app edge (failures are reported, not matched) | one opaque error with context | `anyhow` (or `Box<dyn Error>`) |

Never expose `anyhow::Error` from a library API; never hand-write `Display`/`Error` impls that
`thiserror` derives for you.

## Library pattern (thiserror)

```rust
#[derive(Debug, thiserror::Error)]
pub enum StoreError {
    #[error("order {0} not found")]
    NotFound(OrderId),
    #[error("storage unavailable")]
    Unavailable(#[from] sqlx::Error),   // #[from] gives you `?` conversion
    #[error("invalid state: {reason}")]
    InvalidState { reason: String },
}
```

- One error enum per module/area, not per function and not one giant crate-wide enum.
- `#[from]` for wrap-and-propagate; `#[source]` when you wrap manually but keep the chain.
- Variants carry what the caller needs to *act* — IDs, limits — not prose.

## Application pattern (anyhow)

```rust
use anyhow::{Context, Result};

fn load() -> Result<Config> {
    let raw = fs::read_to_string(&path)
        .with_context(|| format!("reading config {}", path.display()))?;
    toml::from_str(&raw).context("parsing config")
}
```

`with_context` (lazy) on every `?` that crosses a meaningful boundary — the resulting chain
reads like a stack trace. Match on specifics with `err.downcast_ref::<StoreError>()` when an
app must branch on a library error.

## Rules

- `?` is the propagation tool; `match` on errors only where you actually handle them.
- No `unwrap()`/`expect()` on fallible paths in production code. `expect("invariant: …")` is
  allowed only where failure is a bug, and the message states the invariant, not "failed".
- In tests, `unwrap`/`expect` are fine; prefer `fn test_x() -> anyhow::Result<()>` + `?` for
  readable failures.
- Don't stringify errors mid-chain (`format!("{e}")` then wrap) — you destroy `source()`
  chains and downcasting. Keep the typed chain; render only at the edge.
- `panic!`/`assert!` are for broken invariants (bugs), never for expected failures (bad input,
  I/O). A library that panics on bad input is itself the bug.
- Fallible iterator chains: `collect::<Result<Vec<_>, _>>()` fails fast; use
  `partition_result`-style handling only when partial success is a real requirement.

## main() and exit

```rust
fn main() -> anyhow::Result<()> { run() }   // Debug-prints the chain, exits nonzero
```

For CLIs that need custom rendering/exit codes, catch at the top: `if let Err(e) = run()`,
print `e:#` (alternate = full chain), choose the code.
