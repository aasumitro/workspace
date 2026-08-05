# Typing Reference

Policy: new code is typed from birth; public functions always annotated; internals may rely on
inference. The checker (mypy `--strict` or pyright strict) runs in CI — a type error is a build
error.

## Modern forms (floor 3.12+)

```python
def first[T](xs: Sequence[T]) -> T: ...              # PEP 695 — no TypeVar ceremony
class Cache[K, V]: ...
type JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
```

- Builtin generics (`list[int]`, `dict[str, X]`); `X | None` — `Optional`/`Union`/`List` are
  legacy spellings.
- 3.14+: annotations are lazily evaluated by default — forward references work without quotes
  or `from __future__ import annotations`; runtime introspection goes through `annotationlib`.

## Protocols over ABCs

Structural typing decouples the seam from implementations — the fake in tests doesn't inherit
anything:

```python
class Storage(Protocol):
    def put(self, key: str, data: bytes) -> None: ...
    def get(self, key: str) -> bytes | None: ...
```

`@runtime_checkable` only if you genuinely `isinstance` against it (method *presence* only).
Prefer Protocols for seams, ABCs only when you want shared concrete behavior in a base.

## Narrowing

The checker follows `isinstance`, `is None`, `match`, `assert`, and early returns — structure
code so narrowing is natural (guard clauses). For custom checks: `TypeGuard[T]` (narrows in the
positive branch) / `TypeIs[T]` (narrows both branches, 3.13+ via typing-extensions earlier).

```python
def is_active(sub: Subscription | None) -> TypeIs[Subscription]:
    return sub is not None and sub.status == "active"
```

## The escape-hatch ladder (weakest acceptable first)

1. Restructure so the type is provable.
2. `assert isinstance(...)` — runtime-checked narrowing.
3. `cast(T, x)` — unchecked, greppable; comment why it's sound.
4. `# type: ignore[specific-code]` — always with the error code, never bare.
5. `Any` — quarantine at the edges (deserialization, third-party gaps); an `Any` that flows
   inward disables checking silently. `object` + narrowing beats `Any` when feasible.

## Useful precision tools

- `Literal["monthly", "yearly"]` for closed string sets crossing boundaries (or a `StrEnum`).
- `NewType("UserId", str)` — zero-cost distinct IDs the checker enforces.
- `TypedDict` (+ `Required`/`NotRequired`/`ReadOnly`) for external JSON shapes.
- `@overload` when return type depends on argument types/literals — implementation signature
  stays permissive.
- `ParamSpec`/`Concatenate` for decorators that must preserve signatures:

```python
def logged[**P, R](f: Callable[P, R]) -> Callable[P, R]: ...
```

- `Self` for fluent APIs and alternate constructors; `@override` (3.12+) on every intentional
  override — catches rename drift.
- Variance is inferred with PEP 695 syntax — stop annotating `covariant=True` by hand.

## Don'ts

Don't annotate what inference already knows (`x: int = 0` is noise — but do annotate empty
collections: `items: list[Order] = []`). Don't type `self`/`cls`. Don't stringify annotations
by habit (3.14 laziness makes it moot). Don't design APIs that need `Any` to be callable —
that's an API smell, not a typing gap.
