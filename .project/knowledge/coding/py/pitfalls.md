# Python Pitfalls

## Mutable default arguments

```python
def add_item(item, items=[]):      # ONE list shared across all calls
```
Default: `items: list | None = None` then `items = items or []` (or `[] if None`). Same trap
with `{}` and dataclass fields (`field(default_factory=list)`).

## Late-binding closures

```python
callbacks = [lambda: print(i) for i in range(3)]   # all print 2
```
Bind at definition: `lambda i=i: print(i)` — or `functools.partial`.

## `is` vs `==`

`is` compares identity, `==` value. Small-int/string interning makes `is` *appear* to work in
tests and fail in production. `is` only for `None`/`True`/`False`/sentinels.

## Chained/shared references

`b = a` aliases; `a = [[0]] * 3` gives three references to one inner list. Copy explicitly
(`list(a)`, `copy.deepcopy`) — and know slicing copies shallowly.

## Modifying while iterating

`for k in d: d.pop(k)` → RuntimeError; lists silently skip. Iterate over a copy
(`list(d)`), build a new collection, or use comprehension-with-filter.

## Exception-handling traps

Bare `except:` eats `KeyboardInterrupt`/`SystemExit`. `except ...: pass` buries bugs.
Pre-3.14, `return`/`break` inside `finally` silently swallowed in-flight exceptions (3.14
rejects it — older codebases: audit). `except (A, B)` needs the tuple pre-3.14 —
`except A, B:` was a syntax error there, not "catch A as B".

## Import-time side effects & cycles

Module-level code runs on first import — connections/config reads at import time make imports
order-dependent and tests slow. Cycles usually mean a missing third module both should import;
a function-level import is a tourniquet, not a fix.

## Name shadowing

A file named `json.py`/`types.py`/`test.py` in the path shadows stdlib — the error appears in
*unrelated* imports. Also: rebinding builtins (`id`, `list`, `type`) as variable names.

## Float for money

`0.1 + 0.2 != 0.3`. Money is `int` cents or `decimal.Decimal` (from *strings*:
`Decimal("0.1")` — `Decimal(0.1)` imports the float error).

## Truthiness overreach

`if not items:` treats `None`, `[]`, `""`, and `0` identically. When absence ≠ empty ≠ zero,
compare explicitly (`if items is None:`). Timestamps/amounts of `0` are the classic casualty.

## Async-specific

- Forgetting `await` — the coroutine is created, never runs; only a warning tells you.
- Unreferenced `create_task` results can be garbage-collected mid-flight — hold them or use
  `TaskGroup`.
- `time.sleep`/sync I/O in a coroutine blocks the whole loop.
- Swallowing `CancelledError` breaks timeouts and shutdown — re-raise it.

## The GIL is not a correctness tool

Unsynchronized shared mutation was always racy in principle; on free-threaded 3.14 builds it's
racy in practice. Lock it, queue it, or don't share it.

## `functools.lru_cache` on methods

Caches on `self` → keeps every instance alive (leak) and shares nothing between them usefully.
Cache module-level functions, or use `cached_property` for per-instance compute-once.

## Star-import & mutation of `sys.path`

`from x import *` breaks tooling and shadow-audits; `sys.path.append(...)` in code is a
packaging problem wearing a runtime disguise — fix the packaging (`src/` layout, editable
install).
