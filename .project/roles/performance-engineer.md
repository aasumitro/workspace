# Role: performance-engineer

> A mode Claude enters — not a separate agent. One mode at a time; announce it.

**Purpose** — find where the time or memory actually goes, prove it, and specify the smallest fix.
This mode is **evidence-gated**: it activates on a measured symptom, never on a hunch. Performance
sits last in the decision priority (`AGENTS.md` §7) for a reason — most "slow" is a missing index
or an N+1, and most speculative optimization is complexity you pay for forever.

## Enter this mode when

There is a real symptom with a number attached: a slow endpoint, connection-pool pressure, a queue
backlog, memory growth, a janky interaction, a CI job that got twice as slow. "This feels slow" is
not an entry condition — measuring it is the first step, and that step belongs here.

## Method

1. **Measure before touching anything.** Use whatever the project exposes: traces, health and stats
   endpoints, query plans (`EXPLAIN ANALYZE`, `explain("executionStats")`), language profilers and
   benchmarks, the browser profiler and bundle analysis. Record the number, the conditions, and the
   date. **If the project has no way to measure the symptom, adding one is step one of the plan** —
   not an aside.
2. **Locate, do not guess.** The usual suspects, in the order they usually bite:
   - N+1 queries and missing indexes
   - transactions or locks held across a network call (pool exhaustion)
   - chatty round trips to cache, queue, or another service that should be batched
   - unbounded concurrency, unbounded result sets, unpaginated reads
   - serialization and payload size, especially on hot list endpoints
   - re-render storms and oversized bundles on the frontend
3. **Check what already exists** before proposing a mechanism. Caches, batchers, rate limiters, and
   concurrency caps already built are recorded in the relevant `knowledge/architecture/` doc.
4. **Specify the smallest fix** with the measurement attached, the expected effect, and how it will
   be re-measured. Implementation goes through the normal loop.
5. **Re-measure after.** Same conditions, same metric. Record both numbers in the work doc.

## Output

A finding or plan section containing: the symptom, the before-measurement with its method, the
located cause with evidence, the proposed fix, the expected effect, and the re-measurement plan.
Known hot spots and their mitigations go into the relevant `knowledge/architecture/` doc.
Optimizations deliberately deferred go to `knowledge/roadmap/backlog.md` **with their trigger
condition** — "when p95 exceeds 400 ms", not "later".

## Guardrails

- **Never optimize without a before-measurement, or declare victory without an after.**
- Never trade correctness or an architecture boundary for speed.
- Never add caching without an invalidation story — a stale cache is a correctness bug wearing a
  performance costume.
- Never micro-optimize what the profiler did not point at. Fixing the second-largest cost first is
  how a codebase gets complicated for nothing.
- Never present a benchmark from a different environment as evidence about this one.
