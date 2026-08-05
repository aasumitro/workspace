# Error Handling Reference

Exceptions are the error channel. No error codes, no `None`-meaning-failure, no
`(ok, err)` tuples.

## Designing your exceptions

- One base per package: `class BillingError(Exception)` — callers can catch the whole domain.
- Specific subclasses for what callers *act on differently*: `InvoiceNotFound(BillingError)`,
  `QuotaExceeded(BillingError)`. If no caller branches on it, don't mint a class.
- Carry data, not prose: `QuotaExceeded(metric="storage", limit=x, current=y)` with fields —
  messages are for humans, fields are for handlers.
- Never raise bare `Exception`; never raise strings-in-`ValueError` where a domain error fits.

## Raising

```python
raise InvoiceNotFound(invoice_id) from err        # keep the causal chain
raise TimeoutError("gateway") from None           # deliberately hide internals (rare, comment why)
```

- `raise ... from err` whenever translating exceptions at a boundary — an unchained translate
  destroys the actual cause.
- `exc.add_note(f"while processing org {org_id}")` (3.11+) to attach context while a caught
  exception propagates — cheaper than wrap-and-rethrow.
- Guard clauses raise early; happy path stays unindented.

## Catching

- Catch **specific** exceptions at the level that can **act** (retry, fallback, translate,
  report). A handler that can only log-and-reraise shouldn't exist — let it propagate.
- Never bare `except:` (it eats `KeyboardInterrupt`/`SystemExit`); `except Exception` only at
  true top-level boundaries (request handler, worker loop, `main`) — always logged with
  `log.exception(...)` (captures the traceback), never `print(e)`.
- No silent `except ...: pass`. If ignoring truly is the behavior:
  `with contextlib.suppress(FileNotFoundError):` — greppable and scoped.
- 3.14 forms: `except ValueError, TypeError:` (no `as`) is legal; keep the parenthesized tuple
  form in code that must run on older versions.
- `try` bodies minimal — wrap the one statement that can fail, not the whole function; zero-cost
  exceptions (3.11+) mean `try` beats pre-checking (EAFP over LBYL: `try: d[k]` over
  `if k in d: d[k]`).

## Exception groups (3.11+)

Concurrent code fails plurally. `TaskGroup` raises `ExceptionGroup`; handle with `except*`
(each clause sees a filtered subgroup, others keep propagating):

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(sync_invoices())
        tg.create_task(sync_usage())
except* GatewayError as eg:
    for e in eg.exceptions: schedule_retry(e)
```

Raise your own `ExceptionGroup("batch import", errors)` when an operation legitimately produces
multiple independent failures (batch/validation).

## Cleanup

Resource lifetimes → context managers (`with`), not `try/finally` chains; multiple resources →
one parenthesized `with` or `contextlib.ExitStack`. `finally` is for cleanup only — it can no
longer `return`/`break`/`continue` (3.14, PEP 765), which used to silently swallow exceptions.

## The boundary pattern

Translate at layer boundaries, chain preserved: DB driver errors → your storage errors → your
domain errors. Internals raise domain exceptions; only the outermost edge (HTTP handler, CLI
`main`) converts to status codes/exit codes/user messages.
