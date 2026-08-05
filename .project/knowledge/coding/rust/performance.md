# Performance Reference

Measure first. `cargo bench` (criterion), `perf`/flamegraphs (`cargo flamegraph`), heap
profiling (`dhat`). A perf change without a before/after number is a style change.

## Build configuration (free wins first)

```toml
[profile.release]
lto = "thin"          # or "fat" for max, slower builds
codegen-units = 1     # better optimization, slower builds
panic = "abort"       # smaller/faster if unwinding isn't needed
```

Debug builds are 10-100x slower — never benchmark or "it feels slow" a debug binary.

## Allocation discipline

- Reuse buffers in loops: `String::clear()`/`Vec::clear()` + refill beats fresh allocation.
- Pre-size when the count is known: `Vec::with_capacity`, `String::with_capacity`,
  `HashMap::with_capacity`.
- `&str`/`&[T]` parameters instead of `String`/`Vec<T>` — don't force callers to allocate.
- `Cow<'_, str>` for sometimes-owned returns; `Arc<str>`/`Arc<[T]>` for shared immutable data
  (cheaper clones than `String`/`Vec`).
- Audit `.clone()` in hot paths — each one is a candidate restructure. `collect()` mid-chain is
  an allocation; stay in iterator land until the end.

## Iterators

Iterator chains compile to the same code as hand loops (often better — no bounds checks). Write
the clear chain; don't "optimize" into index loops. `filter_map` over `filter().map()`;
`fold`/`sum` over manual accumulation; `chunks_exact` when the tail is separate.

## Data layout

- Order struct fields largest-first only if profiling shows padding pain (the compiler reorders
  by default anyway unless `#[repr(C)]`).
- `Box` large enum variants so the enum isn't sized by its fattest member:
  `Rare(Box<HugePayload>)`.
- SoA (struct of arrays) over AoS for hot numeric scans; `smallvec` for
  almost-always-tiny vectors — only with profile evidence.

## Copies you don't see

- `#[derive(Copy)]` on big types makes every move a memcpy — keep `Copy` for ≤ 2 words.
- `[u8; N]` arrays move by copy; large lookup tables want `static`.
- Bounds checks: usually elided; in proven-hot loops prefer iterator forms (elide naturally)
  before reaching for `get_unchecked` (unsafe, last resort, with a `// SAFETY:`).

## Parallelism

`rayon` (`par_iter`) for embarrassingly-parallel CPU work — measure: below ~100µs of work per
item, thread overhead wins. Async is a *latency/concurrency* tool, not a throughput tool — see
`concurrency-and-async.md`.

## What not to do

No `unsafe` for speed without a benchmark proving the safe version is the bottleneck. No
`mem::transmute` where `as`/`from_bits` works. No lock-free hand-rolling when a `Mutex` isn't
even contended (measure contention first: it's usually not).
