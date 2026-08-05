# Testing Reference

## Where tests live

| Kind | Location | Sees |
|---|---|---|
| Unit | `#[cfg(test)] mod tests` in the same file | private items |
| Integration | `tests/*.rs` | public API only |
| Doc tests | ` ``` ` blocks in doc comments | public API; double as examples |

Doc tests are not optional decoration on a library — every public item's example compiles and
runs in CI, which keeps docs honest.

## Table-driven tests

```rust
#[test]
fn parses_amounts() {
    let cases = [
        ("1.00", Ok(100)),
        ("0", Ok(0)),
        ("-1", Err(ParseError::Negative)),
        ("abc", Err(ParseError::NotANumber)),
    ];
    for (input, expected) in cases {
        assert_eq!(parse_cents(input), expected, "input: {input}");
    }
}
```

Always attach the case to the assertion message — a failing table test must say *which row*.

## Conventions

- Test names state the behavior: `expired_trial_resumes_as_trialing`, not `test_resume_2`.
- `unwrap`/`expect` are fine in tests; better: `fn t() -> anyhow::Result<()>` + `?` so failures
  print the error chain.
- Assert on values and errors precisely: `assert_eq!` over `assert!(x == y)` (better failure
  output); match error *variants*, not error strings.
- `#[should_panic(expected = "...")]` only for actual panic contracts; expected failures are
  `Result`s and asserted as values.
- Each test builds its own state — no shared mutable fixtures, no ordering dependencies; tests
  run in parallel by default and must stay parallel-safe (unique temp dirs via `tempfile`, no
  fixed ports, no `env::set_var` without a serialization guard).
- Async: `#[tokio::test]`; fake time with `time::pause()`/`advance()` — a `sleep` used as
  synchronization is a flake.

## Test doubles

Prefer designing seams as traits and writing small hand-rolled fakes over mocking frameworks —
a 15-line in-memory `struct FakeStore(Mutex<HashMap<..>>)` implementing `Storage` beats a mock
DSL for readability. Conditional compilation for test-only helpers: `#[cfg(test)]` impl blocks.

## Property & fuzz testing

- `proptest` for invariants over generated inputs (round-trips, ordering laws, "never panics"):

```rust
proptest! {
    #[test]
    fn roundtrip(x in any::<u64>()) {
        prop_assert_eq!(decode(&encode(x))?, x);
    }
}
```

- `cargo-fuzz` for parser/deserializer attack surfaces. Both find what tables can't; keep the
  regression cases they discover as plain `#[test]`s.

## Coverage & CI

`cargo test` runs all three kinds. Coverage via `cargo llvm-cov`. The suite that gates "done"
also includes `cargo fmt --check` and `cargo clippy -- -D warnings` — a warning-free build is
part of passing.
