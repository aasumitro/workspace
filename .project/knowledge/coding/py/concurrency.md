# Concurrency Reference

## Choose the model first

| Workload | Use |
|---|---|
| I/O-bound, many concurrent waits | `asyncio` |
| I/O-bound, few tasks / sync libraries | threads (`ThreadPoolExecutor`) |
| CPU-bound | processes (`ProcessPoolExecutor`) — or free-threaded threads / subinterpreters (3.13+/3.14, below) |
| Isolation without processes | `concurrent.interpreters` (3.14, PEP 734) |

## asyncio — structured concurrency (3.11+ style)

```python
async def refresh(org_ids: list[str]) -> None:
    async with asyncio.TaskGroup() as tg:          # all complete or all cancelled
        for oid in org_ids:
            tg.create_task(refresh_one(oid))
    # failures arrive as ExceptionGroup — handle with except*
```

- `asyncio.run(main())` once at the top; `get_running_loop()` inside; never
  `get_event_loop()`.
- `TaskGroup` over bare `gather` (first failure cancels siblings instead of leaking them);
  `async with asyncio.timeout(5):` over `wait_for` (composable, doesn't wrap your coroutine).
- **Fire-and-forget leaks**: `asyncio.create_task` results must be held (the loop keeps only a
  weak ref — an unreferenced task can be GC'd mid-flight) — keep a set, or use a TaskGroup.
- Never block the loop: no `time.sleep`, no sync I/O, no heavy CPU in a coroutine — use
  `await asyncio.sleep`, async clients, or `await asyncio.to_thread(sync_fn, ...)`.
- Cancellation is a real code path: any `await` can raise `CancelledError` — clean up via
  `finally`/context managers, re-raise it (don't swallow), and treat `shield()` as a rare,
  commented exception.
- Sync↔async bridges: `asyncio.to_thread` (sync from async) ·
  `asyncio.run_coroutine_threadsafe(coro, loop)` (async from another thread).

## Threads

- `ThreadPoolExecutor` + `executor.map`/`submit`, not hand-rolled `Thread` lifecycles.
- Share state via `queue.Queue` first; locks second (`threading.Lock`, held briefly, one
  acquisition order); `threading.Event` for signaling; `local()` for per-thread state.
- **Free-threaded Python (3.13 experimental → 3.14 supported, PEP 779)**: on `python3.14t`
  threads run truly parallel — CPU-bound threading becomes real. Consequences:
  - The GIL no longer masks your race conditions. "It worked because of the GIL" code
    (unsynchronized counters, dict mutation from two threads) is now genuinely racy — lock it
    or use atomics-by-design (queues, immutable data).
  - Check C-extension compatibility (packages declare free-threaded support) before flipping a
    workload to `t`-builds.
  - Same source runs on both builds: write thread-correct code unconditionally;
    `sys._is_gil_enabled()` exists for diagnostics, not for branching logic.
- `InterpreterPoolExecutor` / `concurrent.interpreters` (3.14): isolated interpreters, own
  state (and independent locking) each, message-passing via shareable objects — the middle
  ground when you want isolation stronger than threads without process/pickling overhead.

## Processes

`ProcessPoolExecutor` for CPU-bound batch work on the standard build. Arguments/results must
pickle; prefer chunky tasks (amortize IPC); guard the entrypoint
(`if __name__ == "__main__":`) — required on spawn-based platforms, and spawn is the default
everywhere now.

## Universal rules

- Every concurrent path has a bounded lifetime and an owner — no daemon-thread fire-and-forget,
  no orphan tasks; shutdown = stop intake → drain → join/await.
- Bound your queues and pools (an unbounded queue is a slow memory leak with a delay fuse).
- Timeouts on every external wait.
- A `sleep()` used as synchronization is a race with a delay — synchronize with
  events/queues/joins, in code and in tests alike.
