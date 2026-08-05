# Error Handling Reference

## The ground truth: `catch` gives you `unknown`

With `useUnknownInCatchVariables` (part of strict), every catch is untyped — narrow before use:

```ts
try {
  await pay(invoice);
} catch (err) {
  if (err instanceof GatewayError) return retryLater(err);
  throw err;                                    // not yours? propagate.
}
```

Never `catch (err: any)`; never assume `err.message` exists — non-`Error` values get thrown by
real libraries.

## Designing thrown errors

- Always throw `Error` subclasses, never strings/objects.
- One base per domain (`class BillingError extends Error`), specific subclasses for what
  callers *branch on* (`InvoiceNotFound`, `QuotaExceeded`) — with typed fields, and `cause` for
  chaining:

```ts
class QuotaExceeded extends BillingError {
  constructor(readonly metric: string, readonly limit: number, options?: ErrorOptions) {
    super(`quota exceeded: ${metric}`, options);
    this.name = "QuotaExceeded";
  }
}
throw new QuotaExceeded("storage", limit, { cause: err });   // keep the chain
```

- Branch on `instanceof`/`name`/`code` fields — never on message strings.

## Throw vs Result: pick lanes deliberately

- **Throw** for the unexpected: I/O failures, violated invariants, programmer errors. This is
  the JS-native channel; don't fight it.
- **Result-style returns** for *expected, domain-meaningful* outcomes the caller must always
  handle (validation, parsing):

```ts
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
```

  A discriminated union forces handling at compile time — exceptions don't (TS has no checked
  exceptions; nothing in a signature says "this throws").
- Don't mix lanes for the same operation, and don't Result-ify everything — wrapping every
  possible failure produces `unwrap()` culture with extra steps.

## Async failures

- A rejected promise is a throw in async clothing — same typing rules, same narrowing.
- **No floating promises**: every promise is `await`ed, `return`ed, or explicitly
  `void somePromise` with a comment; unhandled rejections crash Node by default. Lint-enforce
  (`no-floating-promises`, `no-misused-promises`).
- Fan-out: `Promise.allSettled` when partial failure is expected (then *inspect* the results —
  an ignored `allSettled` is silent failure); `Promise.all` when any failure fails the batch;
  `AggregateError` (from `Promise.any` or thrown yourself) for plural failures.
- Async cleanup: `try/finally` or `await using` — cleanup must run on the rejection path too.

## Boundaries

Translate at layer edges, chain preserved via `cause`: driver error → storage error → domain
error → (outermost only) HTTP status / process exit / user message. Internals never format user
messages; edges never branch on driver errors. Top-level safety nets
(`process.on("unhandledRejection")`, framework error boundaries/middleware) are for logging and
crash hygiene — not a substitute for handling.

## Validation errors

Boundary validators (zod-class) produce structured issues — map them to your domain's
validation error type at the boundary; don't let library-specific error shapes flow inward.
