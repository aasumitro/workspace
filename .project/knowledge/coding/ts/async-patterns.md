# Async Patterns Reference

## async/await discipline

- `async`/`await` everywhere; `.then()` chains only where a bare expression genuinely reads
  better (rare). Never mix the two styles in one flow.
- Sequential awaits are a latency decision — independent work runs concurrently:

```ts
// serial: 300ms + 300ms
const user = await getUser(id);
const plans = await getPlans();
// concurrent: max(300, 300)
const [user2, plans2] = await Promise.all([getUser(id), getPlans()]);
```

- `return await` inside try/catch (so the rejection is caught here); plain `return promise`
  outside one.
- An `async` function that never awaits is either sync (drop `async`) or a bug (missing await).

## Fan-out and bounded concurrency

Unbounded `Promise.all(items.map(fetchOne))` against a real service is a self-DoS. Bound it —
a tiny pool/chunk pattern or the project's utility:

```ts
for (const batch of chunks(items, 10)) {
  results.push(...await Promise.all(batch.map(fetchOne)));
}
```

`allSettled` + result inspection when partial failure is the contract (`error-handling.md`).

## Cancellation: AbortController is the standard

Pass `AbortSignal` through every async API you design; forward it to fetch/timers/streams:

```ts
async function search(q: string, { signal }: { signal?: AbortSignal } = {}) {
  const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`, { signal });
  ...
}
```

- Compose: `AbortSignal.timeout(5000)` for deadlines, `AbortSignal.any([...])` to merge
  user-cancel + timeout.
- On abort you get an `AbortError`-flavored rejection — treat cancellation as a normal exit
  path, not an error to log as failure.
- UI flavor: cancel the stale request when inputs change (effect cleanup / query library) —
  out-of-order responses overwriting fresh state is the classic race.

## Timers, retries, backoff

- Sleep: `await new Promise(r => setTimeout(r, ms))` — with a signal hook if it must be
  cancellable (or `setTimeout` from `node:timers/promises` in Node).
- Retry with exponential backoff + jitter, a max-attempts cap, and only for retryable errors
  (network/5xx/429 — not validation). Respect the abort signal *between* attempts.
- Every external wait gets a timeout; "hangs forever" is the default you must opt out of.

## Streams & incremental data

- Async iteration is the portable consumption pattern: `for await (const chunk of stream)`.
- Async generators for producing incremental sequences (pagination, tailing):

```ts
async function* pages(url: string) {
  let next: string | undefined = url;
  while (next) {
    const page = await fetchPage(next);
    yield* page.items;
    next = page.nextCursor;
  }
}
```

- Backpressure: don't buffer an entire stream into memory to "simplify" — process as you
  iterate, or use the platform's stream pipeline utilities.

## Resource lifetimes

`await using` (TS 5.2+) for anything with a close/release — connections, locks, temp files —
cleanup runs on every exit path including throws. Pre-`using` codebases: `try/finally` with the
acquire *outside* the try only if acquisition failure needs different handling.

## Ordering traps

See `pitfalls.md`: floating promises, `forEach(async ...)` (doesn't await — use `for...of` or
`Promise.all(map)`), async work inside constructors (factories instead), listeners added after
the event could fire.
