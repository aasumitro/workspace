# Python Guide — use when working with `.py` files

> Current to **Python 3.14**. General-purpose reference + style guide — project-independent.
> Match features to the project's floor version (`requires-python` in `pyproject.toml`): use
> everything up to it, nothing past it (`modern-syntax.md` is version-gated).

## Files

| File | Read when |
|---|---|
| `modern-syntax.md` | Always at least once — version-gated feature reference, 3.10 → 3.14 (pattern matching, PEP 695 generics, t-strings, free-threading) |
| `patterns.md` | Naming, module layout, dataclasses, API design — the "how Python code looks" doc |
| `typing.md` | Type hints: annotations policy, generics, protocols, narrowing |
| `error-handling.md` | Exceptions: hierarchy design, handling, exception groups |
| `concurrency.md` | asyncio, threads (incl. free-threaded 3.13+/3.14), processes, subinterpreters |
| `testing.md` | pytest conventions: fixtures, parametrize, mocking discipline |
| `performance.md` | Only with a measured symptom — profiling, data structures, hot loops |
| `pitfalls.md` | Reviewing or debugging — mutable defaults, late binding, import cycles… |

## The five rules that outrank everything

1. Format + lint with `ruff` (format, check --fix); type-check with a strict checker (mypy or
   pyright). All three clean = part of "done".
2. Public functions carry type hints; new code is typed from birth — `typing.md` binds.
3. Never a bare `except:`; never swallow exceptions silently — `error-handling.md` binds.
4. Dependencies and packaging live in `pyproject.toml`; environments are per-project
   (uv/venv) — never install into the system interpreter.
5. Scripts and tools are deterministic, idempotent, and fail loudly (`sys.exit(1)` with a
   message), never half-succeed silently.

> **Workspace tooling note:** when used inside an agent workspace, `.project/scripts/` stays
> **stdlib-only** (bare `python3`, no `pip install`) so every agent's environment can run them —
> the full guide set above applies to *product* Python code.
