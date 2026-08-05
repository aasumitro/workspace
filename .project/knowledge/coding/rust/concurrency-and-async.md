# Concurrency & Async Reference

## Choose the model first

| Workload | Use |
|---|---|
| CPU-bound parallelism | threads: `std::thread::scope`, or `rayon` for data parallelism |
| I/O-bound, many concurrent waits | async: `tokio` (the default runtime choice) |
| Mixed | async runtime + `spawn_blocking` for the CPU/blocking parts |

Async is not "faster threads" — it's cheaper *waiting*. Don't async a CPU-bound pipeline.

## Threads (sync)

- `thread::scope` for structured parallelism — borrows local data safely, joins automatically:

```rust
thread::scope(|s| {
    for chunk in data.chunks(1024) {
        s.spawn(|| process(chunk));
    }
});  // all joined here
```

- Channels: `std::sync::mpsc` for simple cases; `crossbeam-channel` for select/multi-consumer.
- `Send`/`Sync` are inferred — when the compiler says a type isn't `Send`, believe it and find
  the `Rc`/`RefCell`/raw pointer inside; don't `unsafe impl Send` your way past it.

## Shared state (sync)

- Escalation order: message passing → `Arc<T>` (immutable) → `Arc<Mutex<T>>`/`Arc<RwLock<T>>` →
  atomics (`AtomicUsize`, `AtomicBool`) for counters/flags only.
- Lock discipline: hold locks briefly; never call user/async code while holding one; one
  consistent acquisition order across the codebase kills most deadlocks.
- A poisoned `Mutex` (`lock().unwrap()` panic) means another thread panicked mid-critical
  section — deciding to propagate vs `into_inner()` is a per-call-site decision, not a habit.

## Async (tokio)

- Spawned tasks need `'static` + `Send`: move owned data in; share with `Arc`.
- **Never block the executor**: no `std::thread::sleep`, no sync I/O, no long CPU loops in
  async fns — use `tokio::time::sleep`, async I/O, `spawn_blocking`.
- **Hold no `std` Mutex across `.await`** (compile error if `Send` needed, deadlock risk
  otherwise). Short critical sections around `.await` points: `tokio::sync::Mutex`, or better,
  restructure so the lock never spans an await.
- Structured concurrency: `tokio::join!`/`try_join!` for a fixed set;
  `JoinSet` for dynamic fan-out (like Go's errgroup — first error, abort the rest):

```rust
let mut set = JoinSet::new();
for url in urls { set.spawn(fetch(url)); }
while let Some(res) = set.join_next().await { res??; }
```

- `select!` races futures — remember losers are **cancelled**; only select over
  cancellation-safe futures, or re-arm carefully.
- **Cancellation is silent**: any `.await` is a point where the future may be dropped. Cleanup
  belongs in `Drop` guards, not in code after the await. `CancellationToken`
  (tokio-util) for cooperative shutdown; graceful shutdown = stop intake → drain in-flight →
  then exit.
- Channels: `tokio::sync::mpsc` (bounded — pick a real capacity; unbounded is a memory-leak
  policy), `oneshot` for single replies, `watch` for latest-value broadcast, `broadcast` for
  fan-out with lag tolerance.
- Async closures (1.85+) and async fn in traits (1.75+) are native — see `modern-syntax.md`.

## Testing concurrent code

`#[tokio::test]` for async tests; `tokio::time::pause()` + `advance()` to test timeouts without
real sleeps. `loom` for exhaustive interleaving checks on hand-rolled sync primitives (rare).
Any test with a real `sleep` as synchronization is flaky by construction — use channels/notify.
