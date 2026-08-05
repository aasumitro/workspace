# Modern Rust Syntax Reference

Use features up to the project's toolchain version. Never use features from newer versions.
**Stop reading at your project's version boundary.** Edition-gated items need
`edition = "2024"` in `Cargo.toml`, not just a new compiler.

## Rust 1.65+

- `let-else` for refutable bindings that diverge on failure:

```rust
let Some(user) = find_user(id) else {
    return Err(Error::NotFound);
};
```

- GATs (generic associated types) — lending iterators, associated types with lifetimes.

## Rust 1.70+

- `OnceCell` / `OnceLock` in std — replace `lazy_static!`/`once_cell` crate for simple cases:

```rust
static CONFIG: OnceLock<Config> = OnceLock::new();
fn config() -> &'static Config { CONFIG.get_or_init(Config::load) }
```

- `Option::is_some_and(|x| ...)` not `map_or(false, ...)`.

## Rust 1.75+

- `async fn` and `-> impl Trait` in traits (no `#[async_trait]` needed for many cases; still
  needed when you require `dyn` compatibility or `Send` bounds on the future).

## Rust 1.76–1.79

- C-string literals: `c"hello"` (1.77).
- Inline `const { ... }` blocks in expressions (1.79).
- Automatic temporary lifetime extension rules clarified — don't rely on extension in `match`
  scrutinees.

## Rust 1.80–1.82

- `LazyCell` / `LazyLock` stabilized (1.80) — the last `lazy_static!` use cases die:

```rust
static RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^\d+$").unwrap());
```

- Exclusive-range patterns `0..10` in `match` (1.80).
- `&raw const x` / `&raw mut x` — raw pointers without intermediate references (1.82); required
  form for taking pointers to unaligned/packed fields.
- `Option::inspect` / `Result::inspect` for side-effect peeks.

## Rust 1.85+ — Edition 2024 baseline

- **Edition 2024** (`edition = "2024"`): RPIT lifetime capture defaults changed (use
  `+ use<'a, T>` precise capturing to override) · `unsafe_op_in_unsafe_fn` is deny-by-default ·
  `unsafe extern` blocks · `unsafe` attributes (`#[unsafe(no_mangle)]`) · `gen` reserved ·
  never-type fallback changes.
- **Async closures** `async || { ... }` with `AsyncFn`/`AsyncFnMut`/`AsyncFnOnce` bounds —
  closures that borrow and return futures without `move` gymnastics.

## Rust 1.87–1.88

- **Let chains** (Edition 2024 only): `if let Some(a) = x && a.enabled && let Ok(b) = f(a)` —
  replaces nested `if let` pyramids.
- Anonymous pipes in std (`std::io::pipe`).

## Rust 1.89–1.97 (recent — verify availability in your toolchain)

- Continued stabilization wave; before using anything niche from this range, check
  `cargo +<toolchain> doc` or the release notes for the exact minor version — and prefer the
  long-stable form when a reviewer would have to look it up. When this guide and the compiler
  disagree, the compiler wins; note the correction here.

## Idiom upgrades (any recent toolchain)

| Old | New |
|---|---|
| `lazy_static!` / `once_cell::sync::Lazy` | `std::sync::LazyLock` |
| `#[async_trait]` everywhere | native `async fn` in traits (non-`dyn` cases) |
| `map_or(false, f)` | `is_some_and(f)` / `is_ok_and(f)` |
| nested `if let` | let chains (Edition 2024) |
| `match x { Some(v) => v, None => return ... }` | `let-else` |
| `mem::replace(&mut opt, None)` | `opt.take()` |
| manual pointer casts for packed fields | `&raw const` / `&raw mut` |
