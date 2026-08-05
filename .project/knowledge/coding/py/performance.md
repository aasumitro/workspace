# Performance Reference

Measure first: `cProfile` + `snakeviz` (or `py-spy` for live/production processes — sampling,
no code change), `timeit` for micro-questions, `tracemalloc` for memory. A perf change without
a before/after number is a style change.

## Where Python time actually goes

Attribute lookups, function-call overhead, and allocation in hot loops dominate long before
algorithmic exotica. But **algorithm beats micro-optimization**: fix the O(n²) `in list` before
caching attribute lookups.

| Hot-loop pattern | Faster form |
|---|---|
| `x in big_list` repeatedly | make it a `set`/`dict` once |
| string `+=` in a loop | `"".join(parts)` |
| appending via `for` | list comprehension / generator |
| `df`-style row loops over dicts | restructure to columnar/bulk ops (or use the right library) |
| repeated `obj.attr.method` in a loop | hoist to a local (`m = obj.attr.method`) |
| building a list just to iterate | keep it a generator |

## Data structures

- `dict`/`set` for membership/lookup; `collections.deque` for queue semantics (list `pop(0)` is
  O(n)); `heapq` for top-k; `Counter`/`defaultdict` for tallying.
- `@dataclass(slots=True)` (or `__slots__`) for many-instance classes — smaller, faster
  attribute access.
- `array`, `memoryview`, `bytes` for bulk numeric/binary; NumPy/pandas when the work is truly
  vectorizable (crossing into NumPy per-element is *slower*).

## Caching

`functools.lru_cache(maxsize=...)`/`functools.cache` for pure, hot, repeat-argument functions —
mind unbounded growth and that arguments must be hashable; `cached_property` for
compute-once-per-instance. Invalidation still has to be a story, not a hope.

## Interpreter-level options (3.13+/3.14)

- **JIT builds** (experimental since 3.13): free speedup on some workloads — benchmark, don't
  assume.
- **Free-threaded builds** (supported in 3.14): real parallelism for CPU-bound *threaded* code —
  but single-thread performance has some overhead vs the GIL build; it's a parallelism tool,
  not a universal "faster Python".
- `concurrent.interpreters` / `ProcessPoolExecutor` for parallel CPU work on standard builds
  (`concurrency.md`).

## I/O & serialization

Batch round trips (DB, HTTP, disk) — latency, not CPU, is the usual villain. Stream instead of
slurping (iterate files, chunked reads). Pick serialization by measurement: `orjson`-class
libraries when JSON encode/decode profiles hot; stdlib `json` otherwise. Compression: stdlib
`compression.zstd` (3.14) beats gzip on speed-per-ratio for most payloads.

## What not to do

No C extension/Cython/Rust module before profiling proves the hot spot and the pure-Python
options (algorithm, data structure, batching, caching) are exhausted. No premature `__slots__`
everywhere, no `sys.intern` folklore, no micro-optimizing cold paths — readability pays rent
daily; speed only where measured.
