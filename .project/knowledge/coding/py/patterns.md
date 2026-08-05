# Patterns Reference

## Naming Conventions

- `snake_case` functions/variables/modules; `PascalCase` classes; `SCREAMING_SNAKE_CASE`
  constants; `_leading_underscore` for internal; never `camelCase`.
- Modules: short, lowercase, no underscores if avoidable (`billing`, not `billing_utils` —
  and never a `utils.py` dumping ground; name the concern).
- Predicates read as questions: `is_expired`, `has_stock`, `can_refund`.
- No `get_` prefix for cheap attribute-like access — use `@property` or a plain name.

## Module & package layout

- `src/` layout for packages (`src/pkg/...`) — prevents accidentally importing the working
  copy. `pyproject.toml` is the single metadata/config home (deps, ruff, mypy, pytest).
- `__init__.py` re-exports the public API (`__all__`); deep module paths are implementation
  detail. Keep `__init__.py` logic-free (imports only) — import-time side effects are bugs
  waiting.
- Executable entry: `def main() -> int:` + `if __name__ == "__main__": sys.exit(main())`.

## Data modeling

- `@dataclass(slots=True, frozen=True)` is the default record — frozen unless mutation is the
  point; `kw_only=True` once fields exceed ~3:

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class Invoice:
    id: InvoiceId
    total_cents: int
    currency: str = "USD"
```

- Enums for closed sets (`class Status(StrEnum)`), never string constants scattered.
- `NamedTuple` for tiny immutable pairs crossing function boundaries; `TypedDict` for typing
  *external* JSON-ish payloads at the edges; pydantic-class validation only at real boundaries
  (API/DB), not for internal structures.
- Parse, don't validate: convert external input into typed structures once at the boundary;
  internals accept typed values and never re-check.

## API design

- Keyword-only arguments (`*,`) for booleans and anything with 3+ params —
  `send(email, *, retry=True)` reads; `send(email, True)` doesn't.
- Accept broad, return precise: parameters typed as `Iterable`/`Sequence`/`Mapping`, returns as
  `list`/`dict`/concrete dataclasses.
- Context managers for anything with a lifetime (`contextlib.contextmanager` for the simple
  ones); generators for streams instead of building lists.
- Composition + small functions over inheritance; ABC/`Protocol` seams only where multiple
  implementations exist (Protocols preferred — structural, no inheritance coupling; see
  `typing.md`).
- Exceptions are the error channel — don't return `None`-meaning-failure alongside
  `None`-meaning-absent (`error-handling.md`).

## Import discipline

Absolute imports; module-level only (function-level imports only to break a proven cycle or
defer a heavy optional dep — comment which). Import order: stdlib / third-party / local —
ruff enforces. Never `from x import *`.

## Logging

`logging.getLogger(__name__)` per module; lazy formatting (`log.info("id=%s", id)` — not
f-strings in log calls, they evaluate even when filtered); no `print` outside CLIs' actual
output. Libraries never call `basicConfig()` — configuration belongs to the application.
