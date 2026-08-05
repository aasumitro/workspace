# Testing Reference

Vitest is the assumed runner (Jest-compatible API — everything here maps 1:1). Tests are
TypeScript: typed, linted, and strict like production code.

## Layout & naming

Colocated `thing.test.ts` next to `thing.ts` (or mirrored `tests/`, per repo — one convention,
not both). `describe` per unit/behavior cluster; test names state behavior:
`it("resumes an in-trial cancellation back to trialing")`, not `it("works")`.

## Structure

```ts
it("rejects an extension past the 2-year cap", () => {
  const sub = makeSubscription({ createdAt: daysAgo(700) });   // arrange (factory)
  const result = extend(sub, { months: 3 });                    // act
  expect(result).toEqual({ ok: false, error: expect.any(CapExceeded) });  // assert
});
```

- Factories with overrides (`makeSubscription(overrides?)`) over shared fixture blobs — each
  test states only what it cares about.
- One behavior per test; assert on values with `toEqual`/`toMatchObject`, on errors with
  `toThrow(SpecificError)` / rejects: `await expect(p).rejects.toBeInstanceOf(GatewayError)`.
- Parametrize with `it.each` — and give rows identifiable names:

```ts
it.each([
  ["1.00", 100],
  ["0", 0],
])("parses %s to %i cents", (raw, cents) => { ... });
```

## Async & time

- Tests `await` everything they start — a floating promise in a test is a pass that lies.
- Fake timers for time logic: `vi.useFakeTimers()` + `vi.advanceTimersByTimeAsync(...)`;
  restore in `afterEach`. A real `setTimeout` wait in a test is a flake with a fuse.
- Test cancellation paths: abort the signal, assert the abort behavior — cancellation is logic,
  not noise.

## Mocking discipline

- Ladder: real implementation → hand-rolled fake behind the interface seam → `vi.mock` last.
- `vi.mock` at module granularity hides coupling — prefer injecting the dependency and passing
  a fake. When you must module-mock, keep the mock *typed*
  (`vi.mocked(gateway.charge).mockResolvedValue(...)`) so signature drift fails.
- Never mock what you own and can construct (pure logic, value objects); never assert
  mock-call choreography when an observable outcome exists.
- Network: mock at the HTTP boundary (msw-class interceptors) rather than stubbing your own
  client — tests then survive client refactors.

## Type-level tests

Public type APIs deserve assertions too: `expectTypeOf<CreateInput>().toMatchTypeOf<...>()`
(vitest) or `// @ts-expect-error` for must-not-compile cases — a `@ts-expect-error` that stops
erroring fails the build, which is the point. Use it with a trailing reason comment.

## Snapshots

Inline snapshots (`toMatchInlineSnapshot`) for small serializable outputs only; a 200-line
snapshot nobody reads is not a test, it's a change-detector. Never snapshot objects with
volatile fields (dates, ids) without normalizing.

## Coverage & discipline

Regression test per bug fix (fails without the fix) · coverage is a risk map, not a KPI ·
tests parallel-safe: no shared module state without reset (`vi.restoreAllMocks` in
`afterEach`), unique temp resources, no fixed ports · e2e (Playwright-class) reserved for the
few critical journeys — the pyramid stays unit-heavy.
