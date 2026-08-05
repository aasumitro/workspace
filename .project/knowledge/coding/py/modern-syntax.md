# Modern Python Syntax Reference

Use features up to the project's floor version (`requires-python`). Never use features from
newer versions. **Stop reading at your project's version boundary.**

## Python 3.10+

- Structural pattern matching:

```python
match event:
    case {"type": "paid", "amount": int(amount)} if amount > 0:
        settle(amount)
    case {"type": "refund"}:
        raise Unsupported("no refunds")
    case _:
        log.warning("unhandled: %r", event)
```

- Union syntax `int | None` not `Optional[int]`; `X | Y` not `Union[X, Y]`.
- Parenthesized context managers: `with (open(a) as f, open(b) as g):`.

## Python 3.11+

- `ExceptionGroup` + `except*` — concurrent failures stop being lossy.
- `asyncio.TaskGroup` (structured concurrency) and `asyncio.timeout()` — replace bare
  `gather`/`wait_for` (see `concurrency.md`).
- `tomllib` (stdlib TOML read). `typing.Self`, `LiteralString`, variadic generics
  (`TypeVarTuple`).
- Zero-cost `try` — exceptions are cheap when not raised; stop pre-checking what you could try.
- `datetime.UTC` alias; `add_note()` on exceptions for context accumulation.

## Python 3.12+

- **PEP 695 generics** — type parameters without `TypeVar` ceremony:

```python
def first[T](xs: Sequence[T]) -> T: ...
class Repo[M: Model]: ...
type Vector = list[float]          # `type` alias statement
```

- f-strings fully re-parsed (PEP 701): nesting, reuse of quotes, multiline expressions inside.
- `itertools.batched(iterable, n)`. `Path.walk()`. `@typing.override`.
- Per-interpreter GIL groundwork (C-API level).

## Python 3.13+

- **Free-threaded build (experimental)** — `python3.13t` runs without the GIL; and an
  experimental JIT. Both opt-in builds, not defaults.
- New interactive REPL (colors, multiline editing); dramatically better tracebacks.
- `typing.ReadOnly` for TypedDict items; `copy.replace()` for dataclass-like updates;
  `Path.from_uri()`.
- Removal wave ("dead batteries", PEP 594): `cgi`, `telnetlib`, etc. are gone — check imports
  when upgrading old code.

## Python 3.14+

- **Free-threading officially supported** (PEP 779) — no longer experimental; the
  no-GIL build is a production option. Thread-safety of *your* code is now the interesting
  constraint (see `concurrency.md`).
- **Template strings** (PEP 750): `t"Hello {name}"` produces a `Template` object — interpolation
  you can inspect/escape *before* rendering (SQL/HTML injection-safe formatting layers):

```python
tpl = t"select * from users where id = {user_id}"   # NOT a str — a Template
sql, params = compile_query(tpl)                     # library decides rendering
```

- **Deferred annotation evaluation** (PEP 649/749) — annotations evaluate lazily by default;
  `from __future__ import annotations` becomes unnecessary; use `annotationlib` for
  introspection. Forward references mostly "just work".
- **Multiple interpreters in stdlib** (PEP 734): `concurrent.interpreters` — isolated
  interpreters (own GIL each) as a concurrency option, plus
  `concurrent.futures.InterpreterPoolExecutor`.
- `compression.zstd` (PEP 784) — Zstandard in the stdlib.
- **Unparenthesized multi-exception `except`** (PEP 758): `except ValueError, TypeError:` is
  now valid — but only *without* an `as` clause; `except (ValueError, TypeError) as e:` still
  requires the parens. Mixed codebases: the parenthesized form works everywhere — prefer it.
- **`finally` may no longer `break`/`continue`/`return`** (PEP 765) — control flow that swallows
  in-flight exceptions from a `finally` block is rejected; it was always a bug pattern.
- Better error messages again (typo suggestions across more contexts).

## Idiom upgrades (any modern version)

| Old | New |
|---|---|
| `Optional[X]` / `Union[X, Y]` | `X \| None` / `X \| Y` |
| `TypeVar("T")` ceremony | PEP 695 `def f[T](...)` (3.12+) |
| `from __future__ import annotations` | default behavior (3.14+) |
| `os.path.*` string surgery | `pathlib.Path` |
| `%`-format / `.format()` | f-strings (t-strings when the consumer must control rendering) |
| `dict` "ordered" tricks | plain `dict` (insertion-ordered since 3.7) |
| `asyncio.get_event_loop()` | `asyncio.run()` at the top; `get_running_loop()` inside |
| manual `TypeVar` bounds in classes | `class C[T: Bound]` (3.12+) |
